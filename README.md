# Script di organizzazione file e generazione HTML

Questo progetto contiene uno script (`script.py`) che:
- rinomina i file presenti nella stessa cartella (facoltativo);
- crea cartelle di output per estensione dei file;
- copia i file rinominati dentro quelle cartelle;
- genera un file `out/index.html` con una lista di `<p>` contenenti i nomi dei file.

## Devo installare pacchetti?
No. Lo script usa solo la libreria standard di Python, quindi non è necessario installare pacchetti esterni per eseguirlo.

Serve solo avere Python 3 installato sul sistema.

## Requisiti
- Python 3.8 o superiore consigliato (va bene anche 3.7+, ma meglio 3.8+).

### Come verificare la versione di Python
- macOS/Linux:
  ```bash
  python3 --version
  ```
- Windows (PowerShell o CMD):
  ```bat
  python --version
  ```
  Se non funziona, prova `py --version`.

### Come installare Python
- macOS: tramite [Homebrew](https://brew.sh/)
  ```bash
  brew install python
  ```
  Oppure scarica l’installer da https://www.python.org/downloads/

- Windows: dal Microsoft Store (cerca "Python") oppure dal sito ufficiale https://www.python.org/downloads/

- Ubuntu/Debian:
  ```bash
  sudo apt update && sudo apt install -y python3 python3-pip
  ```

## Come si usa
1. Metti `script.py` nella cartella dove si trovano i file da processare.
2. Apri un terminale nella stessa cartella.
3. Esegui:
   ```bash
   python3 script.py
   ```
   Su Windows potrebbe essere:
   ```bat
   python script.py
   ```

Lo script creerà (di default) la cartella `out/`, con sottocartelle per estensione (es. `out/jpg`, `out/pdf`, …), copierà i file dentro le relative sottocartelle e genererà `out/index.html` con l’elenco dei nomi.

### Opzioni disponibili
- `--dry-run` Mostra cosa verrebbe fatto senza modificare nulla.
- `--no-rename` Non rinominare i file sorgente.
- `--out OUTDIR` Specifica la cartella di output (default: `out`).
- `--include-hidden` Includi anche i file nascosti (che iniziano con ".").

Esempi:
```bash
# Esecuzione “a secco” (nessuna modifica):
python3 script.py --dry-run

# Non rinominare i file, ma copiare e generare HTML:
python3 script.py --no-rename

# Cambiare cartella di output:
python3 script.py --out risultato
```

## Esecuzione come file eseguibile (macOS/Linux)
Lo script ha lo shebang e può essere reso eseguibile:
```bash
chmod +x script.py
./script.py
```

## (Opzionale) Creare un eseguibile standalone
Se desideri un singolo file eseguibile (senza richiedere Python installato sulla macchina di destinazione), puoi usare [PyInstaller]. Questo è l’unico caso in cui serve installare un pacchetto esterno.

1. (Consigliato) Crea un ambiente virtuale:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   # su Windows: .venv\\Scripts\\activate
   ```
2. Installa PyInstaller:
   ```bash
   pip install pyinstaller
   ```
3. Genera l’eseguibile:
   ```bash
   pyinstaller --onefile script.py
   ```
4. Troverai l’eseguibile nella cartella `dist/`.

Note:
- Su macOS può essere necessario firmare/notarizzare l’app oppure consentire l’esecuzione da "Sicurezza e Privacy".
- L’eseguibile è specifico per il sistema operativo su cui lo generi.

## Domande frequenti (FAQ)
- Devo installare pacchetti per farlo funzionare? No, non servono pacchetti esterni.
- Perché alcuni file non vengono considerati? Lo script ignora per sicurezza se stesso, la cartella di output e le directory. Inoltre, per default ignora i file nascosti (usa `--include-hidden` per includerli).

## Risoluzione problemi
- "command not found: python3" → Installa Python o usa `python`/`py` al posto di `python3` a seconda del sistema.
- Permessi su macOS/Linux → Esegui `chmod +x script.py` oppure invoca con `python3 script.py`.

Buon lavoro!