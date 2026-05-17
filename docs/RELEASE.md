# Release

## Stato attuale

Il repository e' attualmente allineato alla release `v0.4.1`.

Dal workflow presente nel repository, la release GitHub viene creata su push di un tag che corrisponde al pattern `v*`.

## Workflow su tag

Il workflow `.github/workflows/release-on-tag.yml` esegue:

1. checkout del repository;
2. verifica che il tag `vX.Y.Z` corrisponda alla versione in `pyproject.toml`;
3. creazione della GitHub Release con note generate automaticamente.

Il workflow osservato non pubblica asset binari aggiuntivi.

## Controlli prima del tag

- Verificare che il working tree sia pulito.
- Verificare che `pyproject.toml` riporti la versione attesa del tag.
- Eseguire almeno i controlli locali essenziali, come `py_compile` e `pytest` se disponibile.
- Aggiornare `README.md`, `CHANGELOG.md` e `docs/` se il comportamento documentato e' cambiato.
- Verificare che non siano presenti dati reali, report reali o sessioni JSON di casi effettivi.

## Cautele operative

- Non pubblicare nei commit o nella release documenti cliente, report con dati originali o sessioni JSON sensibili.
- Non allegare asset aggiuntivi se non sono stati verificati e se non sono previsti dal processo di rilascio.
- Prima del tag, controllare che la documentazione non contenga riferimenti locali, percorsi personali o esempi con dati non sintetici.
