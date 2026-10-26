"""Offline checks for cross-agent budget enforcement; no OpenRouter calls."""
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import budget_proxy as proxy

def main():
    prior = proxy.ROOT
    with tempfile.TemporaryDirectory() as temp:
        proxy.ROOT = Path(temp)
        ledger = proxy.Ledger()
        assert ledger.status()["available_usd"] == 1.0
        def attempt(i):
            return ledger.reserve(f"agent-{i}", f"agent-{i}", 400_000,
                                  {"model": proxy.MODEL, "messages": [{"role":"user","content":"test"}]})
        with ThreadPoolExecutor(max_workers=4) as pool:
            successes = list(pool.map(attempt, range(4)))
        assert sum(successes) == 2, successes
        assert ledger.status()["committed_usd"] == 0.8
        # Durable reservation after restart, including unsettled requests.
        fresh = proxy.Ledger()
        assert fresh.status()["committed_usd"] == 0.8
        assert not fresh.reserve("extra", "agent-extra", 300_000, {})
        # After a known low-cost completion, unused reservation becomes available.
        first = successes.index(True)
        fresh.settle(f"agent-{first}", {"cost": 0.01, "prompt_tokens":100,
                     "completion_tokens":20}, "test-id", "offline_test")
        assert fresh.status()["committed_usd"] == 0.41
        assert fresh.reserve("new-agent","new-agent",550_000,{})
        assert fresh.status()["committed_usd"] == 0.96
        assert not fresh.reserve("overspend","agent-9",50_000,{})
        assert fresh.status()["committed_usd"] <= 1.0
        fresh.db.close()
        ledger.db.close()
        print("PASS: four concurrent reservations, budget denial, settlement, persistence, replay")
    proxy.ROOT = prior

if __name__ == "__main__":
    main()
