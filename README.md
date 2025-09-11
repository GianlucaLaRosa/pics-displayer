# 🚀 Orizzonti Fotografici: Guida alla Gestione Concorsi

Benvenuto\! Questo strumento è stato creato per rendere la gestione dei tuoi concorsi fotografici semplice, flessibile e automatica. Dimentica la creazione manuale di file e cartelle: questo programma si occupa di tutto, dalla preparazione dei materiali per la giuria alla classifica finale.

Segui questa guida per iniziare.

### ✨ Funzionalità Principali

  * **Gestione Completa dei Concorsi:** Crea nuovi concorsi o passa facilmente da uno all'altro senza mai chiudere il programma.
  * **Interfaccia Interattiva:** Gestisci giurati e criteri di valutazione con menu semplici e intuitivi (Aggiungi, Rinomina, Elimina).
  * **"Jury Kit" Intelligente:** Sincronizza le foto e genera un pacchetto `.zip` per la giuria contenente solo i materiali necessari (presentazione PowerPoint e foto originali).
  * **Classifica Automatica:** Calcola la classifica finale gestendo correttamente i pari merito con un sistema "denso" (es. 1°, 2°, 2°, 3°), senza saltare posizioni.
  * **Presentazione Vincitori:** Genera un file PowerPoint con i primi 10 classificati, pronto per la cerimonia di premiazione.

-----

## ✅ Download e Primo Avvio

Lo strumento è un'applicazione autonoma. Non serve installare nulla.

1.  **Scarica il File Corretto:**

      * Per **Windows**, scarica il file `.exe`.
      * Per **macOS**, scarica il file `.app` .

2.  **Primo Avvio (Importante\!):**
    Sia Windows che macOS potrebbero mostrare un avviso di sicurezza la prima volta che avvii il programma, perché non è scaricato dai loro Store ufficiali.

    ### Su Windows 🖥️

    Potrebbe apparire una schermata "Windows ha protetto il PC". Clicca su `Ulteriori informazioni` e poi su `Esegui comunque`.

    ### Su macOS 🍎

    macOS ha una protezione chiamata Gatekeeper che blocca le app non scaricate dall'App Store. Il primo avvio richiede un passaggio in più.

    **Metodo Consigliato (il più semplice):**

    1.  **Fai clic destro** (o `Ctrl`-clic) sull'icona dell'applicazione.
    2.  Seleziona **`Apri`** dal menu che appare.
    3.  Apparirà un avviso di sicurezza, ma questa volta conterrà anche un pulsante **`Apri`**. Cliccalo per confermare.
    4.  Dovrai farlo solo la prima volta; le successive potrai avviare l'app con un normale doppio clic.

    **Metodo Alternativo:**

    1.  Fai doppio clic sull'app. Apparirà un messaggio di errore. Clicca `OK`.
    2.  Vai su **`Impostazioni di Sistema`** \> **`Privacy e Sicurezza`**.
    3.  Scorri in basso fino a trovare un messaggio che dice che l'apertura di 'Orizzonti Fotografici' è stata bloccata. Clicca sul pulsante **`Apri comunque`**.

-----

## 🔢 L'Interfaccia: Menu a Numeri

Il programma è controllato tramite un semplice menu a numeri. Per fare una scelta:

1.  Digita il **numero** corrispondente all'azione che vuoi compiere.
2.  Premi il tasto **Invio** (Enter).
3.  **Suggerimento:** Dalla schermata iniziale di selezione del concorso, puoi digitare `0` per uscire direttamente dal programma.
4.  **Aiuto Online:** Dal menu di un concorso, puoi scegliere l'opzione `❓ Guida e Documentazione` per aprire questa pagina nel tuo browser.

-----

## 📸 Flusso di Lavoro: Dalla Creazione alla Classifica

### 1\. Creare o Selezionare un Concorso

1.  **Avvia il Programma:** Fai doppio clic sull'icona dell'eseguibile.
2.  **Scegli un'Azione:**
      * Per un nuovo progetto, scegli **`>> CREA NUOVO CONCORSO <<`**. Inserisci un nome e, se vuoi, una data di scadenza (`GG/MM/AAAA`).
      * Per lavorare su un progetto esistente, selezionalo dalla lista.
      * Per uscire, scegli **`🚪 Esci dal programma`** (o digita `0`).

Verrà creata automaticamente una cartella per il tuo concorso con questa struttura:

```
Nome Del Concorso/
├── 📁 judges/         # Cartelle personali dei giurati per i loro voti
├── 📁 jury_kit/        # Materiali generati (CSV master, PPTX, foto)
├── 📁 leaderboard/     # Classifica finale e PPTX dei vincitori
└── 📁 pictures/        # Qui vanno messe le foto originali del concorso
```

### 2\. Aggiungere le Foto

1.  Trova la cartella del concorso e apri la sottocartella `pictures`.
2.  **Copia al suo interno tutte le foto** che parteciperanno al concorso.

> ### ⚠️ **Importante: Come Nominare i File delle Foto**
>
> Per estrarre correttamente l'autore e il titolo, i tuoi file devono usare **due trattini `--`** come separatore:
>
>   * **Metodo Consigliato:** `Nome Autore--Titolo della Foto.jpg`
>     *(Esempio: `Mario Rossi--Tramonto a Trieste.jpg`)*
>
>   * **Metodi Alternativi:** `Nome_Autore--Titolo_della_Foto.jpg` `Nome-Autore--Titolo-della-Foto.jpg`
>
> **N.B.** Se il separatore `--` non viene trovato, l'intero nome del file verrà considerato come il titolo della foto.

### 3\. Gestire i Criteri di Valutazione

Prima di generare il materiale, devi definire le regole di valutazione.

1.  Nel menu principale, scegli **`📝 Gestisci Criteri di Valutazione`**.
2.  **Primo Avvio:** Se non ci sono criteri, lo script ti chiederà se vuoi iniziare con una lista standard (Attinenza al tema, Tecnica, ecc.).
3.  **Menu Interattivo:** Usa le opzioni per **aggiungere, rinominare o eliminare** i criteri finché non sei soddisfatto. Ogni modifica viene salvata immediatamente.

### 4\. Gestire i Giurati

1.  Nel menu principale, scegli **`🛠️ Gestisci Giurati`**.
2.  Usa il menu interattivo per **aggiungere, rinominare o eliminare** i giurati. Verrà creata una cartella per ognuno di loro.

### 5\. Generare il "Jury Kit"

Una volta impostati i criteri e aggiunte le foto, puoi creare il pacchetto per la giuria.

1.  Nel menu principale, scegli **`🔄 Genera/Aggiorna Jury Kit Completo`**.
2.  Lo script sincronizzerà le foto dalla cartella `pictures`, le combinerà con i criteri già definiti e, dopo la tua conferma, genererà:
      * Il **file master `...giuria.csv`** nella cartella `jury_kit`. Questo file serve a te per avere una traccia.
      * La **presentazione `...pptx`** con tutte le foto.
      * La cartella `original_pictures` con le copie delle immagini.
      * **Un file ZIP pronto da inviare\!** Nella cartella principale del concorso, troverai un archivio `nome-concorso_jury_kit.zip`. **Questo è l'unico file che devi inviare ai giurati.** Non contiene il file CSV.

### 6\. La Fase di Votazione

1.  **Distribuisci il Materiale:** Invia il file **`nome-concorso_jury_kit.zip`** a tutti i giurati.
2.  **Raccogli i Voti:** Ogni giurato ti restituirà il suo file `.csv` compilato.
3.  **Organizza i File Ricevuti:** Inserisci ogni `.csv` ricevuto nella cartella del rispettivo giurato (`judges/Nome_del_Giurato/`).

### 7\. Generare la Classifica Finale

1.  Nel menu principale, scegli **`🏆 Genera Classifica Finale`**.
2.  Lo script controllerà i voti e ti avviserà se ne manca qualcuno.
3.  **Risultati Pronti\!** Vai nella cartella `leaderboard` per trovare:
      * **`classifica.csv`**: La classifica completa in formato tabellare.
      * **`classifica.pptx`**: Una presentazione pronta per la proiezione con i vincitori dal 10° al 1° posto.
      * **`ordered.pptx`**: Una presentazione di tutte le foto in ordine alfabetico per autore.
      * **`random.pptx`**: Una presentazione di tutte le foto in ordine randomico, prima tutte quelle oltre al 10° posto, poi le altre.

-----

## 💡 Domande Frequenti (FAQ)

  * **Dove vengono salvati i file?**
    La prima volta che avvii il programma, verrà creata una cartella `Concorsi Orizzonti Fotografici` **nello stesso posto in cui hai eseguito il file**. Tutti i tuoi concorsi e il file di registro `ContestRegistry.json` verranno salvati al suo interno.

  * **Come passo da un concorso all'altro?**
    Nel menu principale di un concorso, scegli l'opzione **`📚 Gestisci Concorsi`**. Verrai riportato alla schermata iniziale dove potrai selezionare un altro progetto.

  * **Qual è la differenza tra "Gestisci Criteri" e "Genera Jury Kit"?**
    "Gestisci Criteri" serve a definire le **regole** di valutazione. "Genera Jury Kit" serve a prendere le foto e applicare quelle regole per **produrre i materiali** (PPT e ZIP) da dare ai giurati. È un processo in due fasi che ti dà più controllo.

  * **Perché ricevo un errore di "Accesso Negato" o "Permission Denied"?**
    Questo accade quasi sempre perché un file che lo script sta cercando di modificare (es. `classifica.csv`, `giuria.pptx`) è **attualmente aperto** sul tuo computer (in Excel, PowerPoint, ecc.). Assicurati di **chiudere tutti i file** relativi al concorso prima di eseguire un'azione nello script.

  * **Posso aggiungere o togliere foto da un concorso già avviato?**
    Sì. Aggiungi/rimuovi i file dalla cartella `pictures`, poi esegui di nuovo l'azione **`🔄 Genera/Aggiorna Jury Kit Completo`**. Lo script rileverà le modifiche e aggiornerà tutto. Ricorda di inviare il nuovo file `..._jury_kit.zip` ai giurati\!

  * **Come funziona la classifica in caso di pareggio?**
    Lo script usa un sistema di "classifica densa". Se due foto ottengono lo stesso punteggio al secondo posto, la foto successiva si classificherà al terzo posto (non al quarto). Non ci sono "salti" di posizione.