import unittest

from core.resource_manager import infer_local_inference_profile


class ResourceProfileTests(unittest.TestCase):
    def test_low_ram_uses_conservative_context(self):
        profile = infer_local_inference_profile({
            "system_ram_mb": 8192, "available_ram_mb": 3000,
            "gpu_available": False, "free_vram_mb": None,
        })
        self.assertTrue(profile["low_memory_mode"])
        self.assertEqual(profile["recommended_num_ctx"], 4096)
        self.assertEqual(profile["web_scrape_concurrency"], 1)

    def test_high_ram_uses_default_context(self):
        profile = infer_local_inference_profile({
            "system_ram_mb": 32768, "available_ram_mb": 20000,
            "gpu_available": False, "free_vram_mb": None,
        })
        self.assertFalse(profile["low_memory_mode"])
        self.assertEqual(profile["recommended_num_ctx"], 8192)

    def test_low_vram_uses_conservative_context(self):
        profile = infer_local_inference_profile({
            "system_ram_mb": 32768, "available_ram_mb": 20000,
            "gpu_available": True, "free_vram_mb": 800,
        })
        self.assertTrue(profile["low_memory_mode"])
        self.assertEqual(profile["recommended_num_ctx"], 4096)


if __name__ == "__main__":
    unittest.main()
