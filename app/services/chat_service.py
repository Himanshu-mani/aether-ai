"""Chat use case, independent of HTTP transport."""
import asyncio
import json
import logging
from app.agents.executor import create_agent


async def stream_chat_response(message: str):
    try:
        agent = create_agent()
        async for chunk in agent.generate_response_stream(message):
            payload = {"type": "chunk", "content": chunk}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)
        yield 'data: {"type":"done"}\n\n'
    except asyncio.CancelledError:
        raise
    except Exception:
        logging.exception("Chat stream failed")
        payload = {
            "type": "error",
            "message": "I could not process this request. Check that Ollama is running and try again.",
        }
        yield f"data: {json.dumps(payload)}\n\n"
