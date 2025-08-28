#!/usr/bin/env python3
import datetime
import csv
import sys
import random
import os
import subprocess
from pathlib import Path

def _sanitize_name(name: str) -> str:
    invalid = '<>:"/\\|?*'
    sanitized = ''.join('_' if c in invalid else c for c in name)
    sanitized = sanitized.strip().rstrip(' .')
    while '  ' in sanitized:
        sanitized = sanitized.replace('  ', ' ')
    return sanitized or 'Concorso'


def _exit_requested(s: str) -> bool:
    return s.strip().lower() in {"q", "quit", "esci", "exit", "stop"}


def _input_or_exit(prompt: str) -> str:
    try:
        val = input(prompt)
    except EOFError:
        # Treat EOF as exit request
        print("\nUscita richiesta.")
        sys.exit(0)
    if _exit_requested(val):
        print("Uscita richiesta.")
        sys.exit(0)
    return val

def _open_folder(path: Path) -> None:
    try:
        if os.name == 'nt':  # Windows
            os.startfile(str(path))
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', str(path)])
        else:
            print(f"Sistema operativo non supportato per l'apertura automatica: {os.name}.")
    except Exception as e:
        print(f"Errore durante l'apertura della cartella '{path}': {e}")

def _collect_jurors() -> list[str]:
    jurors: list[str] = []
    while True:
        name = _input_or_exit("Nome giurato (lascia vuoto per terminare): ")
        if not name.strip():
            break
        clean = name.strip()
        jurors.append(clean)
    return jurors


def _collect_criteria() -> list[str]:
    criteria: list[str] = []
    placeholders = [
        "Attinenza al tema",
        "Tecnica",
        "Creatività",
        "Impressione generale",
    ]
    # First four with placeholders
    for ph in placeholders:
        ans = _input_or_exit(
            f"Inserisci criterio [{ph}] (Invio per confermare '{ph}', '-' per scartare): "
        ).strip()
        if ans == "":
            criteria.append(ph)
        elif ans == "-":
            # skip this placeholder
            continue
        else:
            criteria.append(ans)
    # Additional criteria, optional
    while True:
        more = _input_or_exit(
            "Aggiungi un altro criterio (lascia vuoto per terminare): "
        ).strip()
        if more == "":
            break
        criteria.append(more)
    return criteria


def _collect_criteria_from(placeholders: list[str]) -> list[str]:
    criteria: list[str] = []
    # Use provided placeholders in order
    for ph in placeholders:
        ans = _input_or_exit(
            f"Inserisci criterio [{ph}] (Invio per confermare '{ph}', '-' per scartare): "
        ).strip()
        if ans == "":
            criteria.append(ph)
        elif ans == "-":
            continue
        else:
            criteria.append(ans)
    # Allow adding more
    while True:
        more = _input_or_exit(
            "Aggiungi un altro criterio (lascia vuoto per terminare): "
        ).strip()
        if more == "":
            break
        criteria.append(more)
    return criteria


def _read_existing_criteria(csv_path: Path) -> list[str]:
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            first_row = next(reader, [])
            # Criteria are from second column onwards
            return [c for c in first_row[1:] if c != ""]
    except Exception:
        return []


def _read_existing_titles(csv_path: Path) -> list[str]:
    """Read titles from the first column (rows starting from the second)."""
    titles: list[str] = []
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            # skip header
            header = next(reader, None)
            for row in reader:
                if not row:
                    continue
                titles.append(row[0])
    except Exception:
        pass
    return titles


def _write_consolidated_csv(csv_path: Path, criteria: list[str], titles: list[str]) -> None:
    header = [""] + criteria
    rows = [header]
    for t in titles:
        rows.append([t] + [""] * len(criteria))
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def _extract_title_from_filename(path: Path) -> str:
    """Extract the photo title from a filename like
    nome_cognome_eventuale_secondo_nome_1_titolo_dell_immagine.jpg
    and convert it to "Titolo dell immagine".

    Rules:
    - Split stem on underscores; find the first purely numeric token; title is the rest.
    - Join title tokens with spaces.
    - Make lowercase and capitalize first letter of the whole string.
    - If pattern not matched, fallback to stem with underscores -> spaces and capitalize first letter.
    """
    stem = path.stem
    parts = stem.split("_")
    title_tokens: list[str] = []
    # Find first numeric token position
    idx = None
    for i, tok in enumerate(parts):
        if tok.isdigit():
            idx = i
            break
    if idx is not None and idx + 1 < len(parts):
        title_tokens = parts[idx + 1 :]
    else:
        title_tokens = parts
    raw = " ".join(title_tokens).strip()
    raw = raw.replace("  ", " ")
    raw = raw.lower()
    if raw:
        return raw[0].upper() + raw[1:]
    return stem.replace("_", " ")


def main() -> None:
    print("------------------------------------------------------------------")
    print("Benvenuto nello strumento di gestione concorsi fotografici!")
    print("Questo script ti aiuta a organizzare un concorso creando cartelle,")
    print("fogli di calcolo e presentazioni per i giurati e la classifica.")
    print("Segui le istruzioni passo dopo passo. Premi 'q' in qualsiasi momento per uscire.")
    print("------------------------------------------------------------------\n")
    print("### Setup del Concorso ###")
    competition_name = _input_or_exit("Inserisci il nome del concorso: ")
    safe_name = _sanitize_name(competition_name)
    year = datetime.datetime.now().year
    folder_name = f"{safe_name} {year}"

    base = Path.cwd() / folder_name

    # 1) Base folder: crea solo se non esiste
    base_existed = base.exists()
    if not base_existed:
        base.mkdir(parents=True, exist_ok=True)
        print(f"\nCreata cartella principale per il concorso: {base}")
    else:
        print(f"\nLa cartella {base} esiste già. Continuo a lavorarci.")

    _open_folder(base)

    # 2) Sottocartelle da gestire individualmente
    subfolders = ["pictures", "presentations", "spreadsheet", "leaderboard"]
    created = {}
    for sub in subfolders:
        path = base / sub
        if path.exists():
            created[sub] = False
        else:
            path.mkdir(parents=True, exist_ok=True)
            created[sub] = True
            print(f"Creata cartella: {path}")

    # 2b) Se ci sono già voti di almeno un giudice, chiedi cosa fare
    judges_dir = base / "judges"
    judge_csvs_present = bool(_find_judge_csvs(judges_dir))
    skip_leaderboard = False
    if judge_csvs_present:
        # Calcola percorso del CSV consolidato per eventuale leaderboard-only
        snake_master = _make_snake(f"{folder_name} giuria")
        spreadsheet_dir = base / "spreadsheet"
        csv_master = spreadsheet_dir / f"{snake_master}.csv"
        choice = _input_or_exit(
            "Sono presenti dei voti dei giudici. Scegli: [1] Modifica presentazione, criteri, giudici (default), "
            "[2] Crea leaderboard: "
        ).strip()
        if choice == "2":
            # Solo leaderboard
            _generate_leaderboard(base, csv_master)
            return
        else:
            # Tutte le altre operazioni, escludendo la leaderboard
            skip_leaderboard = True

    # 3) Logica specifica per 'pictures'
    pictures_path = base / "pictures"
    if created.get("pictures", False):
        # La cartella pictures non esisteva ed è stata appena creata
        print("Inserire le foto del concorso e riavviare l'eseguibile")
        return
    else:
        # La cartella pictures esisteva già: elenca file .jpg/.jpeg se presenti
        if pictures_path.exists():
            photo_paths = [p for p in pictures_path.iterdir()
                           if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg'}]
            photos = [p.name for p in photo_paths]
            if photos:
                print("\n### Foto Trovate ###")
                print("Ho trovato le seguenti foto nella cartella 'pictures':")
                for name in sorted(photos):
                    print(f"- {name}")
                print("\nOra raccogliamo i dati per i giurati e la valutazione.")
                # Proceed to jurors and criteria collection
                judges_dir = base / "judges"
                if judges_dir.exists():
                    existing_judges = [d.name for d in judges_dir.iterdir() if d.is_dir()]
                    if existing_judges:
                        print("Giurati già presenti:")
                        for j in sorted(existing_judges):
                            print(f"- {j}")
                jurors = _collect_jurors()
                # Do not block CSV synchronization if no jurors were added; just inform
                if not jurors and not (judges_dir.exists() and any(d.is_dir() for d in judges_dir.iterdir())):
                    print("Nessun giurato inserito. Procedo comunque con la gestione del CSV.")
                # Create judges directory and one subfolder per juror (only new ones)
                judges_dir.mkdir(parents=True, exist_ok=True)
                for juror in jurors:
                    juror_dir_name = _sanitize_name(juror)
                    (judges_dir / juror_dir_name).mkdir(parents=True, exist_ok=True)
                # Prepare CSV path (single consolidated CSV)
                snake = "".join(ch.lower() if ch.isalnum() else "_" for ch in f"{folder_name} giuria")
                while "__" in snake:
                    snake = snake.replace("__", "_")
                snake = snake.strip("_")
                spreadsheet_dir = base / "spreadsheet"
                spreadsheet_dir.mkdir(parents=True, exist_ok=True)
                csv_path = spreadsheet_dir / f"{snake}.csv"
                # Build current (title, path) pairs from pictures and shuffle to define spreadsheet order
                title_path_pairs = [(_extract_title_from_filename(p), p) for p in photo_paths]
                random.shuffle(title_path_pairs)
                current_titles = [t for (t, _p) in title_path_pairs]
                # If CSV already exists, read criteria and possibly modify; then sync titles and rewrite CSV
                if csv_path.exists():
                    existing_criteria = _read_existing_criteria(csv_path)
                    if existing_criteria:
                        print("Criteri attuali:")
                        for c in existing_criteria:
                            print(f"- {c}")
                    else:
                        print("Nessun criterio presente nel CSV esistente.")
                    resp = _input_or_exit("Vuoi modificarli? [s/N]: ").strip().lower()
                    if resp in {"s", "si", "sì", "y", "yes"}:
                        # User wants to modify, collect using existing criteria as placeholders
                        criteria_to_use = _collect_criteria_from(existing_criteria or [])
                    else:
                        criteria_to_use = existing_criteria
                        print("I criteri esistenti verranno mantenuti.")
                    # Compute additions/removals and print
                    old_titles = _read_existing_titles(csv_path)
                    added = [t for t in current_titles if t not in old_titles]
                    removed = [t for t in old_titles if t not in current_titles]
                    if added:
                        print("Titoli aggiunti:")
                        for t in added:
                            print(f"+ {t}")
                    if removed:
                        print("Titoli rimossi:")
                        for t in removed:
                            print(f"- {t}")
                    # Rewrite CSV with possibly updated criteria and randomized current titles
                    _write_consolidated_csv(csv_path, criteria_to_use, current_titles)
                    # Print aggiornato only if changes due to photos or criteria
                    changed_due_to_photos = bool(added or removed)
                    changed_due_to_criteria = criteria_to_use != existing_criteria
                    if changed_due_to_photos or changed_due_to_criteria:
                        print(f"Aggiornato: {csv_path}")
                    # Create/overwrite PPT if there is at least one image and either photos changed or PPT is missing
                    presentations_dir = base / "presentations"
                    presentations_dir.mkdir(parents=True, exist_ok=True)
                    snake_base = _make_snake(folder_name)
                    ppt_path = presentations_dir / f"{snake_base}.pptx"
                    need_ppt = bool(current_titles) and (changed_due_to_photos or not ppt_path.exists())
                    if need_ppt:
                        # Order slides exactly as the CSV title column
                        titles_from_csv = _read_existing_titles(csv_path)
                        ordered_pairs: list[tuple[str, Path]] = []
                        title_map = {t: p for (t, p) in title_path_pairs}
                        for t in titles_from_csv:
                            if t in title_map:
                                ordered_pairs.append((t, title_map[t]))
                        _build_ppt(ppt_path, ordered_pairs)
                        print(f"{'Aggiornata' if changed_due_to_photos else 'Creata'} presentazione: {ppt_path}")
                    if not skip_leaderboard:
                        _generate_leaderboard(base, csv_path)
                    return
                # Otherwise (no CSV yet): collect criteria and generate CSV
                criteria = _collect_criteria()
                if not criteria:
                    print("Nessun criterio inserito. Il CSV conterrà solo i titoli delle foto.")
                # Write new CSV
                _write_consolidated_csv(csv_path, criteria, current_titles)
                print(f"Creato: {csv_path}")
                # Also create the PPT (first creation implies image list change)
                if current_titles:
                    presentations_dir = base / "presentations"
                    presentations_dir.mkdir(parents=True, exist_ok=True)
                    snake_base = _make_snake(folder_name)
                    ppt_path = presentations_dir / f"{snake_base}.pptx"
                    # Order slides exactly as the CSV title column
                    titles_from_csv = _read_existing_titles(csv_path)
                    ordered_pairs: list[tuple[str, Path]] = []
                    title_map = {t: p for (t, p) in title_path_pairs}
                    for t in titles_from_csv:
                        if t in title_map:
                            ordered_pairs.append((t, title_map[t]))
                    _build_ppt(ppt_path, ordered_pairs)
                    print(f"Creata presentazione: {ppt_path}")
                if not skip_leaderboard:
                    _generate_leaderboard(base, csv_path)
                return
            else:
                # Nessun file jpg/jpeg presente: chiedi di inserire le foto
                print("\n### Attenzione: Nessuna Foto Trovata ###")
                print("Per procedere, inserisci le foto del concorso (file .jpg o .jpeg)")
                print(f"nella cartella '{pictures_path}' e riavvia lo script.")
                return
    print("\n------------------------------------------------------------------")
    print("Operazione completata con successo!")
    print("Controlla le cartelle create per il tuo concorso:")
    print(f"- **'pictures'**: contiene le foto.")
    print(f"- **'spreadsheet'**: contiene il file CSV per la valutazione.")
    print(f"- **'presentations'**: contiene la presentazione per la giuria.")
    print("\nProssimi passi:")
    print("1. Copia il file CSV dalla cartella 'spreadsheet' nella cartella di ogni giurato (es. judges/Mario_Rossi/).")
    print("2. I giurati possono inserire i loro voti nel file CSV.")
    print("3. Una volta che tutti i voti sono stati inseriti, esegui nuovamente lo script per generare la classifica finale!")
    print("------------------------------------------------------------------")

# Optional PowerPoint support
try:
    from pptx import Presentation  # type: ignore
    from pptx.util import Inches, Pt, Emu  # type: ignore
    from pptx.enum.text import PP_ALIGN  # type: ignore
    from pptx.enum.text import MSO_ANCHOR  # type: ignore
except Exception:  # pragma: no cover
    Presentation = None  # type: ignore


def _make_snake(s: str) -> str:
    snake = "".join(ch.lower() if ch.isalnum() else "_" for ch in s)
    while "__" in snake:
        snake = snake.replace("__", "_")
    return snake.strip("_")


def _build_ppt(ppt_path: Path, title_path_pairs: list[tuple[str, Path]]) -> None:
    """Create/overwrite a PPT with one slide per image in given order.
    Image fills from top without cropping; a bottom text band shows the title.
    """
    if Presentation is None:
        print("python-pptx non è installato: salto la generazione della presentazione.")
        print("Per abilitarla: pip install python-pptx")
        return

    prs = Presentation()
    # Ensure a white background (default is white; keep as is).
    blank_layout = prs.slide_layouts[6]  # blank

    # Dimensions
    slide_w = prs.slide_width
    slide_h = prs.slide_height

    # Reserve a bottom band for the title text (further reduced)
    bottom_band_h = Inches(0.25)
    top_margin = Inches(0.0)
    side_margin = Inches(0.0)

    avail_w = slide_w - 2 * side_margin
    avail_h = slide_h - bottom_band_h - top_margin

    for title, img_path in title_path_pairs:
        slide = prs.slides.add_slide(blank_layout)

        # Add picture roughly sized, then adjust to fit maintaining aspect ratio
        pic = slide.shapes.add_picture(str(img_path), left=side_margin, top=top_margin)
        # Original image size in EMU
        orig_w = pic.image.size[0]
        orig_h = pic.image.size[1]
        # Compute scale to fit into (avail_w, avail_h)
        scale_w = avail_w / orig_w
        scale_h = avail_h / orig_h
        scale = min(scale_w, scale_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        pic.width = new_w
        pic.height = new_h
        # Center horizontally within available width; keep anchored to top
        pic.left = int((slide_w - new_w) / 2)
        pic.top = top_margin  # anchored at top

        # Bottom text box with the title
        tx_left = Inches(0)
        tx_top = slide_h - bottom_band_h
        tx_width = slide_w
        tx_height = bottom_band_h
        textbox = slide.shapes.add_textbox(tx_left, tx_top, tx_width, tx_height)
        tf = textbox.text_frame
        tf.clear()
        # Center text vertically and horizontally within the band
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = title
        font = run.font
        font.size = Pt(20)
        # Default color is black; leave as black.

    prs.save(str(ppt_path))

def _extract_author_from_path(path: Path):
    stem = path.stem
    parts = stem.split("_")
    title_tokens: list[str] = []
    # Find first numeric token position
    idx = None
    for i, tok in enumerate(parts):
        if tok.isdigit():
            idx = i
            break
    if idx is not None and idx + 1 < len(parts):
        title_tokens = parts[:idx]
    else:
        title_tokens = parts
    raw = " ".join(title_tokens).strip()
    raw = raw.replace("  ", " ")
    raw = raw.lower()
    if raw:
        return raw[0].upper() + raw[1:]
    return stem.replace("_", " ")

def _build_leaderboard_ppt(ppt_path: Path, title_path_pairs: list[tuple[str, Path]]) -> None:
    if Presentation is None:
        print("python-pptx non è installato: salto la generazione della presentazione.")
        print("Per abilitarla: pip install python-pptx")
        return

    prs = Presentation()
    # Ensure a white background (default is white; keep as is).
    blank_layout = prs.slide_layouts[6]  # blank

    # Dimensions
    slide_w = prs.slide_width
    slide_h = prs.slide_height

    for title, img_path in title_path_pairs:
        title_slide = prs.slides.add_slide(blank_layout)

        textbox = title_slide.shapes.add_textbox(0, 0, slide_w, slide_h)
        tf = textbox.text_frame
        tf.clear()

        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        run1 = p1.add_run()
        run1.text = title
        font = run1.font
        font.size = Pt(44)
        font.bold = True

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        run2 = p2.add_run()
        run2.text = _extract_author_from_path(img_path)
        font2 = run2.font
        font2.size = Pt(28)
        font2.bold = False

        img_slide = prs.slides.add_slide(blank_layout)

        # Add picture roughly sized, then adjust to fit maintaining aspect ratio
        pic = img_slide.shapes.add_picture(str(img_path), 0, 0)

        img_w, img_h = pic.image.size

        scale = slide_h / img_h

        new_w = int(img_w * scale)
        new_h = slide_h

        pic.width = new_w
        pic.height = new_h

        pic.left = int((slide_w - new_w) / 2)
        pic.top = 0

    prs.save(str(ppt_path))

def _find_judge_csvs(judges_dir: Path) -> list[Path]:
    csvs: list[Path] = []
    if not judges_dir.exists():
        return csvs
    for d in judges_dir.iterdir():
        if d.is_dir():
            for f in d.iterdir():
                if f.is_file() and f.suffix.lower() == ".csv":
                    csvs.append(f)
    return csvs


def _generate_leaderboard(base: Path, master_csv: Path) -> None:
    """Generate leaderboard/classifica.csv based on judge CSVs.
    Uses criteria and titles from the consolidated spreadsheet CSV.
    """
    leaderboard_dir = base / "leaderboard"
    leaderboard_dir.mkdir(parents=True, exist_ok=True)

    judges_dir = base / "judges"
    judge_csvs = _find_judge_csvs(judges_dir)
    if not judge_csvs:
        return  # nothing to do

    criteria = _read_existing_criteria(master_csv)
    titles = _read_existing_titles(master_csv)
    if not criteria or not titles:
        return  # cannot build without structure

    from collections import defaultdict

    values: dict[tuple[str, str], list[float]] = defaultdict(list)  # (title, criterion) -> list of floats

    for jcsv in judge_csvs:
        try:
            with jcsv.open("r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, [])
                # Map criterion name -> column index in this judge CSV
                crit_to_idx: dict[str, int] = {}
                for idx, name in enumerate(header[1:], start=1):
                    if name:
                        crit_to_idx[name] = idx
                seen_titles: set[str] = set()
                for row in reader:
                    if not row:
                        continue
                    title = row[0]
                    if title not in titles:
                        # Skip unknown titles silently
                        continue
                    seen_titles.add(title)
                    for crit in criteria:
                        col = crit_to_idx.get(crit)
                        if col is None:
                            print(f"Voto mancante per titolo '{title}' criterio '{crit}' per il giudice '"
                                  f"{jcsv.parent.name}' ("
                                  f"colonna "
                                  f"assente)")
                            continue
                        cell = row[col] if col < len(row) else ""
                        if cell is None or str(cell).strip() == "":
                            print(f"Voto mancante per titolo '{title}' criterio '{crit}' per il giudice '"
                                  f"{jcsv.parent.name}'")
                            continue
                        s = str(cell).strip().replace(",", ".")
                        try:
                            num = float(s)
                        except Exception:
                            print(f"Voto non valido '{cell}' per titolo '{title}' criterio '{crit}' per il giudice '"
                                  f"{jcsv.parent.name}'")
                            continue
                        values[(title, crit)].append(num)
                # For titles not present at all in this judge CSV, count as missing per-criterion
                missing_titles = [t for t in titles if t not in seen_titles]
                for mt in missing_titles:
                    for crit in criteria:
                        print(f"Voto mancante per titolo '{mt}' criterio '{crit}' per il giudice '{jcsv.parent.name}' ("
                              f"titolo assente)")
        except Exception as e:
            print(f"Impossibile leggere il file dei voti '{jcsv}': {e}")
            continue

    # Build leaderboard rows
    out_rows: list[list[str]] = []
    header = [""] + criteria + ["Totale", "Top10"]
    out_rows.append(header)

    scored: list[tuple[str, list[str], float]] = []  # (title, cells, total)
    for title in titles:
        row_cells: list[str] = []
        criterion_means: list[float] = []
        for crit in criteria:
            nums = values.get((title, crit), [])
            if nums:
                avg = sum(nums) / len(nums)
                criterion_means.append(avg)
                row_cells.append(f"{avg:.3f}")
            else:
                row_cells.append("")
        if criterion_means:
            total = sum(criterion_means) / len(criterion_means)
        else:
            total = float('-inf')  # mark as missing for sorting; will render as blank
        scored.append((title, row_cells, total))

    # Sort by Totale desc
    scored.sort(key=lambda x: x[2], reverse=True)

    # Emit rows; render -inf as blank
    for idx, (title, cells, total) in enumerate(scored, start=1):
        total_str = "" if total == float('-inf') else f"{total:.3f}"
        out_rows.append([title] + cells + [total_str])

    leaderboard_csv = leaderboard_dir / "classifica.csv"
    try:
        with leaderboard_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(out_rows)
        # We keep prints minimal; creation is implicit.
    except Exception as e:
        print(f"Errore nella scrittura della leaderboard '{leaderboard_csv}': {e}")
    # Create pptx leaderboard if possible by taking top 10 images
    if Presentation is not None:
        top10 = [title for (title, _cells, total) in scored if total != float('-inf')][:10]
        if top10:
            title_path_map = {}
            for p in (base / "pictures").iterdir():
                if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg'}:
                    extracted_title = _extract_title_from_filename(p)
                    title_path_map[extracted_title] = p
            top10_pairs = [(t, title_path_map[t]) for t in top10 if t in title_path_map]
            if top10_pairs:
                ppt_leaderboard_path = leaderboard_dir / "classifica.pptx"
                _build_leaderboard_ppt(ppt_leaderboard_path, top10_pairs)
    else:
        print("python-pptx non è installato: salto la generazione della presentazione della classifica.")
        print("Per abilitarla: pip install python-pptx")

if __name__ == "__main__":
    main()
