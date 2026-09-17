# Inferenza

## 1. Uso in Python

```python
from kimk3 import KimK3

model = KimK3.from_pretrained("checkpoints/k3-small", dtype="bf16", device="cuda")
print(model.generate("Spiega la Mixture-of-Experts in tre frasi.", max_tokens=256))
```

## 2. Server compatibile OpenAI

```bash
python -m kimk3.infer.server --model checkpoints/k3-small --port 8000 --max-batch 64
```

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"k3-small","messages":[{"role":"user","content":"Ciao"}],"stream":true}'
```

Endpoint: `/v1/chat/completions`, `/v1/completions`, `/v1/models`, `/health`, `/metrics`.

## 3. Ottimizzazioni

| Tecnica | Effetto |
| --- | --- |
| Paged KV-cache | memoria frammentata, niente padding sprecato |
| Continuous batching | throughput alto con richieste eterogenee |
| Prefix caching | prompt di sistema condivisi calcolati una volta |
| Speculative decoding | draft con `k3-nano`, verifica con il modello grande |
| Chunked prefill | latenza stabile anche con prompt lunghissimi |
| Quantizzazione | INT8 / INT4 / FP8 su pesi e KV-cache |

## 4. Parametri di campionamento

`temperature`, `top_p`, `top_k`, `min_p`, `repetition_penalty`, `presence_penalty`,
`stop`, `seed`, `max_tokens`. Default consigliati: `temperature 0.6`, `top_p 0.95`.

## 5. Costo della memoria

```text
KV-cache ≈ 2 · layer · kv_heads · head_dim · seq_len · batch · bytes_per_elem
```

Con `k3-small` in bf16 a 32k token: circa 3.5 GB per sequenza. Quantizzare la cache in
INT8 la dimezza.

## 6. Deployment

- Immagine Docker con CUDA 12.1 e PyTorch 2.4.
- Health check su `/health`, metriche Prometheus su `/metrics`.
- Autoscaling sul numero di richieste in coda, non sulla CPU.
- Timeout e limite di token per richiesta sempre impostati.
