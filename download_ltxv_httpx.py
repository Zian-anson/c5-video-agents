"""download_ltxv_httpx.py — Download LTXV model using httpx with progress."""
import httpx
import os, sys

url = "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.5.safetensors"
out = os.path.expanduser("/Users/an/ComfyUI/models/checkpoints/ltx-video-2b-v0.9.5.safetensors")
tmp = out + ".part"

print(f"Connecting...")
sys.stdout.flush()

client = httpx.Client(timeout=30, follow_redirects=True)
with client.stream("GET", url) as response:
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))
    print(f"Size: {total / 1024**3:.1f} GB")
    sys.stdout.flush()

    downloaded = 0
    with open(tmp, "wb") as f:
        for chunk in response.iter_bytes(1024 * 1024):
            f.write(chunk)
            downloaded += len(chunk)
            pct = downloaded * 100 // total if total else 0
            print(f"\r  {pct}% ({downloaded/1024**3:.1f}/{total/1024**3:.1f} GB)", end="")
            sys.stdout.flush()

os.rename(tmp, out)
print(f"\n✅ Done! {os.path.getsize(out) / 1024**3:.1f} GB")
