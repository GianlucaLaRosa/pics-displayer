# 🚀 Orizzonti Fotografici: Guida alla Gestione Concorsi

Benvenuto! Questo strumento è stato creato per rendere la gestione dei tuoi concorsi fotografici semplice e automatica. Dimentica la creazione manuale di cartelle e fogli di calcolo: questo programma si occupa di tutto, dalla preparazione dei materiali per la giuria alla classifica finale.

Segui questa guida per iniziare.

-----

## ✅ Download e Primo Avvio

Lo strumento è un'applicazione autonoma. Non serve installare nulla.

1.  **Scarica il File Corretto:**
    * Per **Windows**, scarica il file `.exe`.
    * Per **macOS**, scarica il file `.app` (o l'eseguibile fornito).

2.  **Primo Avvio (Importante!):**
    Sia Windows che macOS potrebbero mostrare un avviso di sicurezza la prima volta che avvii il programma, perché non è scaricato dai loro App Store ufficiali.
    * Su **Windows:** Potrebbe apparire una schermata "Windows ha protetto il PC". Clicca su `Ulteriori informazioni` e poi su `Esegui comunque`.
    * Su **macOS:** Potresti vedere un messaggio che dice che "l'app non può essere aperta perché proviene da uno sviluppatore non identificato". Vai in `Impostazioni di Sistema` > `Privacy e Sicurezza`, scorri in basso e troverai un pulsante per consentire l'apertura del programma. In alternativa, fai clic destro sull'icona dell'app e scegli `Apri`.

-----

## 🔢 L'Interfaccia: Menu a Numeri

Il programma è controllato tramite un semplice menu a numeri che apparirà nella finestra di comando. Per fare una scelta:

1.  Digita il **numero** corrispondente all'azione che vuoi compiere.
2.  Premi il tasto **Invio** (Enter).

È tutto qui! Non servono comandi complicati.

-----

## 📸 Flusso di Lavoro: Dalla Creazione alla Classifica

Ecco i passaggi tipici per gestire un concorso dall'inizio alla fine.

### 1. Creare un Nuovo Concorso

1.  **Avvia il Programma:** Fai doppio clic sull'icona dell'eseguibile.
2.  **Crea il Concorso:** Ti verrà presentata una lista. Scegli l'opzione **`[1] >> CREA UN NUVO CONCORSO <<`**.
3.  **Inserisci i Dettagli:**
    * **Nome:** Digita un nome per il concorso (es. "Bianco e Nero 2025") e premi Invio.
    * **Scadenza (Opzionale):** Puoi inserire una data di scadenza nel formato `GG/MM/AAAA`. Se la lasci vuota, il concorso risulterà sempre "attivo".

Verrà creata una cartella per il tuo concorso con questa struttura di base:
* `pictures` (per le foto originali)
* `judges` (per i voti dei giurati)
* `jury_kit` (dove finiranno i materiali per la giuria)
* `leaderboard` (per la classifica finale)

### 2. Aggiungere le Foto

1.  Trova la cartella del concorso che è stata appena creata.
2.  Apri la sottocartella `pictures`.
3.  **Copia al suo interno tutte le foto** che parteciperanno al concorso.

> ### ⚠️ **Importante: Come Nominare i File delle Foto**
>
> Per estrarre correttamente l'autore e il titolo, i tuoi file devono seguire una di queste convenzioni, usando **due trattini `--`** come separatore:
>
> * **Metodo Consigliato:**
>     `Nome Autore--Titolo della Foto.jpg`
>     *(Esempio: `Mario Rossi--Tramonto a Trieste.jpg`)*
>
> * **Metodi Alternativi (con `_` o `-`):**
>     `Nome_Autore--Titolo_della_Foto.jpg`
>     `nome-autore--titolo-della-foto.jpg`
>
> Lo script è flessibile e gestisce automaticamente spazi o maiuscole, ma il separatore `--` è fondamentale.

### 3. Sincronizzare e Creare il "Jury Kit"

Questa è la fase chiave, dove lo script crea un pacchetto completo per la giuria.

1.  Nel menu principale, scegli l'opzione **`🔄 Sincronizza e Crea/Aggiorna Jury Kit`**.
2.  **Definisci i Criteri:** Lo script ti chiederà di confermare o modificare i criteri di valutazione (es. "Tecnica", "Creatività").
3.  **Conferma le Modifiche:** Ti verrà mostrata un'anteprima. Dai la conferma per procedere.

Lo script genererà e aggiornerà i seguenti elementi:
* **La cartella `jury_kit`**, che ora conterrà:
    * Il foglio di calcolo `.csv` per la votazione.
    * La presentazione `.pptx` con le foto anonime.
    * Una sottocartella `original_pictures` con le foto rinominate solo con il titolo.
* **Un file ZIP pronto da inviare!** Nella cartella principale del concorso, troverai un archivio `nome-concorso_jury_kit.zip`. Questo file contiene l'intera cartella `jury_kit`, pronto per essere distribuito.

### 4. Gestire i Giurati

Puoi registrare i tuoi giurati in qualsiasi momento.

1.  Nel menu principale, scegli **`🛠️ Gestisci Giurati`**.
2.  Da qui potrai **aggiungere**, **rinominare** o **eliminare** i giurati. Per ognuno verrà creata una cartella personale dentro a `judges`.

### 5. La Fase di Votazione

Questa fase avviene al di fuori del programma.

1.  **Distribuisci il Materiale:** Invia il file **`nome-concorso_jury_kit.zip`** a tutti i giurati. Contiene tutto ciò di cui hanno bisogno per votare.
2.  **Raccogli i Voti:** Ogni giurato compilerà il file `.csv` e te lo restituirà.
3.  **Organizza i File Ricevuti:** Prendi ogni file `.csv` compilato e inseriscilo nella cartella del rispettivo giurato, che si trova in `judges/Nome_del_Giurato/`.

### 6. Generare la Classifica Finale

Quando hai raccolto i voti, sei pronto per il risultato finale.

1.  Nel menu principale, scegli **`🏆 Genera Classifica Finale`**.
2.  Lo script controllerà la presenza dei file di voto. Se mancano i voti di alcuni giurati, ti avviserà e chiederà conferma.
3.  **Risultati Pronti!** Vai nella cartella `leaderboard` per trovare:
    * **`classifica.csv`**: Il foglio di calcolo finale con tutti i punteggi e le medie.
    * **`classifica.pptx`**: Una presentazione pronta per la proiezione con le foto vincitrici.

-----

## 💡 Domande Frequenti (FAQ)
* **Posso aggiungere o togliere foto da un concorso già avviato?**
    Sì. Aggiungi/rimuovi i file dalla cartella `pictures`, poi esegui di nuovo l'azione **`🔄 Sincronizza e Crea/Aggiorna Jury Kit`**. Lo script rileverà le modifiche e aggiornerà tutto. Ricorda di inviare il nuovo file `..._jury_kit.zip` ai giurati!

* **Come cambio la data di scadenza di un concorso?**
    Nel menu principale, scegli l'opzione **`✏️ Modifica data di scadenza`**.

* **Cosa succede se rinomino una foto?**
    Lo script la vedrà come una foto rimossa e una aggiunta. Eseguendo l'azione di **Sincronizzazione**, tutto verrà aggiornato correttamente.