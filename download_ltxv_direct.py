"""download_ltxv_direct.py — Direct download with progress bar."""
import urllib.request
import os
import sys

url = "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.5.safetensors"
out = os.path.expanduser("/Users/an/ComfyUI/models/checkpoints/ltx-video-2b-v0.9.5.safetensors")

class Progress:
    def __init__(self):
        self.last_pct = 0

    def __call__(self, count, block_size, total_size):
        pct = int(count * block_size * 100 / total_size)
        if pct != self.last_pct:
            mb = count * block_size / 1024 / 1024
            total_mb = total_size / 1024 / 1024
            print(f"\r  {pct}% ({mb:.0f}/{total_mb:.0f} MB)", end="", flush=True)
            self.last_pct = pct

print(f"Downloading LTX-Video (6.3 GB)...")
print(f"  To: {out}")
urllib.request.urlretrieve(url, out, Progress())
print(f"\n✅ Done! {os.path.getsize(out) / 1024**3:.1f} GB")
