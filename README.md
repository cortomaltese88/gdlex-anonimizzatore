# GD LEX Anonimizzatore

Strumento desktop PySide6 per anonimizzazione locale/offline di documenti testuali.

Software sviluppato da\
**Marco Gianese -- STUDIO GD LEX**\
Padova -- Italia

------------------------------------------------------------------------

## Funzioni principali

- Anonimizzazione locale di file `.txt` e `.docx`
- Revisione manuale del mapping prima della sostituzione
- Generazione di report tecnico `.txt`
- Persistenza sessione tramite export/import JSON

------------------------------------------------------------------------

## Installazione

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

------------------------------------------------------------------------

## Avvio

```bash
gdlex-anonimizzatore
```

------------------------------------------------------------------------

## Note d'uso

Il software è distribuito "as is", senza garanzie di alcun tipo. L'utente resta responsabile della verifica dei documenti prodotti e dell'adeguatezza del risultato rispetto al proprio caso d'uso.

Questo software non costituisce consulenza legale.

I report generati e i file di sessione JSON possono contenere dati sensibili o riferimenti ai valori originali; vanno quindi gestiti, archiviati e condivisi con cautela.

------------------------------------------------------------------------

## Licenza

Il codice del progetto è distribuito con licenza **GPL-3.0-or-later**. Per il testo completo vedi [LICENSE](LICENSE).

La licenza GPL si applica al codice, ma non concede diritti d'uso sul nome, marchio, logo o identità visiva **GD LEX** / **STUDIO GD LEX**. Eventuali fork o versioni modificate non possono essere presentati come ufficiali, approvati o affiliati allo Studio salvo autorizzazione separata.

Il progetto non è affiliato, sponsorizzato o approvato da eventuali terze parti citate nelle dipendenze o nella documentazione.

------------------------------------------------------------------------

## Licenze terze parti

Per un riepilogo sintetico delle principali dipendenze e delle relative licenze vedi [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
