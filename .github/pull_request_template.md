## Descrizione

<!-- Cosa cambia questa PR e perché. -->

Closes #

## Tipo di modifica

- [ ] 🐞 Bug fix
- [ ] ✨ Nuova funzionalità
- [ ] ⚡ Performance
- [ ] ♻️ Refactor
- [ ] 📖 Documentazione
- [ ] 🧪 Test
- [ ] 🔧 Chore / infrastruttura

## Area

- [ ] model · [ ] training · [ ] inference · [ ] data · [ ] agents · [ ] infra · [ ] docs

## Come è stato verificato

<!-- Comandi eseguiti, hardware, config usate, risultati. -->

```bash
ruff check . && mypy src/kimk3 && pytest -q
```

## Impatto su performance

| Metrica | Prima | Dopo |
| --- | --- | --- |
| Throughput (tok/s) | | |
| Memoria picco (GB) | | |
| Loss / benchmark | | |

## Checklist

- [ ] Test aggiunti o aggiornati e verdi
- [ ] Lint, format e type check verdi
- [ ] Documentazione aggiornata se cambia un'API pubblica
- [ ] Nessun peso, dataset o segreto committato
- [ ] Retrocompatibilità dei checkpoint verificata (o breaking change dichiarato)
- [ ] Commit in formato Conventional Commits

## Breaking changes

<!-- Descrivere e indicare il percorso di migrazione, oppure "Nessuno". -->
