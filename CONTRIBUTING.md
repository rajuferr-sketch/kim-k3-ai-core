# Contribuire a Kim K3

Grazie per l'interesse! Questo documento descrive come contribuire in modo efficace.

## 1. Preparare l'ambiente

```bash
git clone https://github.com/rajuferr-sketch/kim-k3-ai-core.git
cd kim-k3-ai-core
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## 2. Prima di aprire una PR

```bash
ruff format .
ruff check . --fix
mypy src/kimk3
pytest -q --cov=kimk3
```

Tutti e quattro i comandi devono passare.

## 3. Flusso di lavoro

1. Apri o commenta una issue prima di iniziare lavori grossi.
2. Crea un branch da `develop`: `feat/nome-breve`.
3. Commit in formato Conventional Commits.
4. Apri la PR verso `develop` compilando il template.
5. Rispondi ai commenti di review; usa `git commit --fixup` e poi squash.

## 4. Cosa NON committare

- Pesi di modelli, checkpoint, dataset.
- Chiavi API, token, file `.env`.
- File generati, cache, artefatti di build.

## 5. Aree in cui serve aiuto

- Kernel ottimizzati per il routing MoE.
- Estensione del contesto oltre 256k token.
- Nuovi tool per il layer agentico.
- Traduzione e ampliamento della documentazione.

## 6. Codice di condotta

Partecipando accetti il [Codice di condotta](CODE_OF_CONDUCT.md).
