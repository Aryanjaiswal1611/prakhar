from app.remediation.rule_based import rule_based_remediation
from app.services.patch_validation import validate_patch

def test_rule_based_patch_generated():
    run={"experiment":{"experiment_type":"database_failure","target_node_key":"database","severity":4},"affected_nodes":["backend","frontend"]}
    rec=rule_based_remediation(run,"python")
    assert rec["source"]=="rule"
    assert "circuit breaker" in rec["patch_text"].lower()
    v=validate_patch(rec["patch_language"], rec["patch_text"])
    assert v["status"] in ("passed","failed")
    assert any(c["name"]=="python_syntax" for c in v["checks"])
