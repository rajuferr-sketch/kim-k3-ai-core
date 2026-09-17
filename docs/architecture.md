# Architettura di Kim K3

## 1. Visione d'insieme

Kim K3 è un transformer **decoder-only** con strati **Mixture-of-Experts (MoE)** sparsi.
Ogni token attiva solo una frazione dei parametri totali: la capacità cresce senza far
esplodere il costo di inferenza.

```text
token → embedding → [ RMSNorm → GQA(RoPE/YaRN) → RMSNorm → MoE/FFN ] × L → RMSNorm → lm_head
```

## 2. Configurazioni

| Variante | Totali | Attivi | Layer | d_model | Teste Q / KV | Esperti | Top-k | Contesto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `k3-nano`  | 1.2 B | 0.3 B | 16 | 1024 | 16 / 8 | 8   | 2 | 8k   |
| `k3-small` | 8 B   | 1.4 B | 28 | 2048 | 32 / 8 | 16  | 2 | 32k  |
| `k3-base`  | 64 B  | 6 B   | 48 | 4096 | 32 / 8 | 64  | 4 | 128k |
| `k3-large` | 400 B | 24 B  | 72 | 7168 | 64 / 8 | 192 | 8 | 256k |

## 3. Attenzione

- **Grouped-Query Attention (GQA)** con 8 gruppi KV: riduce la KV-cache di 4-8×.
- **RoPE** con base 10000, esteso con **YaRN** (scaling non uniforme delle frequenze)
  per arrivare fino a 256k token senza ri-addestrare da zero.
- **FlashAttention-3** quando disponibile (Hopper), fallback su SDPA di PyTorch.
- **QK-clip**: clamp dei logit dell'attenzione per evitare divergenze in bf16.

## 4. Strato MoE

- Router lineare `d_model → n_experts`, selezione **top-k** con softmax sui soli esperti scelti.
- **Load balancing senza auxiliary loss**: un bias per esperto viene aggiornato
  dinamicamente in base al carico osservato, senza inquinare il gradiente principale.
- **Capacity factor** configurabile (default 1.25); i token in eccesso vengono droppati
  verso il residuo.
- **Esperto condiviso**: 1 esperto sempre attivo che cattura la conoscenza generale.
- Esperti con attivazione **SwiGLU**, dimensione intermedia `8/3 · d_model` arrotondata a multipli di 256.

## 5. Normalizzazione e precisione

- **RMSNorm** pre-layer, senza bias, epsilon 1e-6.
- **bf16** per il training, **FP8** opzionale per le matmul degli esperti.
- Pesi del router sempre in fp32 per stabilità numerica.

## 6. Tokenizer

BPE in stile tiktoken, vocabolario 160k, token speciali per ruoli di chat,
tool calling e delimitatori di ragionamento.

## 7. Scelte progettuali e alternative scartate

| Scelta | Motivo | Alternativa scartata |
| --- | --- | --- |
| GQA | miglior rapporto qualità/KV-cache | MQA (perdita di qualità), MHA (cache enorme) |
| MoE sparso | capacità a costo costante | denso (costo lineare nei parametri) |
| YaRN | estensione contesto economica | training diretto a 256k (costo proibitivo) |
| Bias di bilanciamento | nessuna interferenza col gradiente | auxiliary loss classica |
