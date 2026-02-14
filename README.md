# GDLEX Anonimizzatore

MVP desktop (PySide6) per anonimizzazione **solo file `.txt`**.

## Installazione

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## Avvio

```bash
gdlex-anonimizzatore
```

## Flusso rapido

1. Aggiungi file `.txt` (drag&drop o picker).
2. `Analizza` per trovare EMAIL / CODICE_FISCALE / PARTITA_IVA.
3. Rivedi mapping nel dialog di revisione.
4. `Esegui` per creare file `*_anonimizzato.txt`.
5. `Genera report` per esportare report `.txt`.
6. `AI assist (manuale)` per salvare versione `*_anonimizzato_ai.txt`.


## Note UX

- Supporto drag&drop file `.txt` sia sulla finestra principale sia direttamente sulla tabella file.
