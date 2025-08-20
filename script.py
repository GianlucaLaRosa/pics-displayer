#!/usr/bin/env python3
"""
Script eseguibile per:
- rinominare i file presenti nella stessa cartella del programma (facoltativo: disattivabile),
- creare delle cartelle di output (per estensione),
- copiare i file rinominati dentro quelle cartelle,
- generare un file HTML base con una lista di <p> contenenti i nomi dei file,
- (opzionale) creare una presentazione PPTX con tutte le immagini trovate.

Uso tipico:
  python3 script.py

Opzioni:
  --dry-run           Mostra cosa verrebbe fatto senza modificare nulla.
  --no-rename         Non rinomina i file sorgente, li lascia come sono.
  --out OUTDIR        Cartella di output dove creare le sottocartelle e l'HTML (default: out).
  --include-hidden    Includi anche i file nascosti (che iniziano con ".").
  --ppt               Crea un file PPTX con le immagini trovate (richiede il pacchetto "python-pptx").
  --ppt-name NOME     Nome del file PPTX (default: images.pptx). Verrà creato nella cartella di output.

Nota: Per sicurezza, questo script ignora se stesso, la cartella di output e le directory.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff', '.webp'}


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTS


def create_ppt_from_images(out_dir: Path, image_paths: List[Path], ppt_name: str, dry_run: bool) -> Path | None:
    """Crea una presentazione PPTX con una slide per ogni immagine in image_paths.
    Richiede il pacchetto 'python-pptx'. In modalità dry-run non crea file ma stampa cosa farebbe.
    Ritorna il percorso del file PPTX creato, oppure None se non creato.
    """
    ppt_path = out_dir / ppt_name
    if dry_run:
        print(f"[DRY-RUN] Creerei un PPTX con {len(image_paths)} immagini in: {ppt_path}")
        return ppt_path
    try:
        from pptx import Presentation
        from pptx.util import Inches
    except Exception as e:
        print("Impossibile creare il PPTX: il pacchetto 'python-pptx' non è installato.")
        print("Installa con: pip install python-pptx")
        return None

    out_dir.mkdir(parents=True, exist_ok=True)

    prs = Presentation()
    blank_layout = prs.slide_layouts[6]  # layout vuoto
    slide_width = prs.slide_width
    slide_height = prs.slide_height

    for img in image_paths:
        slide = prs.slides.add_slide(blank_layout)
        # Inserisci l'immagine adattandola alla larghezza della slide, preservando proporzioni
        try:
            slide.shapes.add_picture(str(img), left=0, top=0, width=slide_width)
        except Exception as ex:
            # Se fallisce l'inserimento (formato non supportato), aggiungi slide con avviso testuale
            tx_slide = slide
            try:
                # Aggiunge una casella di testo semplice
                textbox = tx_slide.shapes.add_textbox(left=Inches(1), top=Inches(1), width=Inches(8), height=Inches(1.5))
                textbox.text_frame.text = f"Immagine non supportata: {img.name}"
            except Exception:
                pass

    prs.save(str(ppt_path))
    print(f"PPTX creato in: {ppt_path}")
    return ppt_path


def slugify_filename(name: str) -> str:
    """Normalizza un nome file (senza percorso) rendendolo più "sicuro".
    - minuscole
    - spazi e caratteri non alfanumerici -> underscore
    - riduce underscore ripetuti
    Mantiene l'estensione originale.
    """
    p = Path(name)
    stem = p.stem.lower()
    ext = p.suffix  # include il punto, es. ".txt"

    # Sostituzioni: tutto ciò che non è a-z, 0-9, trattino o underscore diventa underscore
    stem = stem.replace(" ", "_")
    stem = re.sub(r"[^a-z0-9_-]", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("._-")
    if not stem:
        stem = "file"
    return f"{stem}{ext.lower()}"


def ensure_unique(path: Path) -> Path:
    """Se il file esiste già, aggiunge un suffisso -1, -2, ... prima dell'estensione."""
    if not path.exists():
        return path
    counter = 1
    stem = path.stem
    ext = path.suffix
    parent = path.parent
    while True:
        candidate = parent / f"{stem}-{counter}{ext}"
        if not candidate.exists():
            return candidate
        counter += 1


def discover_files(base_dir: Path, out_dir: Path, include_hidden: bool) -> List[Path]:
    """Ritorna la lista dei file (non directory) nella cartella base_dir da processare.
    Esclude: script stesso, cartella out, file dentro out, directory e (di default) file nascosti.
    """
    files = []
    script_path = Path(__file__).resolve()
    for entry in base_dir.iterdir():
        # Salta la cartella di output
        if entry.resolve() == out_dir.resolve():
            continue
        # Salta directory
        if entry.is_dir():
            continue
        # Salta lo script stesso
        if entry.resolve() == script_path:
            continue
        # Salta (di default) i file nascosti
        if not include_hidden and entry.name.startswith('.'):
            continue
        files.append(entry)
    return files


def group_out_dir_for(path: Path, out_dir: Path) -> Path:
    """Ritorna la cartella di output per una data estensione."""
    ext = path.suffix.lower().lstrip('.')
    if not ext:
        ext = 'unknown'
    return out_dir / ext


def generate_html(out_dir: Path, filenames: List[str]) -> None:
    """Genera un file HTML con una lista di <p> per i nomi passati."""
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / 'index.html'
    lines = [
        '<!doctype html>',
        '<html lang="it">',
        '<head>',
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        '  <title>Elenco file</title>',
        '  <style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;margin:2rem;} p{margin:.25rem 0}</style>',
        '</head>',
        '<body>',
        '  <h1>Elenco file</h1>',
    ]
    for name in filenames:
        lines.append(f"  <p>{html.escape(name)}</p>")
    lines += ['</body>', '</html>']
    html_path.write_text("\n".join(lines), encoding='utf-8')


def rename_file(src: Path, dry_run: bool) -> Tuple[Path, str]:
    """Rinomina il file src nel suo stesso percorso usando slugify.
    Ritorna (new_path, new_name). Se dry_run è True, non cambia nulla.
    """
    new_name = slugify_filename(src.name)
    new_path = ensure_unique(src.with_name(new_name))
    if new_path == src:
        # Nessun cambiamento
        return src, src.name
    if dry_run:
        print(f"[DRY-RUN] Rinominerò: '{src.name}' -> '{new_path.name}'")
        return new_path, new_path.name
    print(f"Rinomino: '{src.name}' -> '{new_path.name}'")
    src.rename(new_path)
    return new_path, new_path.name


def copy_to_out(src: Path, out_dir: Path, dry_run: bool) -> Path:
    target_dir = group_out_dir_for(src, out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = ensure_unique(target_dir / src.name)
    if dry_run:
        print(f"[DRY-RUN] Copierei: '{src.name}' -> '{target_path}'")
        return target_path
    print(f"Copio: '{src.name}' -> '{target_path}'")
    shutil.copy2(src, target_path)
    return target_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Rinomina, organizza e indicizza i file nella cartella corrente.")
    parser.add_argument('--dry-run', action='store_true', help='Mostra le azioni senza eseguirle')
    parser.add_argument('--no-rename', action='store_true', help='Non rinomina i file sorgente')
    parser.add_argument('--out', default='out', help='Cartella di output (default: out)')
    parser.add_argument('--include-hidden', action='store_true', help='Includi file nascosti (che iniziano con .)')
    parser.add_argument('--ppt', action='store_true', help='Crea un file PPTX con le immagini trovate (richiede python-pptx)')
    parser.add_argument('--ppt-name', default='images.pptx', help='Nome del file PPTX da creare (default: images.pptx)')
    args = parser.parse_args()

    base_dir = Path.cwd()
    out_dir = (base_dir / args.out).resolve()

    print(f"Base: {base_dir}")
    print(f"Output: {out_dir}")
    if args.dry_run:
        print("Modalità DRY-RUN: nessuna modifica verrà applicata.")

    files = discover_files(base_dir, out_dir, include_hidden=args.include_hidden)
    if not files:
        print("Nessun file da processare.")
        return

    processed_names: List[str] = []

    # 1) Rinomina (se abilitato)
    renamed_paths: List[Path] = []
    for f in files:
        current = f
        if not args.no-rename:
            current, new_name = rename_file(f, dry_run=args.dry_run)
        else:
            new_name = f.name
        renamed_paths.append(current if isinstance(current, Path) else Path(current))
        processed_names.append(new_name)

    # 2) Crea cartelle e copia
    copied_paths: List[Path] = []
    for p in renamed_paths:
        dest = copy_to_out(p, out_dir, dry_run=args.dry_run)
        copied_paths.append(dest)

    # 3) Genera HTML
    generate_html(out_dir, processed_names)
    if args.dry_run:
        print(f"[DRY-RUN] Genererei HTML: {out_dir / 'index.html'}")
    else:
        print(f"HTML generato in: {out_dir / 'index.html'}")

    # 4) (Opzionale) Genera PPTX da immagini
    if args.ppt:
        images = [p for p in copied_paths if is_image_file(p)]
        if not images:
            print("Nessuna immagine trovata per creare il PPTX.")
        else:
            create_ppt_from_images(out_dir, images, args.ppt_name, dry_run=args.dry_run)


if __name__ == '__main__':
    main()