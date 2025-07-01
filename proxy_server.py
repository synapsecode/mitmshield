from handler import handle
from mitmproxy import ctx
import asyncio
from mitmproxy import http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from utils import get_code_in_image, save_image_for_ocr
from code_checker import check_if_company_code

class BlockProprietaryRequests:
    def __init__(self):
        self.tasks = set()

    def request(self, flow: http.HTTPFlow) -> None:
        async def ocr_and_block_request():
            try:
                ocr_text = await get_code_in_image(fp)
                print("OCR Result:", ocr_text)
                if check_if_company_code(ocr_text):
                    print("COMPANY CODE_____BLOICKUINGGGGGG")
                    self.block_request(flow, "COMPANY_CODE_FOUND")
                else:
                    flow.resume()  # Resume if not blocked
            except Exception as e:
                print("OCR Error:", e)
                self.block_request(flow, "OCR_EXCEPTION")

        url = flow.request.url.lower()
        content_type = flow.request.headers.get("Content-Type", "").lower()

        ALLOWED_IMG_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]

        if content_type.startswith("image/") or any(ext in url for ext in ALLOWED_IMG_EXTENSIONS):
            fp = save_image_for_ocr(flow)
            if not fp:
                self.block_request(flow, "SAVE_FAILED")
                return

            # Pause the flow
            flow.intercept()

            # Track tasks to prevent GC
            task = asyncio.ensure_future(ocr_and_block_request())
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)

        conditions = [
            "chatgpt.com" in url and 'conversation' in url,
            'x.com' in url and 'createtweet' in url,
            'stackoverflow.com' in url and 'submit' in url,
        ]
        if(any(conditions)):
            blocked = handle(flow)
            if blocked:
                self.block_request(flow, "COMPANY_CODE_FOUND")

    def block_request(self, flow: http.HTTPFlow, reason: str):
        print(f"[{reason}] Blocking request to {flow.request.url}")
        flow.response = http.Response.make(
            403,
            b"Request blocked: " + reason.encode(),
            {"Content-Type": "text/plain"}
        )
        try:
            flow.resume()
        except:
            pass

async def main():
    print("Starting mitmproxy programmatically...")
    options = Options(listen_host='0.0.0.0', listen_port=8080, http2=True)
    master = DumpMaster(options, with_termlog=True, with_dumper=False)
    master.addons.add(BlockProprietaryRequests())
    await master.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Proxy interrupted.")
