# Model Card — Kim K3

## Dettagli del modello

- **Nome**: Kim K3
- **Tipo**: transformer decoder-only con strati Mixture-of-Experts sparsi
- **Sviluppo**: progetto open-source indipendente, non affiliato a Moonshot AI
- **Licenza**: Apache 2.0
- **Lingue**: multilingue, con focus su italiano, inglese, cinese e codice

## Varianti

| Variante | Totali | Attivi | Contesto | Uso previsto |
| --- | --- | --- | --- | --- |
| `k3-nano` | 1.2 B | 0.3 B | 8k | test, CI, didattica |
| `k3-small` | 8 B | 1.4 B | 32k | assistenti locali |
| `k3-base` | 64 B | 6 B | 128k | produzione generale |
| `k3-large` | 400 B | 24 B | 256k | ragionamento e agenti complessi |

## Uso previsto

Assistenza alla scrittura, generazione e revisione di codice, ragionamento,
sintesi di documenti lunghi, flussi agentici con strumenti.

## Usi non previsti

Consulenza medica, legale o finanziaria senza supervisione umana; sorveglianza;
generazione di disinformazione, contenuti illegali o materiale d'odio;
decisioni automatiche ad alto impatto senza revisione umana.

## Dati di addestramento

Corpora pubblici deduplicati, codice con licenze permissive, dati sintetici
filtrati. Il repository **non distribuisce dataset**: la pipeline in `src/kimk3/data/`
descrive filtraggio qualitativo, deduplica MinHash, rimozione PII e decontaminazione
dai benchmark.

## Valutazione

MMLU, GSM8K, MATH, HumanEval, MBPP, BBH, IFEval, LongBench, MT-Bench, τ-bench.
I risultati sono pubblicati in `docs/evaluation.md` insieme a seed e configurazioni.

## Limitazioni

- Può allucinare fatti e citazioni; verificare sempre le fonti.
- Le prestazioni calano sulle lingue a bassa risorsa.
- Il contesto molto lungo aumenta latenza e costo.
- Il routing MoE può degradare su domini molto fuori distribuzione.

## Bias e rischi

Il modello riflette i bias dei dati pubblici. Sono previsti filtri di sicurezza,
red-teaming periodico e rifiuto delle richieste dannose, ma nessuna mitigazione è completa.

## Impatto ambientale

Ogni run di training riporta in `docs/training.md` GPU-ora, hardware e stima di CO₂eq.
