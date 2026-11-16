# AetherAI Architecture

AetherAI uses a modular-monolith architecture: one FastAPI application with clear internal boundaries. Modules are separated by responsibility without introducing network hops or unnecessary infrastructure.

## Request flow

1. The browser sends chat requests to \`POST /api/chat\` and uploads to \`POST /api/upload\`.
2. API route handlers validate HTTP input and delegate work to services.
3. The chat service streams output from the agent executor as Server-Sent Events.
4. The agent router selects direct chat, document RAG, live web retrieval, or file generation.
5. The LLM factory provides the configured Ollama chat and embedding clients.

## Retrieval and tool boundaries

- **Document RAG** (\`app/rag/\`): loads uploaded files, splits text, indexes chunks, and retrieves relevant chunks from ChromaDB.
- **Live Web** (\`app/tools/web_scraper.py\`): retrieves public web-page content when current information is requested.
- **File Operations** (\`app/tools/file_operations.py\`): searches indexed user files through the RAG retrieval interface and creates downloadable outputs.

RAG and Live Web are distinct retrieval sources. File Operations is a separate tool boundary that can call RAG retrieval when searching uploaded files.

## Design constraints

- Keep existing API paths and SSE event names stable for the frontend.
- Keep the workspace and ChromaDB persistence path stable.
- Keep model names, prompts, chunk size/overlap, and supported formats stable unless a separate feature change is approved.
- Use absolute imports rooted at \`app.*\`; root \`main.py\` remains a compatibility entry point.
- Add databases, queues, or microservices only when a measured requirement justifies them.

## Security considerations

Uploads and retrieved content are untrusted. The web scraper performs basic URL/IP validation, but browser redirects and DNS changes can still create SSRF risk. Do not expose web retrieval to untrusted users until network egress controls and redirect validation are added. The application currently has no authentication layer and should remain local or behind trusted access controls.
