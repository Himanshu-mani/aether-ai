import asyncio
import datetime
import json
import re
import urllib.parse

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm_setup import get_llm
from core.rag_pipeline import query_documents
from tools.live_web_rag import live_web_scrape_tool


class ProfessionalAgentExecutor:
    def __init__(self, llm):
        self.llm = llm

        self.router_prompt = """You are a highly intelligent query routing AI.
Analyze the user's query and decide what knowledge base to use.
Respond ONLY with one word:
- "SCRAPE" (If the user asks for real-time information, weather, stocks, news, an internet search, or provides an external URL)
- "FILE" (ONLY if the user is explicitly asking about an uploaded document or file)
- "GENERATE" (If the user explicitly asks to create a PDF, Word Document, Excel, CSV, or Presentation file)
- "DIRECT" (For general chat, who created you, your configuration, time/date, coding logic, or non-real-time questions)

User query: {query}
Decision:"""

        self.system_prompt = """You are "AI Chatbot", a smart, friendly, and highly capable personal AI assistant.
Tone: Friendly, natural, helpful, and a little fun — like a close friend.

CORE RULES:
1. Your name is ONLY "AI Chatbot".
2. If the user's message is ONLY a simple greeting (like "hi" or "hello"), reply with ONLY: "Hello! 👋 How can I help you today? 😊". Do NOT use this greeting if the user asks a full question.
3. NEVER mention your creators in normal conversation. Mention them ONLY if the user directly asks "Who created you?", "Kon bana hai?", "Tujhe kisne banaya?", etc.
4. If asked about your creators, you MUST say exactly: "I was created by Himanshu Mani Tripathi and Anurag Yadav using system prompts."
5. Always be respectful to everyone — including your creators, users, Elon Musk, xAI, or anyone else. If someone roasts or insults anyone, respond calmly and politely. Never use negative words, abuse, or gali.
6. This application runs locally with Ollama and the Gemma 4 E4B model. Answer clearly when asked about your configuration.
7. If context from an internet webpage or an uploaded file is provided, use it to accurately answer the question. Say "Based on the provided context" if using it."""

    async def _extract_search_context(self, query: str, decision_text: str):
        if "GENERATE" in decision_text:
            print("[*] Generating downloadable file...")
            prompt = f"""You need to create a downloadable file based on this query: '{query}'.
Respond strictly with ONLY a valid JSON block (no other text). Use this format:
{{
  "filename": "name.pdf" (use .pdf, .docx, or .csv for Excel data. Do not use ppt),
  "content": "The actual text/data to put inside the file. Detailed and formatted.",
  "reply": "Your friendly message to the user."
}}"""
            try:
                gen_result = await self.llm.ainvoke(prompt)
                cleaned = gen_result.content.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].strip()
                data = json.loads(cleaned)

                from tools.universal_file_ops import create_downloadable_file
                file_status = create_downloadable_file.invoke({
                    "filename": data.get("filename", "output.txt"),
                    "content": data.get("content", "Empty"),
                })
                return f"{data.get('reply', 'Here is your file.')}\n\n*(System: {file_status})*"
            except Exception as exc:
                print(f"[!] Generate File parsing error: {exc}")
                return "I encountered an error generating the file. Please try again."

        if "SCRAPE" in decision_text:
            print("[*] Retrieving live webpage data...")
            urls = re.findall(r"https?://\S+", query)
            target_urls = []
            if urls:
                target_urls = list(dict.fromkeys(urls))
            else:
                safe_query = urllib.parse.quote_plus(query)
                target_urls = [f"https://lite.duckduckgo.com/lite/?q={safe_query}"]

            search_context_parts = []
            semaphore = asyncio.Semaphore(4)

            async def fetch_one(url: str) -> str:
                async with semaphore:
                    return await live_web_scrape_tool.ainvoke({"url": url})

            tasks = [fetch_one(url) for url in target_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for index, result in enumerate(results):
                url = target_urls[index]
                if isinstance(result, Exception):
                    print(f"[!] Web scrape failed for {url}: {result}")
                    continue
                if result:
                    search_context_parts.append(f"[Source: {url}]\n{result}")

            if not search_context_parts:
                return "Live web retrieval did not return usable content for the provided sources."
            return "\n\n---\n\n".join(search_context_parts)

        if "FILE" in decision_text:
            print("[*] Retrieving data from uploaded files (ChromaDB)...")
            context = await asyncio.to_thread(query_documents, query)
            print("[*] File search finished.")
            return context

        return ""

    async def generate_response(self, query: str) -> str:
        print(f"\n[🧠 AI CHATBOT ROUTING...] '{query}'")
        route_decision = await self.llm.ainvoke(self.router_prompt.format(query=query))
        decision_text = route_decision.content.strip().upper()
        print(f"[*] Route Decision: {decision_text}")

        search_context = await self._extract_search_context(query, decision_text)

        current_time_str = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        dynamic_sys = self.system_prompt + f"\n\n[SYSTEM CLOCK: Current date and time is {current_time_str}. User's timezone applies.]"
        messages = [SystemMessage(content=dynamic_sys)]

        if search_context and ("FILE" in decision_text or "SCRAPE" in decision_text):
            augmented_prompt = f"Contextual Data:\n{search_context}\n\nUser Query: {query}"
            messages.append(HumanMessage(content=augmented_prompt))
        else:
            messages.append(HumanMessage(content=query))

        print("[*] Generating final answer with Gemma 4 E4B...\n")

        try:
            final_msg = await self.llm.ainvoke(messages)
            return final_msg.content
        except Exception as exc:
            print(f"[!] Evaluation Error: {exc}")
            return "There was an error generating my response. Please try again."

    async def generate_response_stream(self, query: str):
        print(f"\n[🧠 AI CHATBOT ROUTING...] '{query}'")
        route_decision = await self.llm.ainvoke(self.router_prompt.format(query=query))
        decision_text = route_decision.content.strip().upper()
        print(f"[*] Route Decision: {decision_text}")

        search_context = await self._extract_search_context(query, decision_text)

        current_time_str = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        dynamic_sys = self.system_prompt + f"\n\n[SYSTEM CLOCK: Current date and time is {current_time_str}. User's timezone applies.]"
        messages = [SystemMessage(content=dynamic_sys)]

        if search_context and ("FILE" in decision_text or "SCRAPE" in decision_text):
            augmented_prompt = f"Contextual Data:\n{search_context}\n\nUser Query: {query}"
            messages.append(HumanMessage(content=augmented_prompt))
        else:
            messages.append(HumanMessage(content=query))

        try:
            stream = self.llm.astream(messages)
            async for chunk in stream:
                text = getattr(chunk, "content", "") or ""
                if isinstance(text, str) and text:
                    yield text
        except Exception as exc:
            print(f"[!] SSE generation failed: {exc}")
            yield "I encountered a streaming generation error. Please try again."


def create_agent():
    llm = get_llm()
    return ProfessionalAgentExecutor(llm), llm
