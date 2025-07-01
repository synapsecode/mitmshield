import os
import time
import asyncio

async def get_code_in_image(image_path: str):
    try:
        process = await asyncio.create_subprocess_exec(
            "./xocr",
            image_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            print(f"SUBPROCESS_ERROR:\n{stderr.decode().strip()}")
            return ""
        return stdout.decode().strip()
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}")
        return ""

def save_image_for_ocr(flow):
    SAVE_DIR = os.path.join(os.getcwd(), 'images')
    os.makedirs(SAVE_DIR, exist_ok=True)
    timestamp = int(time.time())
    binary_data = flow.request.content
    ext = "bin"
    if b"\x89PNG" in binary_data:
        ext = "png"
    elif b"\xFF\xD8" in binary_data:
        ext = "jpg"
    elif b"image/webp" in binary_data:
        ext = "webp"
    if(ext == "bin"):
        return None
    filename = f"image_{timestamp}.{ext}"
    filepath = os.path.join(SAVE_DIR, filename)
    try:
        with open(filepath, "wb") as f:
            f.write(binary_data)
        print(f"[+] Saved image to {filepath}")
        return filepath
    except Exception as e:
        print(f"[!] Failed to save image: {e}")
        return None

def remove_image(filepath):
    os.remove(filepath)

def run_async_in_thread(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    loop.close()
    return result
