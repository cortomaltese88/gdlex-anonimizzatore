# GDLEX Anonimizzatore

MVP desktop (PySide6) per anonimizzazione di file `.txt`.

Software sviluppato da\
**Marco Gianese -- STUDIO GD LEX**\
Padova -- Italia

------------------------------------------------------------------------

## Installazione

``` bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

------------------------------------------------------------------------

## Avvio

``` bash
gdlex-anonimizzatore
```

------------------------------------------------------------------------

## Flusso operativo

1.  Aggiungi file `.txt` (drag & drop o selettore file).
2.  Analizza per individuare:
    -   EMAIL\
    -   CODICE_FISCALE\
    -   PARTITA_IVA
3.  Verifica e modifica il mapping nel dialog di revisione.
4.  Esegui l'anonimizzazione → crea file `_anonimizzato.txt`.
5.  Genera report `.txt`.
6.  (Opzionale) AI assist manuale → salva `_anonimizzato_ai.txt`.

------------------------------------------------------------------------

## Caratteristiche attuali

-   Interfaccia desktop PySide6
-   Drag & drop diretto
-   Revisione manuale mapping
-   Generazione report tecnico
-   Persistenza sessione (export/import JSON)
-   Controlli di coerenza versione/tag

------------------------------------------------------------------------

## Stato del progetto

Progetto artigianale in evoluzione.\
Strumento pensato per uso professionale interno e condivisione tra
colleghi.

------------------------------------------------------------------------

## Licenza

© 2026 Marco Gianese -- STUDIO GD LEX

Rilasciato sotto **GDLEX Non-Commercial License**.

È consentito l'uso personale e professionale non commerciale.\
È vietato:

-   l'uso commerciale
-   la rivendita
-   la redistribuzione a fini di lucro
-   l'inclusione in software proprietario o commerciale

For full terms see the `LICENSE` file.
