# Roadmap

## 0.1 — Fondamenta (in corso)

- [x] Documentazione del repository e workflow CI
- [ ] Modello `k3-nano` addestrabile end-to-end su una singola GPU
- [ ] Tokenizer BPE con vocabolario 160k
- [ ] Test unitari su attenzione, MoE e campionamento

## 0.2 — Training scalabile

- [ ] FSDP / ZeRO-3 e expert parallel
- [ ] Checkpoint safetensors con resume affidabile
- [ ] `k3-small` pretraining completo
- [ ] Dashboard delle metriche di training

## 0.3 — Inferenza efficiente

- [ ] Paged KV-cache e continuous batching
- [ ] Server compatibile OpenAI con streaming
- [ ] Quantizzazione INT8 / INT4
- [ ] Speculative decoding con `k3-nano` come draft

## 0.4 — Contesto lungo

- [ ] YaRN fino a 128k e poi 256k token
- [ ] Prefix caching persistente
- [ ] Valutazione su LongBench

## 0.5 — Layer agentico

- [ ] Tool calling compatibile OpenAI con validazione dello schema
- [ ] Memoria episodica e semantica
- [ ] Orchestrazione multi-agente (Planner, Researcher, Coder, Critic, Supervisor)
- [ ] Valutazione su τ-bench e SWE-bench Verified

## 1.0 — Release stabile

- [ ] `k3-base` addestrato e valutato
- [ ] API pubblica congelata e retrocompatibilità dei checkpoint
- [ ] Model card completa con risultati ufficiali
- [ ] Guida al deployment in produzione

## Come contribuire alla roadmap

Apri una issue con etichetta `type:feature` e collega la voce di roadmap interessata,
oppure commenta una voce esistente per candidarti a lavorarci.
