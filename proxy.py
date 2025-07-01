from concurrent.futures import ThreadPoolExecutor
from handler import handle
from mitmproxy import ctx
import asyncio
from mitmproxy import http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from utils import get_code_in_image, remove_image, run_async_in_thread, save_image_for_ocr
from code_checker import check_if_company_code

executor = ThreadPoolExecutor(max_workers=2)

class BlockProprietaryRequests:
    def __init__(self):
        self.tasks = set()

    def request(self, flow: http.HTTPFlow) -> None:
        url = flow.request.url.lower()
        content_type = flow.request.headers.get("Content-Type", "").lower()

        ALLOWED_IMG_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]

        # ----------- HANDLE IMAGE UPLOAD ----------
        if content_type.startswith("image/") or any(ext in url for ext in ALLOWED_IMG_EXTENSIONS):
            fp = save_image_for_ocr(flow)
            if(fp == None):
                self.block_request(flow, "SAVE_FAILED")
                remove_image(fp)
                return True
            
            print("GETTING OCR")
            future = executor.submit(run_async_in_thread, get_code_in_image(fp))
            try:
                ocr_text = future.result(timeout=10)  # Wait up to 10s
                print("OCR RESULT:", ocr_text)
                if check_if_company_code(ocr_text):
                    self.block_request(flow, "COMPANY_CODE_FOUND_IN_IMAGE")
                    remove_image(fp)
                    return
                return True #EXIT
            except Exception as e:
                print("OCR ERROR:", e)
                self.block_request(flow, "OCR_EXCEPTION")
                remove_image(fp)
                return
         # ----------- HANDLE IMAGE UPLOAD ----------

        conditions = [
            "chatgpt.com" in url and 'conversation' in url,
            'x.com' in url and 'createtweet' in url,
            'stackoverflow.com' in url and 'submit' in url,
        ]
        if(any(conditions)):
            blocked = handle(flow)
            if blocked:
                remove_image(fp)
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

# This line initializes the class instance when mitmproxy runs.
addons = [
    BlockProprietaryRequests()
]

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

