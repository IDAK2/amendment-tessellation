# Requirement matrix

| Requirement | Code path | Evidence status |
|---|---|---|
| Consensus-bound conflict graph | `_map` strict equality | PASS: forged graph rejected |
| Complete amendment coverage | Dense unique statuses and canonical conflict pairs | PASS: strict direct suite |
| Deterministic outcome | `maximum_package` exhaustive subset search | PASS: conflict and scope cases |
| Authorization and replay | Frozen proposers and one amendment each | PASS: targeted test |
| Liveness | Complete, expired-partial, and incomplete paths | PASS: targeted tests |
| Deployed-source match | Verification script | PASS: exact byte match |
