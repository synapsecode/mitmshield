from fuzzysearch import global_fuzzy_search
from mitmproxy import ctx

def check_if_company_code(text):
    # Implement the Fuzzy Search
    matched = global_fuzzy_search(text)
    ctx.log.warn(f"MATCHEDDDDD: {matched}")
    if(not matched):
        return False
    return True