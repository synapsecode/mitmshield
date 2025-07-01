import os
from pathlib import Path
from fuzzydiff import fuzzydiff_in_file
from mitmproxy import ctx

def global_fuzzy_search(target_snippet, min_score=60):
    ctx.log.info("GFUZ")
    folder_path = os.getcwd()
    folder = Path(folder_path)

    for file_path in folder.rglob("*.py"):
        if('fuzzysearch.py' in str(file_path) or 'fuzzydiff.py' in str(file_path) or 'venv' in str(file_path)):
            continue
        found, best_score, best_snippet = fuzzydiff_in_file(file_path, target_snippet, min_score)
        if found:
            ctx.log.info(f"\n✅ Match found in file: {file_path}")
            ctx.log.info(f"📌 Match (score: {best_score}) starting at:\n")
            ctx.log.info(best_snippet)
            ctx.log.info(f"Best Match: {best_score} {best_snippet} {file_path}")
            return True # Early return on first match
    ctx.log.error("❌ No matching code snippet found in any file.")
    return False

def check_if_company_code(text):
    matched = global_fuzzy_search(text)
    ctx.log.info(f"MATCHEDDDDD: {matched}")
    if(not matched):
        return False
    return True