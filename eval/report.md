# ARHV evaluation report

Generated: 2026-09-20T13:03:25.934532+00:00

This report is generated only from recorded JSONL runs. Attempts containing infrastructure errors are excluded from pass and round aggregates.

## Red-team results

| Backend | Model | K | Valid N | Passes | Pass rate (95% CI) | Rounds | Round accuracy (95% CI) | Invalid rounds | Mean latency |
|---|---|---:|---:|---:|---|---:|---|---:|---:|
| bedrock | nova-2-lite | 4 | 20 | 0 | 0.0000 [0.0000, 0.1611] | 60 | 0.2000 [0.1183, 0.3178] | 0 | 972 ms |

Chance lines: round accuracy = 1/6 = 0.1667; full-puzzle pass chance = 1/216 = 0.0046.

## API statistics

Family: `mdg-v1`

| Cohort | Attempts | Passes | Pass rate | 95% CI | Round accuracy |
|---|---:|---:|---:|---|---:|
| public | 25 | 12 | 0.4800 | [0.3003, 0.6650] | 0.5600 |
| agent:nova-2-lite:k1 | 1 | 0 | 0.0000 | [0.0000, 0.7935] | 0.6667 |
| agent:nova-2-lite:k4 | 1 | 0 | 0.0000 | [0.0000, 0.7935] | 0.0000 |

## Limitations

- Small samples and self-declared cohorts are directional evidence, not a population study.
- Browser IMU streams are unattested; the physics-consistent simulator is expected to pass.
- A purpose-built optical-flow solver is outside this general-purpose agent benchmark.

## Reproduce

```bash
make bench BACKEND=bedrock MODEL=nova-2-lite K=4 N=10
make report
```
