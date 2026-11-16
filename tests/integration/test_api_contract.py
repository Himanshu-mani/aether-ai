import unittest
from app.main import app


class ApiContractTests(unittest.TestCase):
    def test_existing_api_routes_are_registered(self):
        paths = {route.path for route in app.routes}
        self.assertIn("/api/chat", paths)
        self.assertIn("/api/upload", paths)


if __name__ == "__main__":
    unittest.main()
