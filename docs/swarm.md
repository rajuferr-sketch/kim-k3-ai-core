# 🟪 Swarm di 15 agenti — attivazione automatica su ogni richiesta

Questo documento definisce lo **sciame di agenti** di Kim K3. Ogni richiesta dell'utente,
senza eccezioni, attiva l'intera pipeline: nessun agente è opzionale, ma ciascuno può
concludere con l'esito `skip` motivato quando non ha nulla da aggiungere.

Configurazione eseguibile: [`configs/agents/swarm.yaml`](../configs/agents/swarm.yaml)
Prompt di sistema: [`configs/agents/prompts.md`](../configs/agents/prompts.md)

---

## 1. Registro dei 15 agenti

| # | Agente | Compito | Input | Output | Permessi | Timeout | Può scrivere |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Router** | decide quali agenti e quale modello attivare, stima complessità | richiesta grezza | piano di attivazione, `complexity 1-5` | nessuno | 10s | no |
| 2 | **Coordinator** | assegna i compiti, gestisce dipendenze e budget | piano di attivazione | DAG di task | bus messaggi | 15s | sì (stato) |
| 3 | **Planner** | scompone l'obiettivo in passi e criteri di accettazione | obiettivo | lista di passi + `acceptance[]` | nessuno | 20s | no |
| 4 | **Memory** | recupera contesto, preferenze, sessioni passate; compatta | query di contesto | frammenti rilevanti | vector store, disco | 10s | sì (memoria) |
| 5 | **Research** | cerca informazioni, fonti e dati | query | passaggi + URL citabili | rete (read-only) | 30s | no |
| 6 | **Reasoning** | analisi profonda, deduzioni, ipotesi alternative | problema + fonti | catena di deduzioni | nessuno | 60s | no |
| 7 | **Data** | statistiche, dataset, tabelle, metriche | dati grezzi | tabelle + interpretazione | sandbox dati | 45s | no |
| 8 | **Coding** | scrive, modifica e verifica codice | specifica | patch + test | workspace | 120s | sì (codice) |
| 9 | **Tool** | sceglie e invoca strumenti/API esterni | intento | risultato tool | allowlist tool | 30s | dipende dal tool |
| 10 | **Executor** | esegue concretamente le azioni pianificate | piano approvato | esito azione | privilegi minimi | 120s | sì (azioni) |
| 11 | **Critic** | cerca errori, lacune, incoerenze, assunzioni non dichiarate | bozza | lista di difetti severità 1-3 | nessuno | 30s | no |
| 12 | **Verifier** | verifica fatti, calcoli e output rispetto a fonti e test | bozza + fonti | `pass`/`fail` per claim | rete read-only, sandbox | 45s | no |
| 13 | **Safety** | rischi, policy, richieste problematiche, dati personali | tutto il flusso | `allow` / `restrict` / `block` | veto | 15s | no (veto sì) |
| 14 | **Synthesizer** | fonde i contributi in un'unica risposta coerente | tutti gli output | risposta finale | nessuno | 45s | no |
| 15 | **Evaluator** | valuta la qualità finale secondo la rubrica | risposta finale | punteggio + verdetto | nessuno | 20s | no |

> Nota: l'elenco richiesto citava «10 agenti»; la pipeline completa ne conta **15**,
> perché Coordinator, Synthesizer, Executor, Safety, Evaluator e Router sono necessari
> per chiudere il ciclo. Il numero attivo per richiesta resta comunque 15.

---

## 2. Flusso di attivazione

```text
                      richiesta utente
                            │
                      ┌─────▼─────┐
                      │  ROUTER   │  complessità, modalità, modello
                      └─────┬─────┘
                      ┌─────▼──────┐
                      │COORDINATOR │  crea il DAG dei task
                      └─────┬──────┘
          ┌─────────────────┼──────────────────┐
     ┌────▼────┐       ┌────▼────┐        ┌────▼────┐
     │ PLANNER │       │ MEMORY  │        │ SAFETY  │ (veto continuo)
     └────┬────┘       └────┬────┘        └────┬────┘
          └────────┬────────┘                  │
        ── fan-out parallelo ──                │
  ┌──────────┬──────────┬──────────┬───────────┴──┐
  │ RESEARCH │ REASONING│   DATA   │  TOOL         │
  └────┬─────┴────┬─────┴────┬─────┴────┬──────────┘
       └──────────┴────┬─────┴──────────┘
                  ┌────▼────┐     ┌──────────┐
                  │ CODING  │────▶│ EXECUTOR │
                  └────┬────┘     └────┬─────┘
                       └───────┬───────┘
                        ┌──────▼──────┐
                        │   CRITIC    │
                        └──────┬──────┘
                        ┌──────▼──────┐
                        │  VERIFIER   │──fail──▶ ritorno al Coordinator (max 2 giri)
                        └──────┬──────┘
                        ┌──────▼──────┐
                        │SYNTHESIZER  │
                        └──────┬──────┘
                        ┌──────▼──────┐
                        │ EVALUATOR   │──score < 0.8──▶ un solo ciclo di riparazione
                        └──────┬──────┘
                          risposta finale
```

**Fasi:** `route → coordinate → plan+recall → gather (parallelo) → build → challenge →
verify → synthesize → score → deliver`.

---

## 3. Contratto dei messaggi sul bus

Ogni agente riceve e produce un messaggio tipizzato:

```json
{
  "request_id": "req_8f21",
  "from": "coordinator",
  "to": "research",
  "type": "task",
  "payload": {
    "goal": "trovare tre fonti primarie sul routing MoE",
    "acceptance": ["almeno 3 URL", "pubblicati dopo il 2023"]
  },
  "context_refs": ["mem:sess_44#decisioni"],
  "budget": { "calls": 6, "seconds": 30, "tokens": 20000 },
  "trust": "untrusted_input"
}
```

Risposta:

```json
{
  "request_id": "req_8f21",
  "from": "research",
  "status": "ok",
  "confidence": 0.78,
  "findings": [{ "claim": "...", "source": "https://...", "quote": "..." }],
  "open_questions": ["manca una fonte italiana"],
  "cost": { "calls": 4, "seconds": 12, "tokens": 8600 }
}
```

`status` ∈ `ok` | `partial` | `skip` | `failed` | `blocked`.
Ogni `claim` senza `source` viene marcato dal Verifier come **non verificato** e non può
comparire nella risposta finale come fatto.

---

## 4. Budget per richiesta

| Risorsa | Default | Al superamento |
| --- | --- | --- |
| Tool call totali | 40 | il Coordinator taglia gli agenti a priorità bassa |
| Tempo totale | 6 minuti | risposta parziale con stato dichiarato |
| Token totali | 800k | compattazione via Memory Agent, poi stop |
| Giri di revisione Critic↔Verifier | 2 | si consegna con i limiti dichiarati |
| Cicli di riparazione post-Evaluator | 1 | si consegna con il punteggio visibile |
| Profondità di delega | 2 | delega rifiutata |

---

## 5. Livelli di attivazione

Il Router sceglie il livello ma **tutti e 15 gli agenti vengono comunque interpellati**;
cambia la profondità del loro lavoro.

| Livello | Quando | Profondità |
| --- | --- | --- |
| `L1 lampo` | domanda fattuale breve | ogni agente in modalità minima, molti `skip` |
| `L2 standard` | richiesta normale | fan-out completo, un giro di critica |
| `L3 profondo` | problema complesso o codice | due giri, Reasoning esteso, test obbligatori |
| `L4 critico` | azioni irreversibili, dati sensibili | L3 + conferma umana + doppio Verifier |

---

## 6. Rubrica dell'Evaluator

| Criterio | Peso | Soglia |
| --- | --- | --- |
| Correttezza fattuale | 0.30 | nessun claim non verificato |
| Completezza rispetto al piano | 0.20 | tutti i passi `acceptance` coperti |
| Verificabilità (fonti o test) | 0.20 | ≥ 1 prova per affermazione non banale |
| Chiarezza e concisione | 0.15 | nessuna ripetizione |
| Sicurezza e policy | 0.10 | nessun findings Safety aperto |
| Costo rispetto al budget | 0.05 | entro il 100% |

Punteggio complessivo < **0.80** → un ciclo di riparazione mirato agli criteri falliti.

---

## 7. Sicurezza dello sciame

- **Prompt injection**: ogni contenuto raccolto da Research, Tool o Data entra nel bus
  con `trust: untrusted_input` e non può modificare obiettivi, permessi o budget.
- **Veto del Safety Agent**: può fermare l'Executor in qualsiasi momento; il suo `block`
  non è superabile dagli altri agenti.
- **Privilegio minimo**: solo Coding, Executor, Tool e Memory hanno permessi di scrittura,
  ciascuno limitato al proprio ambito.
- **Human-in-the-loop** obbligatorio per: cancellazioni, pagamenti, invii, deploy, azioni
  su sistemi esterni di produzione.
- **Audit log** per ogni messaggio del bus: agente, input hash, output hash, durata, costo,
  esito. Nessun segreto nei log.

---

## 8. Osservabilità

Traccia esportata per ogni richiesta:

```text
req_8f21  L3  15/15 agenti  38 tool call  4m12s  score 0.91
  router      0.4s  ok
  coordinator 1.1s  ok
  planner     3.8s  ok   6 passi
  memory      1.2s  ok   3 frammenti
  research   18.0s  ok   7 fonti
  reasoning  41.0s  ok
  data        9.3s  skip  nessun dataset
  coding     74.0s  ok   3 file, 12 test verdi
  tool        6.1s  ok
  executor   22.0s  ok
  critic     11.0s  ok   2 difetti sev.2
  verifier   16.0s  ok   11/11 claim verificati
  safety      2.0s  allow
  synthesizer 20.0s ok
  evaluator   5.0s  0.91
```

Metriche da monitorare: tasso di successo, numero medio di passi, costo per richiesta,
percentuale di claim verificati, difetti trovati dal Critic per 1000 token, interventi
di veto del Safety.

---

## 9. Valutazione dello sciame

| Benchmark | Cosa misura |
| --- | --- |
| τ-bench | uso di strumenti in scenari realistici |
| SWE-bench Verified | risoluzione di issue software reali |
| GAIA | ragionamento multi-step con strumenti |
| WebArena | azioni sul web |
| Suite interna `swarm-regress` | traiettorie regressive: successo, passi, costo, veto |
