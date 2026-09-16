import shutil
import subprocess
from typing import Dict, Optional


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _read_meminfo() -> Dict[str, Optional[float]]:
    meminfo = {"total_kib": None, "available_kib": None}
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    meminfo["total_kib"] = _safe_float(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    meminfo["available_kib"] = _safe_float(line.split()[1])
    except OSError:
        return meminfo

    return meminfo


def _read_nvidia_metrics() -> Dict[str, Optional[float]]:
    stats = {
        "gpu_count": 0,
        "gpu_names": [],
        "driver_version": None,
        "total_vram_mb": None,
        "free_vram_mb": None,
        "used_vram_mb": None,
    }

    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return stats

    try:
        result = subprocess.run(
            [
                nvidia_smi,
                "--query-gpu=name,driver_version,memory.total,memory.free,memory.used",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return stats

        rows = [row.strip() for row in result.stdout.splitlines() if row.strip()]
        stats["gpu_count"] = len(rows)
        gpu_names = []
        total_vram_mb_values = []
        free_vram_mb_values = []
        used_vram_mb_values = []

        for row in rows:
            parts = [part.strip() for part in row.split(",")]
            if len(parts) < 5:
                continue
            gpu_names.append(parts[0])
            total_vram_mb_values.append(_safe_float(parts[2]))
            free_vram_mb_values.append(_safe_float(parts[3]))
            used_vram_mb_values.append(_safe_float(parts[4]))

        stats["gpu_names"] = gpu_names
        if total_vram_mb_values:
            stats["total_vram_mb"] = sum(v for v in total_vram_mb_values if v is not None)
        if free_vram_mb_values:
            stats["free_vram_mb"] = sum(v for v in free_vram_mb_values if v is not None)
        if used_vram_mb_values:
            stats["used_vram_mb"] = sum(v for v in used_vram_mb_values if v is not None)

        driver_result = subprocess.run(
            [nvidia_smi, "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if driver_result.returncode == 0 and driver_result.stdout.strip():
            stats["driver_version"] = driver_result.stdout.strip().splitlines()[0].strip()
    except (OSError, subprocess.SubprocessError, ValueError):
        return {"gpu_count": 0, "gpu_names": [], "driver_version": None, "total_vram_mb": None, "free_vram_mb": None, "used_vram_mb": None}

    return stats


def get_resource_snapshot() -> Dict[str, object]:
    meminfo = _read_meminfo()
    total_kib = meminfo.get("total_kib")
    available_kib = meminfo.get("available_kib")
    total_ram_mb = None if total_kib is None else round(total_kib / 1024, 2)
    available_ram_mb = None if available_kib is None else round(available_kib / 1024, 2)

    gpu_stats = _read_nvidia_metrics()
    return {
        "platform": "linux",
        "system_ram_mb": total_ram_mb,
        "available_ram_mb": available_ram_mb,
        "gpu_available": bool(gpu_stats.get("gpu_count")),
        "gpu_count": gpu_stats.get("gpu_count", 0),
        "gpu_names": gpu_stats.get("gpu_names", []),
        "driver_version": gpu_stats.get("driver_version"),
        "total_vram_mb": gpu_stats.get("total_vram_mb"),
        "free_vram_mb": gpu_stats.get("free_vram_mb"),
        "used_vram_mb": gpu_stats.get("used_vram_mb"),
    }


def infer_local_inference_profile(snapshot: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    if snapshot is None:
        snapshot = get_resource_snapshot()

    system_ram_mb = snapshot.get("system_ram_mb")
    available_ram_mb = snapshot.get("available_ram_mb")
    gpu_available = bool(snapshot.get("gpu_available"))

    profile = {
        "gpu_available": gpu_available,
        "low_memory_mode": False,
        "recommended_num_ctx": 8192,
        "web_scrape_concurrency": 4,
    }

    if system_ram_mb is not None and system_ram_mb < 16000:
        profile["low_memory_mode"] = True
        profile["recommended_num_ctx"] = 4096
        profile["web_scrape_concurrency"] = 2
    elif available_ram_mb is not None and available_ram_mb < 6000:
        profile["low_memory_mode"] = True
        profile["recommended_num_ctx"] = 4096
        profile["web_scrape_concurrency"] = 2

    if gpu_available and snapshot.get("free_vram_mb") is not None:
        free_vram_mb = float(snapshot.get("free_vram_mb", 0) or 0)
        if free_vram_mb < 1500:
            profile["low_memory_mode"] = True
            profile["recommended_num_ctx"] = 4096
            profile["web_scrape_concurrency"] = 2

    return profile


def build_resource_summary() -> Dict[str, object]:
    snapshot = get_resource_snapshot()
    return {
        "resources": snapshot,
        "profile": infer_local_inference_profile(snapshot),
    }
