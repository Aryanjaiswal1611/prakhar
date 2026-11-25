from typing import Dict, Any, List

TEMPLATES = {
    ("database_failure","python"): '''# Suggested patch: circuit breaker + retry for DB access
import time
from functools import wraps

class CircuitBreaker:
    def __init__(self, max_failures=3, reset_timeout=30):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.open_until = 0

    def allow(self):
        return time.time() >= self.open_until

    def record_success(self):
        self.failures = 0

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.max_failures:
            self.open_until = time.time() + self.reset_timeout

db_breaker = CircuitBreaker()

def with_retry(retries=3, delay=1):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not db_breaker.allow():
                raise RuntimeError("DB circuit open")
            last = None
            for i in range(retries):
                try:
                    result = fn(*args, **kwargs)
                    db_breaker.record_success()
                    return result
                except Exception as e:
                    last = e
                    db_breaker.record_failure()
                    time.sleep(delay * (2 ** i))
            raise last
        return wrapper
    return deco
''',
    ("database_failure","javascript"): '''// Suggested patch: circuit breaker + retry for DB access
const breaker = { failures: 0, max: 3, openUntil: 0, resetMs: 30000 };
async function withRetry(fn, retries = 3, delay = 500) {
  if (Date.now() < breaker.openUntil) throw new Error("DB circuit open");
  let last;
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fn();
      breaker.failures = 0;
      return res;
    } catch (e) {
      last = e;
      breaker.failures++;
      if (breaker.failures >= breaker.max) breaker.openUntil = Date.now() + breaker.resetMs;
      await new Promise(r => setTimeout(r, delay * Math.pow(2, i)));
    }
  }
  throw last;
}
module.exports = { withRetry };
''',
    ("database_failure","java"): '''// Suggested patch: circuit breaker + retry for DB access
public class DbResilience {
    private int failures = 0; private final int maxFailures = 3;
    private long openUntil = 0; private final long resetMs = 30000;
    public synchronized <T> T withRetry(java.util.concurrent.Callable<T> fn) throws Exception {
        if (System.currentTimeMillis() < openUntil) throw new RuntimeException("DB circuit open");
        Exception last = null;
        for (int i = 0; i < 3; i++) {
            try { T r = fn.call(); failures = 0; return r; }
            catch (Exception e) { last = e; failures++; if (failures >= maxFailures) openUntil = System.currentTimeMillis() + resetMs;
                Thread.sleep((long)(500 * Math.pow(2, i))); }
        }
        throw last;
    }
}
''',
}

GENERIC = {
"python": "# Suggested resilience patch\n# Add timeout, retry, circuit breaker, and fallback handling around dependency call.\n",
"javascript": "// Suggested resilience patch\n// Add timeout, retry, circuit breaker, and fallback handling around dependency call.\n",
"java": "// Suggested resilience patch\n// Add timeout, retry, circuit breaker, and fallback handling around dependency call.\n",
}


def rule_based_remediation(run: Dict[str, Any], language: str) -> Dict[str, Any]:
    exp = run.get("experiment", {})
    ftype = exp.get("experiment_type", "unknown")
    target = exp.get("target_node_key", "unknown")
    affected = run.get("affected_nodes", [])
    lang = language if language in ("python","javascript","java") else "python"
    patch = TEMPLATES.get((ftype, lang)) or GENERIC[lang]
    rec_map = {
        "database_failure": "Implement circuit breaker, retries with backoff, and read-replica/failover for database access.",
        "server_failure": "Add health checks, auto-restart, and multiple replicas behind a load balancer.",
        "network_latency": "Add timeouts, adaptive retries, and caching for slow dependencies.",
        "packet_loss": "Use retries with idempotency keys and degrade gracefully on transient network errors.",
        "cpu_overload": "Apply autoscaling, rate limiting, and workload shedding.",
        "memory_exhaustion": "Add memory limits, leak detection, and graceful degradation/fallback cache.",
        "api_timeout": "Configure strict timeouts, circuit breakers, and fallback responses.",
        "service_dependency_failure": "Isolate dependencies with bulkheads and circuit breakers; provide fallback paths.",
    }
    recommendation = rec_map.get(ftype, "Add retries, timeouts, circuit breakers, and redundancy for critical dependencies.")
    root = f"{ftype.replace('_',' ').title()} at '{target}' caused cascading impact due to dependency coupling."
    return {
        "source": "rule",
        "failure_description": f"{ftype} on {target} (severity {exp.get('severity',3)}).",
        "root_cause": root,
        "affected_components": affected,
        "recommendation": recommendation,
        "patch_language": lang,
        "patch_text": patch,
        "expected_improvement": "Expected resilience score improvement: +8 to +20 depending on redundancy and recovery settings.",
    }
