# Politica di sicurezza

## Versioni supportate

| Versione | Supporto |
| --- | --- |
| `main` | ✅ |
| tag `0.x` più recente | ✅ |
| versioni precedenti | ❌ |

## Segnalare una vulnerabilità

**Non aprire una issue pubblica.** Usa la funzione *Security → Report a vulnerability*
di GitHub (Private Vulnerability Reporting).

Includi: descrizione, impatto, passi di riproduzione, versione e ambiente,
eventuale proof-of-concept.

## Tempi di risposta

| Fase | Tempo |
| --- | --- |
| Conferma di ricezione | 48 ore |
| Valutazione iniziale | 7 giorni |
| Correzione (critica) | 30 giorni |
| Divulgazione coordinata | dopo il rilascio della patch |

## Ambito specifico dei modelli e degli agenti

Consideriamo vulnerabilità anche:

- **Prompt injection** che porta a esecuzione di tool non autorizzati.
- **Fuga di segreti** tramite output del modello o log.
- **Sandbox escape** dall'esecuzione di codice.
- **Deserializzazione insicura** di checkpoint (usare sempre `safetensors`).
- **Data poisoning** nella pipeline di training.

## Buone pratiche per chi esegue il modello

- Non passare mai segreti nel prompt di sistema.
- Eseguire i tool con privilegio minimo e in sandbox senza rete.
- Richiedere conferma umana per azioni irreversibili.
- Registrare e verificare ogni chiamata a tool.
