"""download_ltxv_simple.py — Download LTX-Video model."""
import urllib.request
import os, sys

url = "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.5.safetensors"
out = os.path.expanduser("/Users/an/ComfyUI/models/checkpoints/ltx-video-2b-v0.9.5.safetensors")
tmp = out + ".part"

print(f"Downloading LTX-Video...")
print(f"URL: {url}")
sys.stdout.flush()

req = urllib.request.Request(url)
resp = urllib.request.urlopen(req, timeout=30)
total = int(resp.headers.get("Content-Length", 0))
print(f"File size: {total / 1024**3:.1f} GB")
sys.stdout.flush()

downloaded = 0
with open(tmp, "wb") as f:
    while True:
        chunk = resp.read(1024 * 1024)  # 1MB chunks
        if not chunk:
            break
        f.write(chunk)
        downloaded += len(chunk)
        pct = downloaded * 100 // total
        print(f"\r  {pct}% ({downloaded/1024**3:.1f}/{total/1024**3:.1f} GB)", end="")
        sys.stdout.flush()

os.rename(tmp, out)
print(f"\n✅ Done! {os.path.getsize(out) / 1024**3:.1f} GB")
