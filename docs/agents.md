# Layer agentico di Kim K3

## 1. Ciclo operativo

```text
Obiettivo → Piano → Azione (tool) → Osservazione → Verifica → Sintesi
```

L'agente si ferma quando l'obiettivo è verificato, quando il budget è esaurito
o quando serve una conferma umana.

## 2. Protocollo di tool calling

Richiesta del modello:

```json
{
  "tool_calls": [
    {
      "id": "call_1",
      "type": "function",
      "function": { "name": "run_python", "arguments": "{\"code\":\"print(2+2)\"}" }
    }
  ]
}
```

Osservazione restituita:

```json
{ "role": "tool", "tool_call_id": "call_1", "content": "4" }
```

Errore restituito come dato, non come eccezione:

```json
{ "role": "tool", "tool_call_id": "call_1",
  "content": "{\"error\":\"timeout dopo 30s\",\"retryable\":true}" }
```

## 3. Registro degli strumenti

| Tool | Input | Output | Permessi | Timeout | Conferma umana |
| --- | --- | --- | --- | --- | --- |
| `search_web` | `query` | risultati + URL | rete | 20s | no |
| `read_url` | `url` | testo estratto | rete | 20s | no |
| `run_python` | `code` | stdout/stderr | sandbox senza rete | 30s | no |
| `read_file` | `path` | contenuto | workspace | 5s | no |
| `write_file` | `path`, `content` | esito | workspace | 5s | sì fuori dal workspace |
| `sql_query` | `sql` | righe | DB read-only | 15s | no |
| `shell` | `cmd` | output | allowlist | 30s | sì se distruttivo |
| `vector_search` | `query`, `k` | passaggi | store locale | 5s | no |

Ogni tool dichiara un JSON Schema; gli argomenti non validi vengono rifiutati prima
dell'esecuzione e restituiti al modello come osservazione.

## 4. Gerarchia della memoria

| Livello | Durata | Contenuto | Dove vive |
| --- | --- | --- | --- |
| Scratchpad | un turno | ragionamento intermedio | contesto, non persistito |
| Working memory | una sessione | messaggi e osservazioni | contesto, compattata all'80% |
| Episodic | tra sessioni | riassunti di sessioni passate | disco, indicizzati per data e argomento |
| Semantic | permanente | fatti, preferenze, documenti | vector store |

**Compattazione**: quando il contesto supera l'80%, i turni più vecchi vengono sostituiti
da un riassunto gerarchico che conserva obiettivi, decisioni e vincoli.

## 5. Orchestrazione multi-agente

```text
                ┌───────────┐
        ┌──────▶│  Planner  │──────┐
        │       └───────────┘      ▼
┌───────────────┐            ┌───────────┐
│  Supervisor   │◀──────────▶│Researcher │
└───────────────┘            └───────────┘
        │       ┌───────────┐      ▲
        └──────▶│   Coder   │──────┘
                └───────────┘
                      │
                ┌───────────┐
                │  Critic   │
                └───────────┘
```

Pattern supportati: **sequenziale**, **fan-out/fan-in** parallelo, **debate** tra due
agenti con un giudice, **riflessione** iterativa con il Critic.

Messaggi tipizzati sul bus:

```json
{ "from": "planner", "to": "coder", "type": "task",
  "payload": { "goal": "...", "acceptance": ["test verdi"] }, "budget": { "calls": 10 } }
```

## 6. Sicurezza

- **Prompt injection**: tutto ciò che arriva da web, file, database o output di tool è
  *dato non fidato*. Non può cambiare gli obiettivi né concedere permessi.
- **Privilegio minimo**: i permessi sono dichiarati per tool e per ruolo.
- **Human-in-the-loop**: obbligatorio per cancellazioni, pagamenti, invii, deploy.
- **Sandbox**: nessuna rete, nessun segreto, filesystem effimero, limiti di CPU e memoria.
- **Audit log**: input, output, durata, esito e costo di ogni chiamata.
- **Segreti**: mai nel prompt di sistema; risolti dall'esecutore del tool.

## 7. Budget e arresto

| Risorsa | Default | Comportamento al superamento |
| --- | --- | --- |
| Tool call | 25 per sessione | stop e riassunto dello stato |
| Tempo | 8 minuti | stop e riassunto dello stato |
| Token | 500k | compattazione, poi stop |
| Retry per tool | 3 | fallimento riportato all'utente |
| Profondità di delega | 2 | rifiuto di delegare oltre |

## 8. Valutazione

| Benchmark | Cosa misura |
| --- | --- |
| τ-bench | uso di strumenti in scenari realistici |
| SWE-bench Verified | risoluzione di issue software reali |
| WebArena | navigazione e azioni sul web |
| GAIA | ragionamento multi-step con strumenti |
| Suite interna | traiettorie regressive con tasso di successo, passi, costo, errori |

## 9. Criteri di qualità di una risposta agentica

Corretta, verificata con almeno una fonte o un test, concisa, con i limiti dichiarati
e con i passi successivi suggeriti quando il lavoro è parziale.
