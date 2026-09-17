# Pipeline dati

> Il repository **non distribuisce dataset**. Qui è descritto solo il processo.

## 1. Fasi

```text
raccolta → estrazione testo → filtro lingua → filtro qualità → dedup →
rimozione PII → decontaminazione → tokenizzazione → packing → shard
```

## 2. Fonti

| Categoria | Esempi | Peso indicativo |
| --- | --- | --- |
| Web | crawl pubblici filtrati | 45% |
| Codice | repository con licenza permissiva | 20% |
| Libri e articoli | domini di pubblico dominio, preprint aperti | 15% |
| Enciclopedico | wiki multilingue | 8% |
| Matematica e scienza | dataset aperti | 7% |
| Sintetico | generato e filtrato con verifica | 5% |

## 3. Filtri di qualità

- Euristiche: lunghezza, rapporto simboli/lettere, righe duplicate, boilerplate.
- Classificatore di qualità addestrato su testo di riferimento.
- Perplexity filtering con un modello piccolo.
- Rimozione di contenuti tossici e di spam tramite classificatori dedicati.

## 4. Deduplica

- **Esatta**: hash del documento normalizzato.
- **Fuzzy**: MinHash + LSH, soglia Jaccard 0.8.
- **A livello di riga**: rimozione di blocchi ripetuti oltre soglia.

## 5. Privacy

Rilevamento e mascheramento di email, numeri di telefono, IBAN, chiavi API,
indirizzi e codici fiscali. Rispetto di `robots.txt` e delle richieste di opt-out.

## 6. Decontaminazione

Rimozione di ogni documento con overlap di 13-grammi con i benchmark usati in
`docs/evaluation.md`. Il report di decontaminazione è allegato a ogni run.

## 7. Packing

Sequenze concatenate fino alla lunghezza di contesto con maschera di documento,
così i token di un documento non attendono a quelli di un altro.
