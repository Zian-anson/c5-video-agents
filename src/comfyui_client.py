"""comfyui_client.py — ComfyUI REST API client for image & video generation.

Connects to local ComfyUI at localhost:8188.
Supports SDXL image generation (free, local) and Wan2.1 video (optional).
"""
import asyncio
import httpx

COMFYUI_HOST = "http://127.0.0.1:8188"
COMFYUI_OUTPUT = "/Users/an/ComfyUI/output"


async def check_comfyui() -> bool:
    """Check if ComfyUI is running."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{COMFYUI_HOST}/system_stats")
            return r.status_code == 200
    except Exception:
        return False


async def get_available_nodes() -> list[str]:
    """Get available node types from ComfyUI."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{COMFYUI_HOST}/object_info")
            if r.status_code == 200:
                return list(r.json().keys())
            return []
    except Exception:
        return []


async def generate_sdxl_image(prompt: str, scene_num: int = 1,
                               seed: int = 42, steps: int = 25) -> dict:
    """Generate an image using local SDXL (free, no API key needed).

    Builds a full txt2img workflow: checkpoint → CLIP → latent → sample → decode → save.
    """
    negative = "blurry, low quality, ugly, distorted, bad anatomy, deformed, extra limbs"
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_base_1.0_0.9vae.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 576, "batch_size": 1}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed, "steps": steps, "cfg": 7.0,
                "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
                "model": ["1", 0], "positive": ["2", 0],
                "negative": ["3", 0], "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"stardust_scene{scene_num}", "images": ["6", 0]}
        }
    }

    try:
        async with httpx.AsyncClient(timeout=300) as client:
            r = await client.post(
                f"{COMFYUI_HOST}/api/prompt",
                json={"prompt": workflow},
            )
            if r.status_code != 200:
                return {"status": "error", "detail": r.text}

            result = r.json()
            prompt_id = result.get("prompt_id", "")

            # Wait for completion
            for _ in range(60):
                await asyncio.sleep(5)
                hist_r = await client.get(f"{COMFYUI_HOST}/history")
                if hist_r.status_code != 200:
                    continue
                history = hist_r.json()
                if prompt_id not in history:
                    continue
                info = history[prompt_id]
                if info.get("status", {}).get("completed"):
                    # Find the output image
                    for nid, outputs in info.get("outputs", {}).items():
                        for img in outputs.get("images", []):
                            fname = img.get("filename", "")
                            return {
                                "status": "success",
                                "image": f"{COMFYUI_OUTPUT}/{fname}",
                                "prompt_id": prompt_id,
                            }
                    return {"status": "success", "prompt_id": prompt_id}
                # Check for errors
                for msg in info.get("status", {}).get("messages", []):
                    if msg[0] == "execution_error":
                        return {"status": "error", "detail": msg[1].get("exception_message", "?")}
            return {"status": "timeout", "prompt_id": prompt_id}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


async def generate_wan_video(prompt: str, scene_num: int = 1,
                             seed: int = 42, steps: int = 10) -> dict:
    """Generate a video using local Wan2.1 text-to-video.

    Official template workflow:
    UNETLoader → ModelSamplingSD3(shift=8) → KSampler
    CLIPLoader(type=wan) → CLIPTextEncode → KSampler
    EmptyHunyuanLatentVideo → KSampler
    KSampler → VAEDecode → CreateVideo → SaveVideo
    """
    negative = "blurry, low quality, ugly, distorted, bad anatomy, deformed"
    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "wan2.1_t2v_1.3B.safetensors",
                "weight_dtype": "default",
            }
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "wan",
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "Wan2.1_VAE.pth"}
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["2", 0]}
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["2", 0]}
        },
        "6": {
            "class_type": "EmptyHunyuanLatentVideo",
            "inputs": {
                "width": 832,
                "height": 480,
                "length": 33,
                "batch_size": 1,
            }
        },
        "7": {
            "class_type": "ModelSamplingSD3",
            "inputs": {"model": ["1", 0], "shift": 8.0}
        },
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed, "steps": steps, "cfg": 6.0,
                "sampler_name": "uni_pc", "scheduler": "simple", "denoise": 1.0,
                "model": ["7", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0],
            }
        },
        "9": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["8", 0], "vae": ["3", 0]}
        },
        "10": {
            "class_type": "CreateVideo",
            "inputs": {"images": ["9", 0], "fps": 16}
        },
        "11": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["10", 0],
                "filename_prefix": f"stardust_scene{scene_num}",
                "format": "mp4",
                "codec": "h264",
            }
        }
    }

    try:
        async with httpx.AsyncClient(timeout=600) as client:
            r = await client.post(
                f"{COMFYUI_HOST}/api/prompt",
                json={"prompt": workflow},
            )
            if r.status_code != 200:
                return {"status": "error", "detail": r.text}

            result = r.json()
            prompt_id = result.get("prompt_id", "")

            # Wan2.1 video generation can take several minutes
            for _ in range(720):
                await asyncio.sleep(5)
                hist_r = await client.get(f"{COMFYUI_HOST}/history")
                if hist_r.status_code != 200:
                    continue
                history = hist_r.json()
                if prompt_id not in history:
                    continue
                info = history[prompt_id]
                if info.get("status", {}).get("completed"):
                    # Scan ALL output nodes for video/files
                    for nid, outputs in info.get("outputs", {}).items():
                        # ComfyUI SaveVideo outputs under "images" key with animated flag
                        for key in ("video", "images", "gifs", "videos"):
                            for item in outputs.get(key, []):
                                fname = item.get("filename", "")
                                if fname.endswith((".mp4", ".webm", ".gif")):
                                    return {
                                        "status": "success",
                                        "video": f"{COMFYUI_OUTPUT}/{fname}",
                                        "prompt_id": prompt_id,
                                    }
                    return {"status": "success", "prompt_id": prompt_id}
                for msg in info.get("status", {}).get("messages", []):
                    if msg[0] == "execution_error":
                        return {"status": "error", "detail": msg[1].get("exception_message", "?")}
            return {"status": "timeout", "prompt_id": prompt_id}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


async def simulate_generate(prompt: str) -> dict:
    """Fallback when ComfyUI is not available."""
    return {
        "status": "simulated",
        "prompt": prompt,
        "note": "ComfyUI not running — run with ComfyUI for actual video generation"
    }
