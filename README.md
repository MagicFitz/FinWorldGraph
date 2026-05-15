# FinWorldGraph

A basic MVP implementation of **Agent-Conditioned Projection Function**:

\[
P_{a,t} = \Pi(W_t, C_a, H_{a,<t})
\]

This repo now provides a rule-based `hard filter + soft ranking + structured packaging` pipeline.

## Files

- `projector.py`: core dataclasses and projection pipeline.
- `demo_projection.py`: small runnable demo that prints a `PerceptionPack` JSON.

## Run demo

```bash
python demo_projection.py
```

## Implemented pipeline (v0.1)

1. Visibility Filter (hard constraints)
   - future leakage check
   - source access check
   - channel delay check
2. Candidate Recall (rule-based)
3. Feature Construction
   - portfolio exposure
   - sector exposure
   - role affinity
   - temporal decay
   - source reliability
   - novelty
   - memory / belief relevance
   - network exposure
   - market move relevance
4. Scoring & Ranking (weighted linear score)
5. Diversification & Budgeting (type budgets + canonical event dedup)
6. PerceptionPack Builder (with score/reasons/evidence/hidden summary)
