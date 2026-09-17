# Guida al training

## 1. Pipeline a quattro stadi

| Stadio | Obiettivo | Dati | Token indicativi |
| --- | --- | --- | --- |
| 1. Pretraining | conoscenza generale | corpus multilingue deduplicato | 1-15 T |
| 2. Mid-training | codice, matematica, contesto lungo | dati curati e sintetici | 200-800 B |
| 3. SFT | seguire istruzioni, tool calling | dialoghi e traiettorie | 1-10 B |
| 4. Allineamento | preferenze, sicurezza | coppie di preferenza, reward model | 0.1-1 B |

## 2. Comandi

```bash
torchrun --nproc_per_node=8 -m kimk3.train.pretrain --config configs/k3-small/pretrain.yaml
python -m kimk3.train.sft  --config configs/k3-small/sft.yaml
python -m kimk3.train.dpo  --config configs/k3-small/dpo.yaml
python -m kimk3.train.rl   --config configs/k3-small/rl.yaml
```

## 3. Iperparametri di riferimento (`k3-small`)

| Parametro | Valore |
| --- | --- |
| Ottimizzatore | Muon (matrici) + AdamW (embedding, norm, router) |
| Learning rate | 3e-4 con warmup 2000 step |
| Scheduler | cosine fino al 10% del picco |
| Batch globale | 4 M token |
| Weight decay | 0.1 |
| Grad clip | 1.0 |
| Lunghezza sequenza | 4k → 32k (curriculum) |
| Precisione | bf16, FP8 opzionale sugli esperti |

## 4. Parallelismi

- **Data parallel**: FSDP / ZeRO-3 con sharding di parametri, gradienti e stati.
- **Tensor parallel**: dentro il nodo, per `d_model` grandi.
- **Pipeline parallel**: tra nodi, con micro-batch interleaved.
- **Expert parallel**: esperti distribuiti, all-to-all per il dispatch dei token.

Regola pratica: EP × TP ≤ GPU per nodo, PP tra i nodi, DP a coprire il resto.

## 5. Stabilità

- QK-clip sui logit dell'attenzione.
- Router in fp32 e logit del router con z-loss opzionale.
- Salto degli step con loss NaN/Inf e riavvio dall'ultimo checkpoint sano.
- Monitoraggio: loss, grad-norm, entropia del router, carico per esperto, token droppati.

## 6. Checkpoint

Formato **safetensors** con sharding, salvataggio ogni N step, retention delle ultime K
copie più checkpoint marcati. Mai `torch.load` su file non fidati.

## 7. Riproducibilità e impatto ambientale

Ogni run registra seed, commit SHA, config YAML completa, versioni delle librerie,
GPU-ora, hardware e stima di CO₂eq.
