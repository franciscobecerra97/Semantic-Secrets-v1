"""Process and CUDA telemetry kept outside repeat-equality projections."""

from __future__ import annotations

import platform
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class Telemetry:
    started: float = 0.0

    def __enter__(self) -> "Telemetry":
        import psutil

        self.started = time.perf_counter()
        self._stop = threading.Event()
        process = psutil.Process()
        self._rss_peak = int(process.memory_info().rss)

        def sample_rss() -> None:
            while not self._stop.wait(0.01):
                self._rss_peak = max(self._rss_peak, int(process.memory_info().rss))

        self._sampler = threading.Thread(target=sample_rss, name="p9-v3b-rss-sampler", daemon=True)
        self._sampler.start()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
        except ImportError:
            pass
        return self

    def __exit__(self, *_: object) -> None:
        if hasattr(self, "_stop"):
            self._stop.set()
        if hasattr(self, "_sampler"):
            self._sampler.join(timeout=1)
        return None

    def finish(self) -> dict[str, Any]:
        allocated = reserved = 0
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.synchronize()
                allocated = int(torch.cuda.max_memory_allocated())
                reserved = int(torch.cuda.max_memory_reserved())
        except ImportError:
            pass
        self._stop.set()
        self._sampler.join(timeout=1)
        rss_bytes = self._rss_peak
        return {
            "elapsed_seconds": round(time.perf_counter() - self.started, 6),
            "peak_process_rss_bytes": rss_bytes,
            "framework_peak_gpu_allocated_bytes": allocated,
            "framework_peak_gpu_reserved_bytes": reserved,
        }


def environment_record() -> dict[str, Any]:
    record: dict[str, Any] = {
        "platform": platform.platform(),
        "python": sys.version,
    }
    try:
        import torch

        record.update(
            torch_version=torch.__version__,
            framework_cuda=torch.version.cuda,
            cuda_available=torch.cuda.is_available(),
            cudnn_version=torch.backends.cudnn.version(),
        )
        if torch.cuda.is_available():
            record["gpu"] = [
                {
                    "index": index,
                    "name": torch.cuda.get_device_name(index),
                    "capability": list(torch.cuda.get_device_capability(index)),
                    "total_memory_bytes": torch.cuda.get_device_properties(index).total_memory,
                }
                for index in range(torch.cuda.device_count())
            ]
    except ImportError:
        record["torch"] = "not-installed"
        record["cuda_available"] = False
    return record
