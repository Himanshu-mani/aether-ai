"""Best-effort, cross-platform local resource detection."""

import platform
import shutil
import subprocess
from typing import Dict, Optional


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _read_meminfo() -> Dict[str, Optional[float]]:
    """Return Linux /proc memory values in KiB when available."""
    meminfo = {"total_kib": None, "available_kib": None}
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    meminfo["total_kib"] = _safe_float(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    meminfo["available_kib"] = _safe_float(line.split()[1])
    except OSError:
        pass
    if meminfo["total_kib"] is None:
        try:
            import psutil
            vm = psutil.virtual_memory()
            meminfo["total_kib"] = vm.total / 1024
            meminfo["available_kib"] = vm.available / 1024
        except (ImportError, OSError, AttributeError):
            pass
    return meminfo


def _read_nvidia_metrics() -> Dict[str, object]:
    stats = {"gpu_count": 0, "gpu_names": [], "driver_version": None,
             "total_vram_mb": None, "free_vram_mb": None, "used_vram_mb": None}
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return stats
    try:
        result = subprocess.run(
            [nvidia_smi, "--query-gpu=name,driver_version,memory.total,memory.free,memory.used",
             "--format=csv,noheader,nounits"], capture_output=True, text=True,
            check=False, timeout=5)
        if result.returncode != 0 or not result.stdout.strip():
            return stats
        rows = [[part.strip() for part in row.split(",")]
                for row in result.stdout.splitlines() if row.strip()]
        rows = [row for row in rows if len(row) >= 5]
        if not rows:
            return stats
        stats["gpu_count"] = len(rows)
        stats["gpu_names"] = [row[0] for row in rows]
        stats["driver_version"] = rows[0][1]
        for key, index in (("total_vram_mb", 2), ("free_vram_mb", 3), ("used_vram_mb", 4)):
            values = [_safe_float(row[index]) for row in rows]
            stats[key] = round(sum(v for v in values if v is not None), 2)
    except (OSError, subprocess.SubprocessError, ValueError):
        return {"gpu_count": 0, "gpu_names": [], "driver_version": None,
                "total_vram_mb": None, "free_vram_mb": None, "used_vram_mb": None}
    return stats


def get_resource_snapshot() -> Dict[str, object]:
    meminfo = _read_meminfo()
    total_kib, available_kib = meminfo["total_kib"], meminfo["available_kib"]
    gpu = _read_nvidia_metrics()
    return {
        "platform": platform.system().lower(),
        "system_ram_mb": round(total_kib / 1024, 2) if total_kib is not None else None,
        "available_ram_mb": round(available_kib / 1024, 2) if available_kib is not None else None,
        "gpu_available": bool(gpu["gpu_count"]), "gpu_count": gpu["gpu_count"],
        "gpu_names": gpu["gpu_names"], "driver_version": gpu["driver_version"],
        "total_vram_mb": gpu["total_vram_mb"], "free_vram_mb": gpu["free_vram_mb"],
        "used_vram_mb": gpu["used_vram_mb"],
    }


def infer_local_inference_profile(snapshot: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    snapshot = snapshot or get_resource_snapshot()
    total, available = snapshot.get("system_ram_mb"), snapshot.get("available_ram_mb")
    profile = {"gpu_available": bool(snapshot.get("gpu_available")), "low_memory_mode": False,
               "recommended_num_ctx": 8192, "web_scrape_concurrency": 2}
    if (total is not None and total < 16000) or (available is not None and available < 6000):
        profile.update(low_memory_mode=True, recommended_num_ctx=4096, web_scrape_concurrency=1)
    free_vram = snapshot.get("free_vram_mb")
    if profile["gpu_available"] and free_vram is not None and float(free_vram or 0) < 1500:
        profile.update(low_memory_mode=True, recommended_num_ctx=4096, web_scrape_concurrency=1)
    return profile


def build_resource_summary() -> Dict[str, object]:
    snapshot = get_resource_snapshot()
    return {"resources": snapshot, "profile": infer_local_inference_profile(snapshot)}
