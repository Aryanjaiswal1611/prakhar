import ast
from typing import Dict, Any

UNSAFE_PATTERNS = ["os.system(", "subprocess.Popen(", "shutil.rmtree(", "rm -rf", "Format-Volume", "DROP DATABASE"]


def validate_patch(language: str, patch_text: str) -> Dict[str, Any]:
    checks = []
    logs = []
    status = "passed"
    if not patch_text or not patch_text.strip():
        return {"status":"failed","checks":[{"name":"non_empty","ok":False,"detail":"Patch is empty"}],"logs":["Patch text empty"]}

    checks.append({"name":"non_empty","ok":True,"detail":"Patch contains content"})
    lowered = patch_text.lower()
    unsafe = [p for p in UNSAFE_PATTERNS if p.lower() in lowered]
    ok_safe = len(unsafe) == 0
    checks.append({"name":"unsafe_patterns","ok":ok_safe,"detail":"No unsafe patterns detected" if ok_safe else f"Unsafe patterns: {unsafe}"})
    if not ok_safe:
        status = "failed"
        logs.append("Unsafe pattern detected; patch rejected for safety.")

    if language == "python":
        try:
            ast.parse(patch_text)
            checks.append({"name":"python_syntax","ok":True,"detail":"Python AST parse succeeded"})
        except SyntaxError as e:
            checks.append({"name":"python_syntax","ok":False,"detail":str(e)})
            logs.append(f"Python syntax error: {e}")
            status = "failed"
    elif language in ("javascript","java"):
        # lightweight static checks for MVP
        brace_ok = patch_text.count("{") == patch_text.count("}")
        checks.append({"name":"brace_balance","ok":brace_ok,"detail":"Braces balanced" if brace_ok else "Unbalanced braces"})
        if not brace_ok:
            status = "failed"
    else:
        checks.append({"name":"language_supported","ok":False,"detail":"Unsupported language"})
        status = "failed"

    checks.append({"name":"review_only","ok":True,"detail":"Patch is review-only; not executed on host"})
    logs.append("Validation completed in safe static/simulated mode.")
    return {"status": status, "checks": checks, "logs": logs}
