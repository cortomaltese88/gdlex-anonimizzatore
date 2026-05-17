# Troubleshooting

## Dipendenze mancanti

Sintomi comuni:

- comando `gdlex-anonimizzatore` non trovato;
- errori di import all'avvio;
- GUI che non parte.

Verifiche consigliate:

- attivare il virtualenv corretto;
- reinstallare il progetto con `pip install -e .`;
- per ambiente sviluppo, usare `pip install -e .[dev]`.

## PySide6 non installato

Se compare un errore relativo a `PySide6`, l'applicazione non puo' aprire la GUI.

Azioni consigliate:

- verificare l'installazione delle dipendenze del progetto;
- controllare di stare usando l'interprete Python dell'ambiente dove il pacchetto e' stato installato.

## File DOCX non elaborato come atteso

Il supporto `DOCX` e' prudente e run-level safe.

Possibili effetti:

- alcune sostituzioni non vengono applicate;
- il report o il log possono indicare skip `cross-run`;
- il testo resta invariato in alcune occorrenze.

Questo succede tipicamente quando il contenuto da sostituire e' spezzato in piu' run interni del documento Word. In questi casi serve una verifica manuale del risultato.

## Output inatteso

Se l'output contiene sostituzioni mancanti o eccessive:

- rieseguire `Analizza`;
- controllare la finestra di revisione;
- verificare whitelist di sessione e sostituzioni manuali;
- confermare che il testo rientri nei pattern effettivamente supportati.

Il rilevamento e' euristico: alcuni casi richiedono correzione manuale.

## Sessione JSON o report

Se import/export sessione o generazione report non danno il risultato atteso:

- verificare che il file JSON sia valido;
- ricordare che l'import ripristina mapping e whitelist della sessione;
- controllare i permessi di scrittura nella cartella di destinazione;
- considerare che report e JSON possono includere dati originali e quindi vanno gestiti con cautela.

## Problemi tema o GUI

L'app usa una GUI PySide6 con tema scuro applicato via Qt.

Se la finestra appare anomala o non coerente con il sistema:

- verificare di avere un ambiente desktop funzionante;
- provare l'avvio nella stessa sessione grafica in cui si usa normalmente Python/Qt;
- escludere ambienti headless o forwarding grafico incompleto.

## Limiti dell'anonimizzazione

`gdlex-anonimizzatore` e' uno strumento di supporto, non una garanzia di anonimizzazione completa.

Controllare sempre:

- residui identificativi nel testo finale;
- coerenza dei placeholder;
- presenza di dati sensibili in report e file JSON;
- adeguatezza del risultato rispetto al contesto d'uso.
