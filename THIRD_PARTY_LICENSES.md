# Third-Party Licenses

Riepilogo prudente delle principali dipendenze e componenti citati nel progetto.

| Componente | Ruolo | Licenza | Note |
| --- | --- | --- | --- |
| Python | Runtime esterno | PSF License | Verificato localmente a livello di runtime Python; non incluso automaticamente nel repository. |
| PySide6 | GUI/runtime | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | Verificato localmente. PySide6 non impone di per sé la GPL sul progetto; questo repository sceglie GPL-3.0-or-later per policy di distribuzione. |
| python-docx | Supporto DOCX | MIT | Verificato localmente. |
| lxml | Dipendenza indiretta/probabile per gestione XML/DOCX | BSD-3-Clause | Verificato localmente. |
| pytest | Dev/test | da verificare | Metadata non disponibili localmente nell'ambiente ispezionato durante questo audit. |

## Note

- Le dipendenze installate dall'utente mantengono le rispettive licenze.
- Prima di distribuire binari o bundle che includano materialmente dipendenze terze sarà necessario includere licenze, notice e attribuzioni adeguate secondo i termini applicabili.
- Nome, logo, marchio e identità visiva **GD LEX** / **STUDIO GD LEX** restano distinti dalla licenza del codice e non sono concessi dalla GPL salvo autorizzazione separata.
