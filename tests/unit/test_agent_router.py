import unittest
from app.agents.router import normalize_route


class AgentRouterTests(unittest.TestCase):
    def test_supported_route_is_preserved(self):
        self.assertEqual(normalize_route("SCRAPE"), "SCRAPE")

    def test_route_in_model_sentence_is_detected(self):
        self.assertEqual(normalize_route("Decision: FILE"), "FILE")

    def test_unknown_route_falls_back_to_direct(self):
        self.assertEqual(normalize_route("not sure"), "DIRECT")


if __name__ == "__main__":
    unittest.main()
