# Uso

## Avvio applicazione

Dopo l'installazione:

```bash
gdlex-anonimizzatore
```

L'app apre una GUI desktop PySide6 con tabella file, pulsanti di azione, barra di avanzamento e area log.

## Selezione file

Sono supportati file:

- `.txt`
- `.docx`

I file possono essere aggiunti tramite:

- pulsante `Aggiungi file`;
- drag and drop nella finestra.

La tabella mostra percorso file, tipo, stato, numero entita' trovate, output e relativo esito.

## Analisi

Premere `Analizza` per avviare il rilevamento preliminare.

Per ogni file l'app:

- legge il testo sorgente;
- rileva entita' supportate;
- apre una finestra di revisione manuale.

Nella finestra di revisione e' possibile:

- cambiare il testo di sostituzione;
- disattivare la singola sostituzione;
- aggiungere una riga manuale;
- rimuovere righe selezionate;
- aggiungere il valore corrente alla whitelist di sessione.

## Anonimizzazione

Dopo la revisione, premere `Esegui`.

Comportamento generale:

- i file `TXT` vengono scritti come nuovo file con suffisso `_anonimizzato`;
- i file `DOCX` vengono salvati con lo stesso suffisso nella cartella di output;
- se non e' stata scelta una cartella dedicata, l'output viene salvato accanto al file sorgente.

Se un file non e' stato prima analizzato, l'esecuzione viene saltata.

## Esportazione output e report

Con `Scegli output folder` si imposta una cartella comune di destinazione.

Con `Genera report` l'app produce un file testuale `gdlex_report_YYYYMMDD_HHMMSS.txt` che puo' includere:

- riepilogo per file con esito `OK`, `WARN` o `ERR`;
- whitelist di sessione;
- mapping di sessione;
- entita' rilevate e sostituzioni applicate o proposte.

Il report puo' contenere dati originali o riferimenti sensibili: va verificato e custodito con cautela.

## Sessioni JSON

Dal menu `File` sono disponibili:

- `Esporta sessione...`
- `Importa sessione...`

La sessione JSON puo' memorizzare:

- versione applicativa e timestamp;
- mapping `SOCIETA` e `PERSONA`;
- whitelist di sessione;
- override di sostituzione e flag `anonymize`.

Importare una sessione puo' ripristinare mapping e preferenze della sessione corrente. Anche questi file possono contenere dati sensibili.

## Cosa controllare prima di usare un documento anonimizzato

- Che tutti i nominativi sensibili previsti siano stati davvero sostituiti.
- Che non restino email, CF, partita IVA o riferimenti indiretti identificativi.
- Che i placeholder assegnati siano coerenti nel documento e nella sessione.
- Che il report e l'eventuale JSON di sessione non vengano condivisi impropriamente.
- Che il formato finale del `DOCX` resti leggibile e completo.

## Limiti noti

- Il riconoscimento e' basato su pattern e non copre tutti i casi redazionali.
- Nei `DOCX` alcune sostituzioni possono essere saltate se il testo e' spezzato su piu' run interni.
- La whitelist globale esclude alcuni termini istituzionali comuni per ridurre falsi positivi.
- La presenza di un output non equivale a una verifica privacy completa.
