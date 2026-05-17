# Build e ambiente

## Requisiti

- Python `>= 3.10`
- ambiente con supporto GUI per PySide6

Dipendenze dichiarate nel progetto:

- `PySide6>=6.6`
- `python-docx>=1.1`

## Virtualenv

Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

## Installazione dipendenze

Installazione standard:

```bash
pip install -e .
```

Installazione sviluppo:

```bash
pip install -e .[dev]
```

## Avvio GUI

```bash
gdlex-anonimizzatore
```

Oppure:

```bash
python -m gdlex_anonimizzatore.main
```

## Verifiche locali

Compilazione sintattica non invasiva:

```bash
python3 -m py_compile $(find src -name "*.py" | sort)
```

Se `pytest` e' disponibile:

```bash
pytest
```

## Note piattaforma

- Su Linux desktop l'app si avvia tramite Qt/PySide6 e usa una UI grafica locale.
- Su Windows serve un ambiente Python con supporto GUI e dipendenze installate correttamente.
- In ambienti headless o server-only l'avvio GUI puo' non essere disponibile o non essere utile.
