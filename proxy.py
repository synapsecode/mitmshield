from concurrent.futures import ThreadPoolExecutor
from mitmproxy import http, ctx
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from handler import handle
from utils import get_code_in_image, remove_image, run_async_in_thread, save_image_for_ocr
from code_checker import check_if_company_code

import asyncio
import os

executor = ThreadPoolExecutor(max_workers=4)

ALLOWED_IMG_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

class BlockProprietaryRequests:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def request(self, flow: http.HTTPFlow) -> None:
        url = flow.request.url.lower()
        method = flow.request.method
        content_type = flow.request.headers.get("Content-Type", "").lower()
        if self.is_image_request(url, content_type):
            self.handle_image_request(flow)
        elif method.lower() in ['post', 'put']:
            self.handle_block_condition(flow)

    def is_image_request(self, url: str, content_type: str) -> bool:
        return content_type.startswith("image/") or any(url.endswith(ext) for ext in ALLOWED_IMG_EXTENSIONS)

    def handle_image_request(self, flow: http.HTTPFlow):
        fp = save_image_for_ocr(flow)
        if not fp or not os.path.exists(fp):
            self.block_request(flow, "SAVE_FAILED")
            return

        ctx.log.info("Running OCR for image...")
        future = executor.submit(run_async_in_thread, get_code_in_image(fp))
        try:
            ocr_text = future.result(timeout=10)
            ctx.log.info(f"OCR RESULT: {ocr_text}")

            if check_if_company_code(ocr_text):
                self.block_request(flow, "COMPANY_CODE_FOUND_IN_IMAGE")
            # else allow through

        except Exception as e:
            ctx.log.warn(f"OCR ERROR: {e}")
            self.block_request(flow, "OCR_EXCEPTION")

        finally:
            remove_image(fp)

    def handle_block_condition(self, flow: http.HTTPFlow):
        blocked = handle(flow)
        if blocked:
            self.block_request(flow, "COMPANY_CODE_FOUND")

    def block_request(self, flow: http.HTTPFlow, reason: str):
        ctx.log.warn(f"[{reason}] Blocking request to {flow.request.url}")
        flow.response = http.Response.make(
            403,
            f"Request blocked: {reason}".encode(),
            {"Content-Type": "text/plain"}
        )
        try:
            flow.resume()
        except Exception:
            pass

# ---------- Programmatic Startup (if run as main) ----------
addons = [BlockProprietaryRequests()]

async def main():
    print("Starting mitmproxy programmatically...")
    options = Options(listen_host='0.0.0.0', listen_port=8080, http2=True)
    master = DumpMaster(options, with_termlog=True, with_dumper=False)
    master.addons.add(BlockProprietaryRequests())
    try:
        await master.run()
    except KeyboardInterrupt:
        print("Proxy interrupted.")

if __name__ == "__main__":
    asyncio.run(main())
