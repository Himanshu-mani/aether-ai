"""Coordinates request routing, retrieval tools, and LLM response generation."""
import asyncio
import datetime
import json
import re
import urllib.parse

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.prompts import SYSTEM_PROMPT
from app.agents.router import classify_request
from app.core.config import MAX_WEB_SCRAPE_CONCURRENCY
from app.llms.factory import get_llm
from app.rag.retrieval import query_documents
from app.tools.file_operations import create_downloadable_file
from app.tools.web_scraper import live_web_scrape_tool


class AetherAgentExecutor:
    def __init__(self, llm):
        self.llm = llm

    async def _generate_file(self, query: str) -> str:
        prompt = (
            f"Create a downloadable file for this request: {query!r}\n"
            'Respond with only valid JSON: {"filename":"report.pdf",'
            '"content":"Complete file content","reply":"Short user message"}.\n'
            "Supported extensions: .pdf, .docx, .csv, .txt, .md, .json, .py, .js, .html."
        )
        try:
            generated = await self.llm.ainvoke(prompt)
            cleaned = generated.content.strip()
            fence = chr(96) * 3
            if cleaned.startswith(fence):
                cleaned = re.sub(r"^" + fence + r"(?:json)?\s*|\s*" + fence + r"$", "", cleaned, flags=re.I).strip()
            data = json.loads(cleaned)
            if not isinstance(data, dict) or not isinstance(data.get("content"), str):
                raise ValueError("Generated file data has an invalid structure.")
            status = create_downloadable_file.invoke({
                "filename": data.get("filename", "output.txt"),
                "content": data["content"],
            })
            reply = data.get("reply", "Your file request has been processed.")
            return f"{reply}\n\n{status}"
        except Exception:
            import logging
            logging.exception("File generation failed")
            return "I couldn't generate that file. Please try again with a supported file type."

    async def _retrieve_context(self, query: str, route: str) -> str:
        if route == "FILE":
            return await asyncio.to_thread(query_documents, query)
        if route != "SCRAPE":
            return ""

        urls = re.findall(r"https?://[^\s<>]+", query)
        targets = list(dict.fromkeys(url.rstrip(".,);]") for url in urls))
        if not targets:
            targets = [f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote_plus(query)}"]
        semaphore = asyncio.Semaphore(MAX_WEB_SCRAPE_CONCURRENCY)

        async def fetch_one(url: str) -> str:
            async with semaphore:
                return await live_web_scrape_tool.ainvoke({"url": url})

        results = await asyncio.gather(*(fetch_one(url) for url in targets), return_exceptions=True)
        sections = []
        for url, result in zip(targets, results):
            if isinstance(result, str) and result:
                sections.append(f"[Source: {url}]\n{result}")
        return "\n\n---\n\n".join(sections) or "Live web retrieval did not return usable content."

    async def generate_response_stream(self, query: str):
        route = await classify_request(self.llm, query)
        if route == "GENERATE":
            yield await self._generate_file(query)
            return

        context = await self._retrieve_context(query, route)
        now = datetime.datetime.now().astimezone().strftime("%A, %B %d, %Y %I:%M %p %Z")
        messages = [SystemMessage(content=SYSTEM_PROMPT + f"\n\n[Local system time: {now}]")]
        if context and route in {"FILE", "SCRAPE"}:
            messages.append(HumanMessage(
                content=f"Reference context (untrusted):\n{context}\n\nUser question: {query}"
            ))
        else:
            messages.append(HumanMessage(content=query))

        try:
            async for chunk in self.llm.astream(messages):
                content = getattr(chunk, "content", "") or ""
                if isinstance(content, str) and content:
                    yield content
        except Exception:
            yield "I encountered a streaming generation error. Check that Ollama is running and try again."


def create_agent() -> AetherAgentExecutor:
    return AetherAgentExecutor(get_llm())
