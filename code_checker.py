from fuzzysearch import global_fuzzy_search

def check_if_company_code(text):
    # Implement the Fuzzy Search
    matched = global_fuzzy_search(text)
    print("MATCHEDDDDD", matched)
    if(not matched):
        return False
    return True