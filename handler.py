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
    
    if "mail.google.com" in flow.request.pretty_host and flow.request.method == "POST":
        ctx.log.info('MAILLLLLLLLL')
    
    if(check_if_company_code(request_text)):
        return True

    # request_data = json.loads(request_text)
    # if "chatgpt.com" in url and 'conversation' in url:
    #     if('messages' in request_data):
    #         for m in request_data['messages']:
    #             parts =  m.get('content', dict()).get('parts', [])
    #             for part in parts:
    #                 ctx.log.info(f"PART {part}")
    #                 if( check_if_company_code(part) ):
    #                     return True
    return False