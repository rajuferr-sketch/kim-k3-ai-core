# Kim K3 — AI Core

![status](https://img.shields.io/badge/status-alpha-orange)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![arch](https://img.shields.io/badge/architecture-MoE%20decoder--only-8A2BE2)
![context](https://img.shields.io/badge/context-256k%20tokens-brightgreen)

> **Kim K3** è un progetto open-source indipendente che replica, in forma didattica e
> riproducibile, l'architettura di un modello linguistico di grandi dimensioni in stile
> *Kimi K2 / K3*: decoder-only, Mixture-of-Experts, addestramento a più stadi e
> capacità agentiche native (tool calling, memoria, multi-agente).
>
> ⚠️ **Non affiliato a Moonshot AI.** Nessun peso, dataset o codice proprietario di terzi
> è incluso in questo repository.

---

## 📚 Indice dei capitoli

| Colore | Capitolo | Contenuto |
| --- | --- | --- |
| 🟦 | [**Code**](#-code) | Architettura, struttura del codice, training, inferenza, benchmark |
| 🟥 | [**Issues**](#-issues) | Template, etichette, triage, ciclo di vita dei bug |
| 🟩 | [**Pull requests**](#-pull-requests) | Workflow Git, CI, review, merge policy |
| 🟪 | [**Agents**](#-agents) | Tool calling, memoria, sicurezza agentica, orchestrazione multi-agente |

---

# 🟦 Code

![section](https://img.shields.io/badge/sezione-CODE-1f6feb?style=for-the-badge)

## 1. Panoramica del modello

Kim K3 è un **transformer decoder-only** con strati **Mixture-of-Experts (MoE)** sparsi.
Solo una frazione dei parametri totali è attiva per token, il che permette di scalare la
capacità del modello senza far esplodere il costo di inferenza.

| Configurazione | Parametri totali | Parametri attivi | Layer | d_model | Esperti | Top-k | Contesto |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `k3-nano`  | 1.2 B  | 0.3 B | 16 | 1024 | 8   | 2 | 8k   |
| `k3-small` | 8 B    | 1.4 B | 28 | 2048 | 16  | 2 | 32k  |
| `k3-base`  | 64 B   | 6 B   | 48 | 4096 | 64  | 4 | 128k |
| `k3-large` | 400 B  | 24 B  | 72 | 7168 | 192 | 8 | 256k |

### Componenti architetturali

- **Attenzione**: Grouped-Query Attention (GQA) con 8 gruppi KV, FlashAttention-3 quando disponibile.
- **Posizionamento**: RoPE con estensione **YaRN** per il contesto lungo (fino a 256k token).
- **Normalizzazione**: RMSNorm pre-layer, senza bias.
- **Attivazione**: SwiGLU nei blocchi feed-forward densi e negli esperti.
- **Routing MoE**: router lineare top-k con *auxiliary-loss-free load balancing* (bias per esperto aggiornato dinamicamente) e *expert capacity factor* configurabile.
- **Esperto condiviso**: 1 esperto sempre attivo per catturare conoscenza generale.
- **Ottimizzatore**: Muon/AdamW ibrido, con QK-clip per stabilizzare i logit dell'attenzione.
- **Precisione**: bf16 in training, FP8 opzionale per le matmul degli esperti.

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
│   ├── train/
│   │   ├── pretrain.py        # pretraining
│   │   ├── sft.py             # supervised fine-tuning
│   │   ├── dpo.py             # preference optimization
│   │   └── rl.py              # RLHF / RLAIF
│   ├── infer/
│   │   ├── engine.py          # paged KV-cache, continuous batching
│   │   ├── sampling.py        # temperature, top-p, min-p, repetition
│   │   └── server.py          # API compatibile OpenAI
│   ├── agents/                # tool calling, memoria, orchestrazione
│   └── eval/                  # harness di valutazione
├── configs/                   # YAML per ogni size e ogni stadio
├── scripts/                   # utility CLI
├── tests/                     # unit + integration
├── docs/                      # documentazione approfondita
└── .github/                   # issue template, PR template, workflow CI
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
# Pretraining
torchrun --nproc_per_node=8 -m kimk3.train.pretrain --config configs/k3-small/pretrain.yaml

# Supervised fine-tuning
python -m kimk3.train.sft --config configs/k3-small/sft.yaml

# Preference optimization
python -m kimk3.train.dpo --config configs/k3-small/dpo.yaml
```

**Pipeline in 4 stadi**

1. **Pretraining** — corpus multilingue deduplicato, curriculum da 4k a 128k token di contesto.
2. **Mid-training** — iniezione di dati di codice, matematica e ragionamento lungo.
3. **SFT** — istruzioni, dialoghi multi-turno, traiettorie di tool calling.
4. **Allineamento** — DPO o RLHF con reward model e self-critique.

**Parallelismi supportati**: data parallel (FSDP/ZeRO-3), tensor parallel, pipeline parallel, expert parallel.

## 5. Inferenza

```python
from kimk3 import KimK3

model = KimK3.from_pretrained("checkpoints/k3-small")
print(model.generate("Spiega la Mixture-of-Experts in tre frasi.", max_tokens=256))
```

Server compatibile OpenAI:

```bash
python -m kimk3.infer.server --model checkpoints/k3-small --port 8000
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"k3-small","messages":[{"role":"user","content":"Ciao"}]}'
```

Ottimizzazioni: paged KV-cache, continuous batching, prefix caching, speculative decoding, quantizzazione INT8/INT4/FP8.

## 6. Valutazione

```bash
python -m kimk3.eval.run --model checkpoints/k3-small --suite all
```

Suite incluse: MMLU, GSM8K, MATH, HumanEval, MBPP, BBH, IFEval, LongBench, τ-bench (agentico), MT-Bench.

## 7. Convenzioni di codice

- Formattazione `ruff format`, lint `ruff check`, tipi `mypy --strict` sui moduli pubblici.
- Docstring in stile Google, test `pytest` per ogni modulo nuovo.
- Nessun numero magico: tutto passa da `configs/`.

---

# 🟥 Issues

![section](https://img.shields.io/badge/sezione-ISSUES-d1242f?style=for-the-badge)

## 1. Tipi di issue disponibili

| Template | Quando usarlo |
| --- | --- |
| 🐞 **Bug report** | Errore riproducibile in training, inferenza o tooling |
| ✨ **Feature request** | Nuova funzionalità o miglioria architetturale |
| 🧠 **Model quality** | Risposte errate, allucinazioni, degrado su benchmark |
| ⚡ **Performance** | Throughput, latenza, consumo memoria |
| 📖 **Documentation** | Documentazione mancante, errata o poco chiara |

## 2. Etichette ufficiali

| Etichetta | Significato |
| --- | --- |
| `type:bug` / `type:feature` / `type:docs` / `type:perf` / `type:quality` | Categoria |
| `area:model` / `area:training` / `area:inference` / `area:data` / `area:agents` / `area:infra` | Area tecnica |
| `priority:P0` … `P3` | P0 = blocca tutto, P3 = miglioria opzionale |
| `status:needs-triage` / `confirmed` / `in-progress` / `blocked` | Stato |
| `good first issue`, `help wanted` | Per i nuovi contributor |

## 3. Processo di triage

1. Ogni nuova issue nasce con `status:needs-triage`.
2. Entro **72 ore** un maintainer assegna tipo, area e priorità.
3. Le issue non riproducibili ricevono una richiesta di informazioni; dopo **14 giorni** senza risposta vengono chiuse come `stale`.
4. Le P0 hanno SLA di **24 ore** e richiedono una postmortem al momento della chiusura.

## 4. Cosa includere sempre

- Versione del repository (commit SHA), Python, PyTorch, CUDA, driver.
- Hardware (GPU, VRAM, numero di nodi).
- Config YAML usata e comando esatto.
- Log completo dell'errore e traceback.
- Comportamento atteso vs osservato, passi minimi di riproduzione.

## 5. Sicurezza

Le vulnerabilità **non** vanno aperte come issue pubbliche: seguire [`SECURITY.md`](SECURITY.md).

---

# 🟩 Pull requests

![section](https://img.shields.io/badge/sezione-PULL%20REQUESTS-1a7f37?style=for-the-badge)

## 1. Workflow Git

```text
main            ← protetto, sempre verde
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

## 4. Continuous Integration

Il workflow [`ci.yml`](.github/workflows/ci.yml) esegue su ogni PR:

1. **lint** — ruff check + format check
2. **types** — mypy
3. **test** — pytest con coverage (soglia minima 80%)
4. **smoke** — training di 10 step + generazione di 32 token su `k3-nano`
5. **security** — scansione dipendenze e ricerca di segreti

## 5. Regole di merge

- Minimo **1 approvazione** (2 per `src/kimk3/model/` e `src/kimk3/train/`).
- Tutti i check CI verdi, branch aggiornato su `develop`.
- **Squash merge** obbligatorio, titolo in Conventional Commit.
- I `CODEOWNERS` sono richiesti automaticamente come reviewer.
- Nessun force-push su `main` o `develop`.

## 6. Review: cosa guardiamo

Correttezza numerica, stabilità del training, uso della memoria, retrocompatibilità dei
checkpoint, leggibilità, copertura dei test e assenza di regressioni sui benchmark.

---

# 🟪 Agents

![section](https://img.shields.io/badge/sezione-AGENTS-8250df?style=for-the-badge)

## 1. Modello agentico

Kim K3 è progettato per operare come **agente**: pianifica, chiama strumenti, osserva i
risultati e itera fino al completamento dell'obiettivo.

```text
Utente → Pianificatore → [Tool call → Osservazione]* → Sintesi → Risposta
```

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
timeout per tool, retry con backoff esponenziale, errori restituiti al modello come
osservazione strutturata invece di interrompere la sessione.

## 3. Strumenti di base

| Tool | Descrizione |
| --- | --- |
| `search_web` | Ricerca web con citazioni obbligatorie |
| `read_url` | Estrazione del contenuto testuale di una pagina |
| `run_python` | Esecuzione in sandbox isolata, senza rete, timeout 30s |
| `read_file` / `write_file` | Accesso al filesystem limitato al workspace |
| `sql_query` | Query in sola lettura su database whitelistati |

## 4. Memoria

- **Working memory** — finestra di contesto corrente, compattata quando supera l'80%.
- **Episodic memory** — riassunti delle sessioni passate, salvati su disco.
- **Semantic memory** — vector store con embedding per il recupero di conoscenza.
- **Scratchpad** — ragionamento intermedio, non mostrato all'utente.

## 5. Orchestrazione multi-agente

| Ruolo | Responsabilità |
| --- | --- |
| **Planner** | Scompone l'obiettivo in sotto-task ordinati |
| **Researcher** | Raccoglie informazioni e cita le fonti |
| **Coder** | Scrive ed esegue codice, corregge gli errori |
| **Critic** | Verifica i risultati e segnala incoerenze |
| **Supervisor** | Coordina, applica il budget e decide quando fermarsi |

Comunicazione tramite messaggi tipizzati su un bus condiviso; budget globale di token,
tempo e chiamate per prevenire loop infiniti.

## 6. Sicurezza agentica

- **Prompt injection**: il contenuto recuperato da web o file è *dati*, mai istruzioni.
- **Privilegio minimo**: ogni tool riceve solo i permessi strettamente necessari.
- **Human-in-the-loop**: conferma obbligatoria per azioni distruttive o irreversibili.
- **Audit log**: ogni chiamata a tool viene registrata con input, output e timestamp.
- **Sandbox**: esecuzione di codice isolata, senza rete e senza accesso ai segreti.
- **Rate limiting** e budget per sessione su token, costo e durata.

## 7. Valutazione degli agenti

τ-bench, SWE-bench Verified, WebArena, GAIA, più una suite interna di traiettorie
regressive con metriche di tasso di successo, numero di passi, costo e tasso di errore.

---

## 📄 Licenza

Apache License 2.0 — vedi [`LICENSE`](LICENSE).

## 🔗 Documenti collegati

[`CONTRIBUTING.md`](CONTRIBUTING.md) ·
[`AGENTS.md`](AGENTS.md) ·
[`SECURITY.md`](SECURITY.md) ·
[`MODEL_CARD.md`](MODEL_CARD.md) ·
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) ·
[`CHANGELOG.md`](CHANGELOG.md)
