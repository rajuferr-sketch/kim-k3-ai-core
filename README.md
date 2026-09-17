# Kim K3 — AI Core

![status](https://img.shields.io/badge/status-alpha-orange)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![arch](https://img.shields.io/badge/architecture-MoE%20decoder--only-8A2BE2)
![params](https://img.shields.io/badge/parametri-800B%20totali%20%2F%2040B%20attivi-ff6f00)
![context](https://img.shields.io/badge/context-256k%20tokens-brightgreen)

> **Kim K3** è un progetto open-source indipendente che replica, in forma didattica e
> riproducibile, l'architettura di un modello linguistico di grandi dimensioni in stile
> *Kimi K2 / K3*: decoder-only, Mixture-of-Experts, addestramento a più stadi e
> capacità agentiche native (tool calling, memoria, multi-agente).
>
> 🎯 **Modello di riferimento: `k3-ultra`, 800 miliardi di parametri totali, 40 miliardi
> attivi per token.**
>
> ⚠️ **Non affiliato a Moonshot AI.** Nessun peso, dataset o codice proprietario di terzi
> è incluso in questo repository.

---

## 📚 Indice dei capitoli

| Colore | Capitolo | Contenuto |
| --- | --- | --- |
| 🟦 | [**Code**](#-code) | Architettura 800B, struttura del codice, training, inferenza, benchmark |
| 🟥 | [**Issues**](#-issues) | Template, etichette, triage, SLA, ciclo di vita, esempi compilati |
| 🟩 | [**Pull requests**](#-pull-requests) | Workflow Git, CI, review, merge policy, release |
| 🟪 | [**Agents**](#-agents) | Tool calling, memoria, sicurezza agentica, orchestrazione multi-agente |
| 🟨 | [**Actions**](#-actions) | Workflow CI/CD, matrici, runner GPU, cache, release, sicurezza della supply chain |

---

# 🟦 Code

![section](https://img.shields.io/badge/sezione-CODE-1f6feb?style=for-the-badge)

## 1. Panoramica del modello

Kim K3 è un **transformer decoder-only** con strati **Mixture-of-Experts (MoE)** sparsi.
Solo una frazione dei parametri totali è attiva per token: `k3-ultra` ha **800 B parametri
totali** ma ne attiva **circa 40 B** per token, quindi costa come un modello denso da 40 B
in inferenza pur avendo la capacità di uno da 800 B.

| Configurazione | Totali | Attivi | Layer | d_model | Teste Q / KV | Esperti | Top-k | Contesto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `k3-nano`  | 1.2 B | 0.3 B | 16 | 1024 | 16 / 8 | 8   | 2  | 8k   |
| `k3-small` | 8 B   | 1.4 B | 28 | 2048 | 32 / 8 | 16  | 2  | 32k  |
| `k3-base`  | 64 B  | 6 B   | 48 | 4096 | 32 / 8 | 64  | 4  | 128k |
| `k3-large` | 400 B | 24 B  | 72 | 7168 | 64 / 8 | 192 | 8  | 256k |
| **`k3-ultra`** | **800 B** | **40 B** | **88** | **8192** | **64 / 8** | **384** | **8** | **256k** |

### Dettaglio di `k3-ultra` (800 B)

| Voce | Valore |
| --- | --- |
| Parametri totali | ~800 B |
| Parametri attivi per token | ~40 B (5%) |
| Layer | 88 (i primi 3 densi, i restanti MoE) |
| `d_model` | 8192 |
| Teste di attenzione | 64 query, 8 KV (GQA), `head_dim` 128 |
| Esperti per layer MoE | 384 routed + 1 condiviso sempre attivo |
| Esperti attivi per token | 8 routed + 1 condiviso |
| Dimensione intermedia esperto | 2048 (SwiGLU) |
| FFN denso dei primi layer | 28672 |
| Vocabolario | 160k |
| Contesto | 128k nativo, 256k con YaRN |
| Precisione | bf16 in training, FP8 sulle matmul degli esperti |
| Memoria pesi | ~1.6 TB bf16, ~800 GB FP8, ~400 GB INT4 |

### Componenti architetturali

- **Attenzione**: Grouped-Query Attention (GQA) con 8 gruppi KV, FlashAttention-3 su Hopper/Blackwell.
- **Posizionamento**: RoPE con estensione **YaRN** per il contesto lungo (fino a 256k token).
- **Normalizzazione**: RMSNorm pre-layer, senza bias, epsilon 1e-6.
- **Attivazione**: SwiGLU nei blocchi densi e negli esperti.
- **Routing MoE**: router lineare top-8 con *auxiliary-loss-free load balancing* (bias per
  esperto aggiornato dinamicamente) e *expert capacity factor* configurabile.
- **Esperto condiviso**: 1 esperto sempre attivo per la conoscenza generale.
- **Multi-Token Prediction**: testa MTP opzionale che accelera lo speculative decoding.
- **Ottimizzatore**: Muon/AdamW ibrido con QK-clip per stabilizzare i logit dell'attenzione.

## 2. Struttura del repository

```text
kim-k3-ai-core/
├── src/kimk3/
│   ├── model/
│   │   ├── config.py          # dataclass di configurazione
│   │   ├── attention.py       # GQA + RoPE/YaRN + FlashAttention
│   │   ├── moe.py             # router, esperti, load balancing
│   │   ├── block.py           # blocco transformer
│   │   └── transformer.py     # modello completo
│   ├── tokenizer/             # BPE/tiktoken, vocab 160k
│   ├── data/                  # pipeline dati, dedup, filtraggio, packing
│   ├── train/                 # pretrain, sft, dpo, rl
│   ├── infer/                 # engine, sampling, server OpenAI-compatibile
│   ├── agents/                # tool calling, memoria, orchestrazione
│   └── eval/                  # harness di valutazione
├── configs/
│   ├── k3-nano/ k3-small/ k3-base/ k3-large/
│   └── k3-ultra/              # model.yaml, pretrain.yaml, sft.yaml, dpo.yaml
├── scripts/                   # utility CLI
├── tests/                     # unit + integration
├── docs/                      # documentazione approfondita
└── .github/                   # issue template, PR template, workflow
```

## 3. Installazione

```bash
git clone https://github.com/rajuferr-sketch/kim-k3-ai-core.git
cd kim-k3-ai-core
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Requisiti: Python 3.11+, PyTorch 2.4+, CUDA 12.1+ (opzionale per GPU).

## 4. Training

```bash
# Pretraining di k3-ultra (800B) su 64 nodi da 8 GPU
torchrun --nnodes=64 --nproc_per_node=8 \
  -m kimk3.train.pretrain --config configs/k3-ultra/pretrain.yaml

# Supervised fine-tuning
python -m kimk3.train.sft --config configs/k3-ultra/sft.yaml

# Preference optimization
python -m kimk3.train.dpo --config configs/k3-ultra/dpo.yaml
```

**Pipeline in 4 stadi**

1. **Pretraining** — corpus multilingue deduplicato, curriculum da 4k a 128k token di contesto.
2. **Mid-training** — iniezione di dati di codice, matematica e ragionamento lungo.
3. **SFT** — istruzioni, dialoghi multi-turno, traiettorie di tool calling.
4. **Allineamento** — DPO o RLHF con reward model e self-critique.

**Scala di calcolo per `k3-ultra`**: circa 15 T token, 512 GPU H100/H200,
~90 giorni, budget stimato 3.5·10²⁴ FLOP. Parallelismi: FSDP/ZeRO-3 + tensor parallel 8
+ pipeline parallel 8 + expert parallel 16.

## 5. Inferenza

```python
from kimk3 import KimK3

model = KimK3.from_pretrained("checkpoints/k3-ultra", dtype="fp8")
print(model.generate("Spiega la Mixture-of-Experts in tre frasi.", max_tokens=256))
```

Server compatibile OpenAI:

```bash
python -m kimk3.infer.server --model checkpoints/k3-ultra --tp 8 --ep 16 --port 8000
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"k3-ultra","messages":[{"role":"user","content":"Ciao"}]}'
```

Per servire 800 B servono almeno 8 GPU da 141 GB in FP8, oppure 16 GPU da 80 GB.
Ottimizzazioni: paged KV-cache, continuous batching, prefix caching, speculative decoding
con `k3-small` come draft, quantizzazione INT8/INT4/FP8.

## 6. Valutazione

```bash
python -m kimk3.eval.run --model checkpoints/k3-ultra --suite all
```

Suite incluse: MMLU, GSM8K, MATH, HumanEval, MBPP, BBH, IFEval, LongBench, τ-bench
(agentico), SWE-bench Verified, MT-Bench.

## 7. Convenzioni di codice

- Formattazione `ruff format`, lint `ruff check`, tipi `mypy --strict` sui moduli pubblici.
- Docstring in stile Google, test `pytest` per ogni modulo nuovo.
- Nessun numero magico: tutto passa da `configs/`.

📖 Approfondimenti: [`docs/architecture.md`](docs/architecture.md) ·
[`docs/training.md`](docs/training.md) · [`docs/inference.md`](docs/inference.md) ·
[`docs/evaluation.md`](docs/evaluation.md) · [`docs/data.md`](docs/data.md)

---

# 🟥 Issues

![section](https://img.shields.io/badge/sezione-ISSUES-d1242f?style=for-the-badge)

## 1. Tipi di issue disponibili

| Template | Quando usarlo | Etichette automatiche |
| --- | --- | --- |
| 🐞 **Bug report** | Errore riproducibile in training, inferenza o tooling | `type:bug`, `status:needs-triage` |
| ✨ **Feature request** | Nuova funzionalità o miglioria architetturale | `type:feature`, `status:needs-triage` |
| 🧠 **Model quality** | Risposte errate, allucinazioni, degrado su benchmark | `type:quality`, `area:model` |
| ⚡ **Performance** | Throughput, latenza, consumo memoria, costo | `type:perf` |
| 📖 **Documentation** | Documentazione mancante, errata o poco chiara | `type:docs`, `good first issue` |
| 🧪 **Reproducibility** | Un run non riproduce i numeri dichiarati | `type:quality`, `area:training` |
| 🔐 **Security** | ❌ non usare: seguire [`SECURITY.md`](SECURITY.md) | — |

## 2. Etichette ufficiali

**Tipo** · `type:bug` `type:feature` `type:docs` `type:perf` `type:quality` `type:chore`

**Area** · `area:model` `area:training` `area:inference` `area:data` `area:agents`
`area:eval` `area:infra` `area:tokenizer`

**Priorità**

| Etichetta | Significato | SLA prima risposta | SLA fix |
| --- | --- | --- | --- |
| `priority:P0` | blocca il training o la produzione | 4 ore | 24 ore |
| `priority:P1` | funzionalità principale rotta | 24 ore | 7 giorni |
| `priority:P2` | difetto con workaround | 72 ore | prossima minor |
| `priority:P3` | miglioria opzionale | best effort | backlog |

**Stato** · `status:needs-triage` `status:needs-info` `status:confirmed`
`status:in-progress` `status:blocked` `status:wontfix` `status:duplicate`

**Community** · `good first issue` `help wanted` `discussion` `breaking-change`

**Dimensione** · `size:XS` (<1h) `size:S` (<1g) `size:M` (<3g) `size:L` (<1sett) `size:XL` (>1sett)

## 3. Ciclo di vita di una issue

```text
apertura
  └─ status:needs-triage
       ├─ non riproducibile → status:needs-info ─(14 giorni senza risposta)→ chiusa stale
       ├─ duplicato        → status:duplicate → chiusa con link all'originale
       └─ valida           → status:confirmed + tipo + area + priorità + size
                                └─ assegnazione → status:in-progress
                                     ├─ dipendenza esterna → status:blocked
                                     └─ PR con "Closes #N" → merge → chiusa
```

## 4. Processo di triage

1. Ogni nuova issue nasce con `status:needs-triage`.
2. Entro **72 ore** (4 ore per le sospette P0) un maintainer assegna tipo, area, priorità e dimensione.
3. Le issue non riproducibili ricevono una richiesta di informazioni; dopo **14 giorni**
   senza risposta vengono chiuse come `stale` e possono essere riaperte.
4. Le P0 richiedono una **postmortem** in `docs/postmortems/` al momento della chiusura.
5. Triage settimanale il lunedì: revisione della coda, ri-prioritizzazione, assegnazioni.

## 5. Cosa includere sempre

- Versione del repository (commit SHA), Python, PyTorch, CUDA, driver NVIDIA.
- Hardware: modello GPU, VRAM, numero di nodi, interconnessione (NVLink/InfiniBand).
- Config YAML usata e comando esatto, incluse le variabili d'ambiente rilevanti.
- Log completo dell'errore e traceback, non solo l'ultima riga.
- Comportamento atteso vs osservato e passi minimi di riproduzione.
- Per le issue di qualità: prompt esatto, output ottenuto, output atteso, parametri di campionamento e seed.
- Per le issue di performance: comando di profiling, `nvidia-smi`, throughput misurato e atteso.

## 6. Esempio di bug report ben scritto

```markdown
**Titolo**: OOM su k3-ultra durante il pretraining con expert parallel 16

**Ambiente**: commit a1b2c3d · Python 3.11.9 · PyTorch 2.4.1 · CUDA 12.4 · 64×H100 80GB

**Comando**:
torchrun --nnodes=8 --nproc_per_node=8 -m kimk3.train.pretrain \
  --config configs/k3-ultra/pretrain.yaml

**Atteso**: il training parte e completa il primo step.
**Osservato**: CUDA out of memory allo step 1 durante l'all-to-all degli esperti.
**Traceback**: (allegato full-log.txt)
**Note**: con capacity_factor 1.0 invece di 1.25 il problema non si presenta.
```

## 7. Discussioni vs issue

Domande d'uso, idee non ancora mature e confronti architetturali vanno in
**GitHub Discussions**. Le issue restano per lavoro azionabile e tracciabile.

## 8. Sicurezza

Le vulnerabilità **non** vanno aperte come issue pubbliche: seguire [`SECURITY.md`](SECURITY.md)
e la funzione *Private Vulnerability Reporting* di GitHub.

---

# 🟩 Pull requests

![section](https://img.shields.io/badge/sezione-PULL%20REQUESTS-1a7f37?style=for-the-badge)

## 1. Workflow Git

```text
main            ← protetto, sempre verde, taggato per le release
 └── develop    ← integrazione
      ├── feat/moe-router-v2
      ├── fix/kv-cache-overflow
      └── docs/training-guide
```

Branch naming: `feat/`, `fix/`, `perf/`, `docs/`, `refactor/`, `test/`, `chore/`.

## 2. Conventional Commits

```text
feat(moe): aggiunge load balancing senza auxiliary loss
fix(infer): corregge overflow della KV-cache oltre 128k token
perf(attention): abilita FlashAttention-3 su Hopper
docs(training): aggiunge guida al parallelismo degli esperti
```

## 3. Checklist obbligatoria della PR

- [ ] La PR risolve una issue collegata (`Closes #123`).
- [ ] Test aggiunti o aggiornati, `pytest` verde in locale.
- [ ] `ruff check`, `ruff format --check`, `mypy` senza errori.
- [ ] Documentazione aggiornata se cambia un'API pubblica.
- [ ] Nessun peso, dataset o segreto committato.
- [ ] Impatto su performance misurato se si tocca il path caldo.
- [ ] Retrocompatibilità dei checkpoint verificata o breaking change dichiarato.

## 4. Continuous Integration

Il workflow [`ci.yml`](.github/workflows/ci.yml) esegue su ogni PR: lint, type check,
test con coverage (soglia 80%), smoke test su `k3-nano`, scansione di sicurezza.
Dettagli nel capitolo [Actions](#-actions).

## 5. Regole di merge

- Minimo **1 approvazione** (2 per `src/kimk3/model/` e `src/kimk3/train/`).
- Tutti i check CI verdi, branch aggiornato su `develop`.
- **Squash merge** obbligatorio, titolo in Conventional Commit.
- I `CODEOWNERS` sono richiesti automaticamente come reviewer.
- Nessun force-push su `main` o `develop`.

## 6. Review: cosa guardiamo

Correttezza numerica, stabilità del training, uso della memoria, retrocompatibilità dei
checkpoint, leggibilità, copertura dei test e assenza di regressioni sui benchmark.

## 7. Release

`main` viene taggato con SemVer (`v0.3.0`). Il workflow di release genera il changelog dai
Conventional Commit, costruisce il pacchetto e pubblica le note. Le breaking change
richiedono un incremento di minor finché siamo in `0.x`.

---

# 🟪 Agents

![section](https://img.shields.io/badge/sezione-AGENTS-8250df?style=for-the-badge)

## 1. Modello agentico

Kim K3 è progettato per operare come **agente**: pianifica, chiama strumenti, osserva i
risultati e itera fino al completamento dell'obiettivo.

```text
Utente → Pianificatore → [Tool call → Osservazione → Verifica]* → Sintesi → Risposta
```

Il ciclo si chiude quando l'obiettivo è verificato, il budget è esaurito o serve
l'intervento umano.

## 2. Tool calling

Formato compatibile OpenAI:

```json
{
  "type": "function",
  "function": {
    "name": "search_web",
    "description": "Cerca informazioni aggiornate sul web",
    "parameters": {
      "type": "object",
      "properties": { "query": { "type": "string" } },
      "required": ["query"]
    }
  }
}
```

Regole: output JSON validato contro lo schema, massimo 25 chiamate per sessione,
timeout per tool, retry con backoff esponenziale (max 3), errori restituiti al modello come
osservazione strutturata `{"error": "...", "retryable": true}` invece di interrompere la sessione.
Le chiamate indipendenti vengono eseguite in parallelo.

## 3. Strumenti di base

| Tool | Descrizione | Permessi | Timeout |
| --- | --- | --- | --- |
| `search_web` | Ricerca web con citazioni obbligatorie | rete in uscita | 20s |
| `read_url` | Estrazione del contenuto testuale di una pagina | rete in uscita | 20s |
| `run_python` | Esecuzione in sandbox isolata, senza rete | nessuno | 30s |
| `read_file` / `write_file` | Filesystem limitato al workspace | workspace | 5s |
| `sql_query` | Query in sola lettura su database whitelistati | DB read-only | 15s |
| `shell` | Comandi in allowlist, mai distruttivi senza conferma | sandbox | 30s |
| `vector_search` | Recupero dalla memoria semantica | store locale | 5s |

## 4. Memoria

- **Working memory** — finestra di contesto corrente (fino a 256k token), compattata
  automaticamente quando supera l'80% con un riassunto gerarchico.
- **Episodic memory** — riassunti delle sessioni passate salvati su disco e richiamabili per chiave.
- **Semantic memory** — vector store con embedding per il recupero di conoscenza stabile.
- **Scratchpad** — ragionamento intermedio, non mostrato all'utente e non persistito.

Politica di scrittura: si salva ciò che è una regola durevole (preferenze, vincoli,
decisioni), non i dettagli effimeri della sessione.

## 5. Orchestrazione multi-agente

| Ruolo | Responsabilità | Può scrivere |
| --- | --- | --- |
| **Planner** | Scompone l'obiettivo in sotto-task ordinati | no |
| **Researcher** | Raccoglie informazioni e cita le fonti | no |
| **Coder** | Scrive ed esegue codice, corregge gli errori | sì (workspace) |
| **Critic** | Verifica i risultati e segnala incoerenze | no |
| **Supervisor** | Coordina, applica il budget e decide quando fermarsi | sì (decisioni) |

Comunicazione tramite messaggi tipizzati su un bus condiviso; budget globale di token,
tempo e chiamate per prevenire loop infiniti. Pattern supportati: sequenziale,
fan-out/fan-in parallelo, debate, riflessione iterativa.

## 6. Sicurezza agentica

- **Prompt injection**: il contenuto recuperato da web o file è *dati*, mai istruzioni.
- **Privilegio minimo**: ogni tool riceve solo i permessi strettamente necessari.
- **Human-in-the-loop**: conferma obbligatoria per azioni distruttive o irreversibili.
- **Audit log**: ogni chiamata a tool viene registrata con input, output e timestamp.
- **Sandbox**: esecuzione di codice isolata, senza rete e senza accesso ai segreti.
- **Rate limiting** e budget per sessione su token, costo e durata.
- **Nessun segreto nel prompt**: le credenziali vivono nell'esecutore del tool, non nel contesto.

## 7. Budget di default

| Risorsa | Limite |
| --- | --- |
| Tool call per sessione | 25 |
| Durata sessione | 8 minuti |
| Token totali | configurabile (default 500k) |
| Retry per tool | 3 con backoff esponenziale |
| Profondità di delega multi-agente | 2 |

## 8. Valutazione degli agenti

τ-bench, SWE-bench Verified, WebArena, GAIA, più una suite interna di traiettorie
regressive con metriche di tasso di successo, numero di passi, costo e tasso di errore.

📖 Regole operative complete: [`AGENTS.md`](AGENTS.md) e [`docs/agents.md`](docs/agents.md)

---

# 🟨 Actions

![section](https://img.shields.io/badge/sezione-ACTIONS-bf8700?style=for-the-badge)

## 1. Workflow disponibili

| Workflow | File | Trigger | Cosa fa |
| --- | --- | --- | --- |
| **CI** | [`ci.yml`](.github/workflows/ci.yml) | push, PR | lint, tipi, test, smoke, sicurezza |
| **Docs** | [`docs.yml`](.github/workflows/docs.yml) | push su `docs/**` | link check e build della documentazione |
| **Benchmark** | [`benchmark.yml`](.github/workflows/benchmark.yml) | PR con `area:model`, notturno | valutazione su `k3-nano` e confronto con la baseline |
| **Release** | [`release.yml`](.github/workflows/release.yml) | tag `v*` | changelog, build, pubblicazione della release |
| **Stale** | [`stale.yml`](.github/workflows/stale.yml) | cron giornaliero | chiude issue e PR inattive |
| **Labeler** | [`labeler.yml`](.github/workflows/labeler.yml) | PR aperta | etichette automatiche per area |
| **CodeQL** | [`codeql.yml`](.github/workflows/codeql.yml) | push, PR, settimanale | analisi statica di sicurezza |

## 2. Struttura di un job CI

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python }}", cache: pip }
      - run: pip install -e ".[dev]"
      - run: pytest -q --cov=kimk3 --cov-report=term-missing
```

## 3. Ordine di esecuzione

```text
lint ──┐
types ─┼─→ test ─→ smoke ─→ (benchmark solo su area:model)
security ┘
```

`concurrency` con `cancel-in-progress` evita run duplicati sullo stesso branch.

## 4. Runner

| Job | Runner | Motivo |
| --- | --- | --- |
| lint, types, docs | `ubuntu-latest` | veloci e gratuiti |
| test, smoke | `ubuntu-latest` | `k3-nano` gira su CPU |
| benchmark, training di verifica | self-hosted con GPU (label `gpu-a100`) | servono CUDA e VRAM |

I runner self-hosted eseguono solo su PR provenienti dal repository, mai da fork non fidati.

## 5. Cache e tempi

- `cache: pip` su `setup-python` per le dipendenze.
- Cache dedicata per i pesi del tokenizer e i dataset di test.
- Obiettivo: CI completa in meno di 10 minuti, smoke test in meno di 5.

## 6. Segreti e permessi

- `permissions: contents: read` come default in ogni workflow; si allarga solo dove serve.
- Nessun segreto esposto ai workflow che girano su `pull_request` da fork.
- Le action di terze parti sono **pinnate al commit SHA**, non al tag mobile.
- `GITHUB_TOKEN` con il minimo privilegio necessario, mai PAT personali.

## 7. Sicurezza della supply chain

- `pip-audit` sulle dipendenze a ogni PR.
- **Gitleaks** per la ricerca di segreti nella history.
- **CodeQL** settimanale su Python.
- **Dependabot** per aggiornamenti di dipendenze e action.
- Nessun artefatto pubblicato senza checksum.

## 8. Branch protection collegata

`main` e `develop` richiedono come check obbligatori: `lint`, `types`,
`test (3.11)`, `test (3.12)`, `smoke`, `security`. Senza tutti verdi il merge è bloccato.

## 9. Esecuzione manuale

Ogni workflow espone `workflow_dispatch` per essere lanciato a mano dalla scheda Actions,
con input opzionali (per esempio la variante di modello da testare).

📖 Approfondimento: [`docs/actions.md`](docs/actions.md)

---

## 📄 Licenza

Apache License 2.0 — vedi [`LICENSE`](LICENSE).

## 🔗 Documenti collegati

[`CONTRIBUTING.md`](CONTRIBUTING.md) ·
[`AGENTS.md`](AGENTS.md) ·
[`SECURITY.md`](SECURITY.md) ·
[`MODEL_CARD.md`](MODEL_CARD.md) ·
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) ·
[`CHANGELOG.md`](CHANGELOG.md) ·
[`docs/`](docs/README.md)
