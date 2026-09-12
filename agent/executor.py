import asyncio
import re
import datetime
from core.llm_setup import get_llm
from core.rag_pipeline import query_documents
from tools.live_web_rag import live_web_scrape_tool
from langchain_core.messages import HumanMessage, SystemMessage

class ProfessionalAgentExecutor:
    def __init__(self, llm):
        self.llm = llm
        
        # Updated Router for the new Architecture
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
6. You run on both online and offline mode. Your core engine uses local Ollama with the Gemma 2 2B (2 billion parameters) model. Answer clearly when asked about your configuration.
7. If context from an internet webpage or an uploaded file is provided, use it to accurately answer the question. Say "Based on the provided context" if using it."""

    async def generate_response(self, query: str) -> str:
        # Route logic
        print(f"\n[🧠 AI CHATBOT ROUTING...] '{query}'")
        route_decision = await self.llm.ainvoke(self.router_prompt.format(query=query))
        decision_text = route_decision.content.strip().upper()
        print(f"[*] Route Decision: {decision_text}")
        
        search_context = ""
        
        # Action execution based on route
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
                import json
                cleaned = gen_result.content.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].strip()
                data = json.loads(cleaned)
                
                from tools.universal_file_ops import create_downloadable_file
                # execute the langchin tool string correctly
                file_status = create_downloadable_file.invoke({
                    "filename": data.get("filename", "output.txt"), 
                    "content": data.get("content", "Empty")
                })
                return f"{data.get('reply', 'Here is your file.')}\n\n*(System: {file_status})*"
            except Exception as e:
                print(f"[!] Generate File parsing error: {e}")
                return "I encountered an error generating the file. Please try again."

        elif "SCRAPE" in decision_text:
            print("[*] Retrieving live webpage data...")
            # Detect URLs
            urls = re.findall(r'(https?://\S+)', query)
            if urls:
                target_url = urls[0]
            else:
                import urllib.parse
                safe_query = urllib.parse.quote_plus(query)
                target_url = f"https://lite.duckduckgo.com/lite/?q={safe_query}"
            
            # Asynchronous tool invocation
            search_context = await live_web_scrape_tool.ainvoke({"url": target_url})
            print("[*] Webpage Scrape finished.")
            
        elif "FILE" in decision_text:
            print("[*] Retrieving data from uploaded files (ChromaDB)...")
            search_context = await asyncio.to_thread(query_documents, query)
            print("[*] File search finished.")
            
        # Context building
        current_time_str = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        dynamic_sys = self.system_prompt + f"\n\n[SYSTEM CLOCK: Current date and time is {current_time_str}. User's timezone applies.]"
        messages = [SystemMessage(content=dynamic_sys)]
        
        if search_context and ("FILE" in decision_text or "SCRAPE" in decision_text):
            augmented_prompt = f"Contextual Data:\n{search_context}\n\nUser Query: {query}"
            messages.append(HumanMessage(content=augmented_prompt))
        else:
            messages.append(HumanMessage(content=query))
            
        print("[*] Generating final answer (Gemma 2)...\n")
        
        try:
            final_msg = await self.llm.ainvoke(messages)
            return final_msg.content
        except Exception as e:
            print(f"[!] Evaluation Error: {e}")
            return "There was an error generating my response. Please try again."

def create_agent():
    llm = get_llm()
    return ProfessionalAgentExecutor(llm), llm
