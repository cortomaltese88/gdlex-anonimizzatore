# GD LEX Anonimizzatore

Strumento desktop PySide6 per anonimizzazione locale/offline di documenti testuali, pensato per un flusso di lavoro prudente su file `.txt` e `.docx`.

Software sviluppato da
**Marco Gianese -- STUDIO GD LEX**
Padova -- Italia

## Stato progetto

Versione repository: `v0.4.1`.

Il progetto e' utilizzabile per analisi e sostituzione locale di entita' testuali, con revisione manuale prima dell'esecuzione e generazione di report/sessioni. Resta comunque uno strumento di supporto: l'anonimizzazione non va considerata automatica, completa o garantita per ogni documento.

## Funzionalita' principali

- Elaborazione locale/offline di file `.txt` e `.docx`
- Analisi preliminare delle entita' rilevate
- Revisione manuale di valori, sostituzioni e flag `anonimizza`
- Whitelist di sessione per escludere termini dalla sostituzione
- Mapping di sessione coerente per `SOCIETA` e `PERSONA`
- Esportazione output anonimizzato nella cartella sorgente o in una cartella dedicata
- Generazione di report testuale di sessione
- Export/import della sessione in JSON

## Formati supportati

- Input: `.txt`, `.docx`
- Output: `.txt`, `.docx`, report `.txt`, sessioni `.json`

Per i file `DOCX` il progetto opera con una strategia conservativa: alcune sostituzioni possono essere saltate se il testo da anonimizzare e' spezzato su piu' run interni del documento.

## Entita' rilevate

Il rilevamento attuale copre principalmente:

- email
- codici fiscali
- partite IVA
- ragioni sociali con forme come `S.p.A.` o `S.r.l.`
- nominativi persona in alcuni pattern ricorrenti
- voci manuali aggiunte dall'utente in fase di revisione

Il riconoscimento e' basato su regole e pattern; non sostituisce una verifica umana del contenuto finale.

## Installazione

### Setup rapido

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Su Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Setup sviluppo

Per includere gli strumenti di test:

```bash
pip install -e .[dev]
```

## Avvio

Dopo l'installazione:

```bash
gdlex-anonimizzatore
```

In alternativa:

```bash
python -m gdlex_anonimizzatore.main
```

## Uso base

Flusso tipico:

1. aggiungere uno o piu' file `.txt` o `.docx` tramite pulsante o drag and drop;
2. eseguire `Analizza`;
3. rivedere le entita' trovate nella finestra di revisione;
4. modificare, disattivare o aggiungere righe manuali se necessario;
5. scegliere facoltativamente una cartella di output;
6. eseguire `Esegui`;
7. controllare i file anonimizzati e, se utile, generare il report.

L'applicazione consente anche l'import/export della sessione da menu `File`, utile per riprendere mapping e whitelist della sessione corrente.

## Sessioni e report

### Sessioni JSON

L'export di sessione genera un file JSON che puo' includere:

- mapping di sessione per societa' e persone;
- whitelist di sessione;
- valori originali, sostituzioni e flag `anonymize` delle entita' rilevate.

Questi file possono quindi contenere dati sensibili o riferimenti ai valori originali. Devono essere trattati come materiale riservato.

### Report

Il report testuale include, tra l'altro:

- riepilogo per file con esito `OK`/`WARN`/`ERR`, se disponibile;
- cartella di output;
- whitelist di sessione;
- mapping di sessione;
- elenco entita' e sostituzioni per ciascun file.

Anche il report puo' contenere dati originali o metadati sensibili e va verificato prima di archiviarlo o condividerlo.

## Limiti noti dell'anonimizzazione

- Il rilevamento e' euristico e puo' produrre falsi positivi o falsi negativi.
- I pattern persona/societa' coprono casi ricorrenti, non ogni possibile forma redazionale.
- Nei `DOCX` alcune occorrenze possono non essere sostituite se il match attraversa piu' run del documento.
- Termini istituzionali o di contesto possono influenzare il rilevamento; alcune esclusioni sono intenzionali per prudenza.
- L'app non certifica conformita' normativa, anonimizzazione irreversibile o idoneita' del risultato per uno specifico procedimento.

## Privacy e responsabilita' dell'utente

Il progetto e' orientato a un uso locale/offline, ma questo non elimina il rischio residuo derivante da:

- errori di rilevamento;
- dati sensibili presenti nei documenti sorgente;
- dati originali memorizzati in report o sessioni JSON;
- condivisione impropria di output non verificati.

Prima di usare, archiviare o condividere un documento anonimizzato, l'utente deve:

1. controllare manualmente il contenuto finale;
2. verificare che non restino riferimenti diretti o indiretti a persone, societa' o altri dati identificativi;
3. trattare con cautela report e file di sessione;
4. valutare l'adeguatezza del risultato rispetto al proprio caso d'uso.

Questo software non costituisce consulenza legale.

## Documentazione

- [docs/USO.md](docs/USO.md)
- [docs/BUILD.md](docs/BUILD.md)
- [docs/RELEASE.md](docs/RELEASE.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [SECURITY.md](SECURITY.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

## Licenza

Il codice del progetto e' distribuito con licenza **GPL-3.0-or-later**. Per il testo completo vedi [LICENSE](LICENSE).

## Dipendenze terze

Per un riepilogo sintetico delle principali dipendenze e delle relative licenze vedi [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Marchio GD LEX

La licenza GPL si applica al codice, ma non concede diritti d'uso su nome, marchio, logo o identita' visiva **GD LEX** / **STUDIO GD LEX**.

Eventuali fork o versioni modificate non possono essere presentati come ufficiali, approvati o affiliati allo Studio salvo autorizzazione separata.

Il progetto non e' affiliato, sponsorizzato o approvato da eventuali terze parti citate nelle dipendenze o nella documentazione.
