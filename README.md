# Amendment Tessellation

Place the amendments on the chamber floor. The seams matter more than the speeches.

A facilitator freezes one motion, its scope rules, and the proposer addresses. Each proposer files one amendment in prose. Validators label scope and draw only the semantic conflict edges. Contract code then examines every subset and stores the largest mutually compatible package, using a public lexicographic tie-break.

The result is `PACKAGE`, `NO_PACKAGE`, or `INCOMPLETE`. The model cannot select favorites or silently discard a conflicting edge after consensus.

Configured live proposers are operator-controlled role fixtures, not independent legislators.

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```

## Live chamber

- Contract: [`0x348579936Bce80a504800c0caf714f833De16E0A`](https://explorer-studio.genlayer.com/address/0x348579936Bce80a504800c0caf714f833De16E0A)
- Reviewed source: [`971c35d`](https://github.com/IDAK2/amendment-tessellation/tree/971c35d3bf8db5e3fafb7964a14337901e660458)
- Live tessellation: `TILE-1791756982`, conflict `[0,1]`, selected package `[0,2]`.
- Verification: finalized, majority agree, successful execution, exact deployed-source match.
