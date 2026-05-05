"""download_ltxv.py — Download LTX-Video model using huggingface_hub."""
from huggingface_hub import hf_hub_download
import os

out_dir = os.path.expanduser("/Users/an/ComfyUI/models/checkpoints")
os.makedirs(out_dir, exist_ok=True)

print("Downloading LTX-Video 2B v0.9.5...")
path = hf_hub_download(
    repo_id="Lightricks/LTX-Video",
    filename="ltx-video-2b-v0.9.5.safetensors",
    local_dir=out_dir,
    local_dir_use_symlinks=False,
    resume_download=True,
)
print(f"✅ Downloaded to: {path}")
print(f"Size: {os.path.getsize(path) / 1024**3:.1f} GB")
