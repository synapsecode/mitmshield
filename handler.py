import json
from code_checker import check_if_company_code
from mitmproxy import ctx

def handle(flow):
    content_type = flow.request.headers.get("Content-Type", "").lower()
    url = flow.request.url.lower()
    request_text = ""
    try:
        request_text = flow.request.content.decode('utf-8')
    except Exception as e:
        ctx.log.error(e)
    if(len(request_text) == 0):
        return False
    
    # TODO: Special Case for e-mails
    
    if(check_if_company_code(request_text)):
        return True

    return False