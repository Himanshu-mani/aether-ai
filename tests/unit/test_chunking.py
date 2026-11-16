import unittest
from langchain_core.documents import Document
from app.rag.chunking import split_documents


class ChunkingTests(unittest.TestCase):
    def test_chunking_preserves_source_metadata(self):
        document = Document(page_content="AetherAI " * 300, metadata={"source": "sample.txt"})
        chunks = split_documents([document])
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.metadata["source"] == "sample.txt" for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
