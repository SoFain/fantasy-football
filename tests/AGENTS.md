# Purpose

Test placement and validation discipline.

# Ownership

This subtree owns unit and regression tests. Tests should sit near the behavior changed and protect the contract that can regress.

# Local Contracts

- Add tests near the changed behavior.
- Prefer focused tests first.
- Avoid full suites unless risk justifies it or the user asks.
- Preserve command output caps for noisy tests.
- Where relevant, test write gates, no-live-ranking writes, no champion activation, and absence of the old Python tournament path.

# Work Guidance

Keep fixtures small. Test contracts and boundary behavior before incidental formatting. Do not add broad snapshot-style tests for narrow logic.

# Verification

Focused example with a byte-capped readback:

```powershell
$log = New-TemporaryFile
.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests *> $log
$status = $LASTEXITCODE
$text = Get-Content -LiteralPath $log -Raw
if ($text.Length -gt 4000) { $text.Substring($text.Length - 4000) } else { $text }
Remove-Item -LiteralPath $log
exit $status
```

Use full discovery only when source risk warrants it:

```powershell
.\venv\Scripts\python.exe -m unittest discover tests
```

# Child DOX Index

No child AGENTS.md files exist yet.
