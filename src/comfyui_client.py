"""comfyui_client.py — ComfyUI REST API client for video generation.

Connects to local ComfyUI at localhost:8188.
Supports Kling / Minimax / Wan API nodes installed in the ComfyUI instance.
"""
import json
import httpx

COMFYUI_HOST = "http://127.0.0.1:8188"


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


async def find_video_nodes() -> list[str]:
    """Find video-related API nodes (Kling, Minimax, Wan, etc.)."""
    nodes = await get_available_nodes()
    video_keywords = ["kling", "minimax", "wan", "videonode", "texttovideo", "imagetovideo"]
    return [n for n in nodes if any(k in n.lower() for k in video_keywords)]


async def generate_video(prompt: str, node_type: str = "KlingTextToVideoNode",
                         duration: int = 5, negative_prompt: str = "") -> dict:
    """Send a video generation prompt to ComfyUI via the specified API node.

    This builds a minimal workflow that calls the video API node.
    Each node type has different parameters — we use the most common ones.

    Args:
        prompt: The video description prompt
        node_type: The ComfyUI node class to use (e.g., 'KlingTextToVideoNode')
        duration: Target video duration in seconds
        negative_prompt: What to avoid

    Returns:
        dict with status and prompt_id
    """
    # Build minimal workflow for the video API node
    # This is a generic template — specific nodes may need different params
    workflow = {
        "3": {
            "class_type": node_type,
            "inputs": {
                "prompt": prompt,
                "negative_prompt": negative_prompt or None,
                "duration": duration,
            }
        }
    }

    payload = {"prompt": workflow}

    async with httpx.AsyncClient(timeout=300) as client:
        r = await client.post(
            f"{COMFYUI_HOST}/api/prompt",
            json=payload,
        )
        if r.status_code == 200:
            result = r.json()
            return {"status": "queued", "prompt_id": result.get("prompt_id")}
        else:
            return {"status": "error", "detail": r.text}


async def simulate_generate(prompt: str) -> dict:
    """Simulate video generation — returns a mock result for demo/testing.
    Real generation would use generate_video() with the actual ComfyUI node."""
    return {
        "status": "simulated",
        "prompt": prompt,
        "note": "Demo mode — wire to actual ComfyUI node for real generation"
    }
