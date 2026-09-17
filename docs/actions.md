# GitHub Actions

## 1. Mappa dei workflow

| Workflow | Trigger | Durata tipica | Bloccante |
| --- | --- | --- | --- |
| `ci.yml` | push, pull_request, manuale | 8 min | sì |
| `docs.yml` | modifiche a `docs/**`, `*.md` | 2 min | sì |
| `benchmark.yml` | PR etichettate `area:model`, cron notturno | 40 min | no |
| `release.yml` | tag `v*` | 5 min | — |
| `stale.yml` | cron giornaliero | 1 min | no |
| `labeler.yml` | pull_request_target | 30 s | no |
| `codeql.yml` | push, PR, cron settimanale | 10 min | no |

## 2. Grafo dei job di CI

```text
lint ─────┐
types ────┼──▶ test (3.11, 3.12) ──▶ smoke (k3-nano) ──▶ report
security ─┘
```

`fail-fast: false` sulla matrice, così un fallimento su 3.12 non nasconde 3.11.

## 3. Buone pratiche applicate

- `concurrency` per branch con `cancel-in-progress: true`.
- `permissions: contents: read` come default, allargato solo dove serve.
- Action di terze parti pinnate al **commit SHA**.
- `timeout-minutes` su ogni job per evitare run appesi.
- `workflow_dispatch` su tutti i workflow per l'esecuzione manuale.
- Cache pip e cache dei dataset di test.
- Artefatti (log, report di coverage, risultati dei benchmark) caricati a ogni run.

## 4. Runner GPU self-hosted

```yaml
  benchmark:
    runs-on: [self-hosted, linux, x64, gpu-a100]
    timeout-minutes: 90
    if: github.event.pull_request.head.repo.full_name == github.repository
```

I job GPU non girano mai su PR provenienti da fork: niente esecuzione di codice non fidato
su hardware con segreti.

## 5. Segreti usati

| Segreto | Scopo | Dove |
| --- | --- | --- |
| `GITHUB_TOKEN` | commenti, release, etichette | automatico |
| `PYPI_TOKEN` | pubblicazione del pacchetto | solo `release.yml` |
| `WANDB_API_KEY` | log dei benchmark | solo runner self-hosted |

Nessun segreto è disponibile ai workflow `pull_request` da fork.

## 6. Check obbligatori per il merge

`lint` · `types` · `test (3.11)` · `test (3.12)` · `smoke` · `security` · `docs`

Configurati nella branch protection di `main` e `develop`.

## 7. Diagnosi dei fallimenti più comuni

| Sintomo | Causa probabile | Rimedio |
| --- | --- | --- |
| `ruff format --check` rosso | codice non formattato | `ruff format .` |
| `mypy` rosso solo in CI | versione diversa in locale | allineare con `pip install -e ".[dev]"` |
| Coverage sotto soglia | test mancanti sul nuovo modulo | aggiungere test |
| Smoke test OOM | config troppo grande per il runner | usare `configs/k3-nano/smoke.yaml` |
| Benchmark in coda | runner GPU occupato | attendere o rilanciare a mano |
| Gitleaks rosso | segreto nella history | revocare la chiave e riscrivere la history |
