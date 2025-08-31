#!/usr/bin/env python3
import datetime
import csv
import sys
import random
import os
import subprocess
import re
import shutil
import json
from pathlib import Path
from collections import defaultdict

# --- Gestione codifica su Windows ---
if sys.platform == 'win32':
    try:
        # Tenta di cambiare la codifica del terminale per supportare UTF-8
        import subprocess

        subprocess.run(['chcp', '65001'], check=True, capture_output=True, text=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    except FileNotFoundError:
        # chcp potrebbe non essere disponibile o non riuscire
        pass

# --- IMPOSTAZIONE SEPARATORE ---
FILENAME_SEPARATOR = "--"

# Tentativo di importare 'inquirer'. Se non riesce, useremo un fallback.
try:
    if not sys.stdout.isatty():
        raise ImportError("Non è un terminale interattivo, fallback a input standard.")
    import inquirer
except ImportError:
    inquirer = None

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
except ImportError:
    Presentation = None


# --- FUNZIONI DI UTILITÀ E INPUT ---

def _sanitize_name(name: str) -> str:
    invalid = '<>:"/\\|?*'
    sanitized = ''.join('_' if c in invalid else c for c in name)
    sanitized = sanitized.strip().rstrip(' .')
    while '  ' in sanitized:
        sanitized = sanitized.replace('  ', ' ')
    return sanitized or 'Senza_Nome'


def _exit_requested(s: str) -> bool:
    return s.strip().lower() in {"q", "quit", "esci", "exit", "stop"}


def _input_or_exit(prompt: str) -> str:
    try:
        val = input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nUscita richiesta.")
        sys.exit(0)
    if _exit_requested(val):
        print("Uscita richiesta.")
        sys.exit(0)
    return val


def _confirm_or_exit(message: str, default: bool = False) -> bool:
    if inquirer:
        full_message = f"{message.strip()} (premi Ctrl+C per uscire)"
        questions = [inquirer.Confirm('confirm', message=full_message, default=default)]
        try:
            answers = inquirer.prompt(questions)
            if answers is None: sys.exit(0)
            return answers['confirm']
        except (KeyboardInterrupt, EOFError):
            print("\nUscita richiesta.");
            sys.exit(0)
    else:
        prompt = f"{message.strip()} [s/n]: "
        resp = _input_or_exit(prompt).strip().lower()
        if resp == "": return default
        return resp in {"s", "si", "sì", "y", "yes"}


def _open_folder(path: Path) -> None:
    try:
        if os.name == 'nt':
            os.startfile(str(path))
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(path)])
        else:
            subprocess.run(['xdg-open', str(path)])
    except Exception as e:
        print(f"Errore durante l'apertura della cartella '{path}': {e}")


def _make_snake(s: str) -> str:
    snake = "".join(ch.lower() if ch.isalnum() else "_" for ch in s)
    while "__" in snake: snake = snake.replace("__", "_")
    return snake.strip("_")


# --- NUOVA FUNZIONE FLESSIBILE PER LE DATE ---
def _parse_date_flexible(date_str: str) -> datetime.date | None:
    """Prova a leggere una data sia in formato GG/MM/AAAA che AAAA-MM-GG."""
    if not date_str:
        return None
    try:
        # Prova prima il nuovo formato (italiano)
        return datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        try:
            # Se fallisce, prova il vecchio formato (ISO)
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            # Se falliscono entrambi, la data non è valida
            return None


# --- GESTIONE LOG CONCORSI ---

def _get_log_path(root_dir: Path) -> Path:
    return root_dir / ".contests_log.json"


def _read_log(log_path: Path) -> dict:
    if not log_path.exists():
        return {"contests": {}}
    try:
        with log_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"contests": {}}


def _write_log(log_path: Path, data: dict) -> None:
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    if os.name == 'nt':
        try:
            subprocess.run(['attrib', '+H', str(log_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass


def _update_contest_in_log(log_path: Path, contest_name: str, deadline: str | None):
    log_data = _read_log(log_path)
    if contest_name not in log_data["contests"]:
        log_data["contests"][contest_name] = {}
    log_data["contests"][contest_name]["deadline"] = deadline
    _write_log(log_path, log_data)


# --- FUNZIONI DI LETTURA/SCRITTURA FILE ---

def _read_existing_criteria(csv_path: Path) -> list[str]:
    if not csv_path.exists(): return []
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            first_line = f.readline()
            if first_line.startswith('sep='):
                first_line = f.readline()
            f.seek(0)
            if f.readline().startswith('sep='):
                pass

            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(first_line, delimiters=',;')
                reader = csv.reader(f, dialect)
            except csv.Error:
                f.seek(0)
                if f.readline().startswith('sep='):
                    pass
                reader = csv.reader(f, delimiter=';')

            return [c for c in next(reader, [])[1:] if c]
    except Exception:
        return []


def _read_existing_titles(csv_path: Path) -> list[str]:
    if not csv_path.exists(): return []
    titles = []
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            first_line = f.readline()
            if not first_line.startswith('sep='):
                f.seek(0)

            sniffer = csv.Sniffer()
            try:
                sample = f.readline()
                f.seek(0)
                if f.readline().startswith('sep='): pass

                dialect = sniffer.sniff(sample, delimiters=',;')
                reader = csv.reader(f, dialect)
            except csv.Error:
                f.seek(0)
                if f.readline().startswith('sep='): pass
                reader = csv.reader(f, delimiter=';')

            next(reader, None)
            for row in reader:
                if row: titles.append(row[0])
    except Exception:
        pass
    return titles


def _write_consolidated_csv(csv_path: Path, criteria: list[str], titles: list[str]) -> None:
    header = [""] + criteria
    rows = [header] + [[t] + [""] * len(criteria) for t in titles]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        f.write('sep=;\n')
        writer = csv.writer(f, delimiter=';')
        writer.writerows(rows)


def _normalize_string(text: str) -> str:
    text = text.replace('_', ' ').replace('-', ' ')
    return ' '.join(text.split()).strip()


def _parse_filename(path: Path) -> tuple[str, str]:
    stem = path.stem.strip()
    raw_author, raw_title = "", ""
    if FILENAME_SEPARATOR in stem:
        parts = stem.split(FILENAME_SEPARATOR, 1)
        raw_author, raw_title = parts[0], parts[1]
    else:
        match = re.search(r'_(?P<num>\d+)_', stem)
        if match:
            raw_author, raw_title = stem[:match.start()], stem[match.end():]
        else:
            raw_title = stem

    author = _normalize_string(raw_author).title()
    normalized_title = _normalize_string(raw_title)
    title = normalized_title[0].upper() + normalized_title[1:] if normalized_title else ""

    return author or "Autore Sconosciuto", title or "Titolo Sconosciuto"


# --- DASHBOARD DI STATO ---

def _display_contest_status(base: Path, folder_name: str):
    pictures_path = base / "pictures"
    judges_dir = base / "judges"
    jury_kit_dir = base / "jury_kit"
    csv_path = jury_kit_dir / f"{_make_snake(folder_name)} giuria.csv"
    log_path = _get_log_path(base.parent)
    log_data = _read_log(log_path)

    contest_info = log_data.get("contests", {}).get(folder_name, {})
    deadline_str = contest_info.get("deadline")
    deadline_date = _parse_date_flexible(deadline_str)

    photo_count = len([p for p in pictures_path.iterdir() if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg'}])
    criteria = _read_existing_criteria(csv_path)
    jurors = [d.name for d in judges_dir.iterdir() if d.is_dir()]
    submitted_votes = [p.parent.name for p in _find_judge_csvs(judges_dir)]

    print("\n" + "---" * 15)
    print(f"📊 STATO CONCORSO: {folder_name}")
    if deadline_date:
        is_expired = deadline_date < datetime.date.today()
        print(f"  - Scadenza:           {deadline_str} {'(Scaduto)' if is_expired else ''}")
    else:
        print("  - Scadenza:           Non impostata")
    print("---" * 15)
    print(f"  - Foto Trovate:       {photo_count}")
    print(f"  - Criteri Definiti:   {len(criteria)}")
    print(f"  - Giurati Registrati: {len(jurors)}")
    print(f"  - Voti Consegnati:    {len(submitted_votes)} su {len(jurors)}")
    print("---" * 15)


# --- FUNZIONI AZIONE DEL MENU ---

def _action_manage_jurors(judges_dir: Path):
    while True:
        print("\n### 🛠️  Gestione Giurati ###")
        jurors = sorted([d.name for d in judges_dir.iterdir() if d.is_dir()])

        choices = ["Aggiungi un nuovo giurato"]
        if jurors:
            choices.extend(["Rinomina un giurato esistente", "Elimina un giurato"])
        choices.append("Torna al menu principale")

        if inquirer:
            questions = [inquirer.List('action', message="Scegli un'azione", choices=choices, carousel=True)]
            answers = inquirer.prompt(questions)
            if not answers: return
            action = answers['action']
        else:
            for i, choice in enumerate(choices, 1): print(f"  [{i}] {choice}")
            while True:
                try:
                    choice_num = int(_input_or_exit("Scelta: "))
                    if 1 <= choice_num <= len(choices):
                        action = choices[choice_num - 1]
                        break
                    else:
                        print("Scelta non valida.")
                except ValueError:
                    print("Inserisci un numero.")

        if "Aggiungi" in action:
            while True:
                name = _input_or_exit("Nome nuovo giurato (vuoto per terminare): ").strip()
                if not name: break
                safe_name = _sanitize_name(name)
                if (judges_dir / safe_name).exists():
                    print(f"ATTENZIONE: Giurato '{safe_name}' esiste già.")
                else:
                    (judges_dir / safe_name).mkdir(parents=True, exist_ok=True)
                    print(f"✅ Creata cartella per: {safe_name}")

        elif "Rinomina" in action:
            if not jurors:
                print("Nessun giurato da rinominare.")
                continue

            old_name = ""
            if inquirer:
                q = [inquirer.List('old_name', message="Quale giurato vuoi rinominare?", choices=jurors)]
                answers = inquirer.prompt(q)
                if answers:
                    old_name = answers['old_name']
            else:
                print("\nGiurati esistenti:")
                for i, name in enumerate(jurors, 1):
                    print(f"  [{i}] {name}")

                while True:
                    try:
                        choice_idx = int(_input_or_exit("Numero del giurato da rinominare: ")) - 1
                        if 0 <= choice_idx < len(jurors):
                            old_name = jurors[choice_idx]
                            break
                        else:
                            print("Scelta non valida.")
                    except (ValueError, IndexError):
                        print("Inserisci un numero valido.")

            if old_name:
                new_name_raw = _input_or_exit(f"Nuovo nome per '{old_name}': ").strip()
                if new_name_raw:
                    new_name = _sanitize_name(new_name_raw)
                    if (judges_dir / new_name).exists():
                        print(f"ERRORE: Esiste già un giurato di nome '{new_name}'.")
                    else:
                        (judges_dir / old_name).rename(judges_dir / new_name)
                        print(f"✅ '{old_name}' rinominato in '{new_name}'.")

        elif "Elimina" in action:
            if not jurors:
                print("Nessun giurato da eliminare.")
                continue

            name_to_delete = ""
            if inquirer:
                q = [inquirer.List('del_name', message="Quale giurato vuoi eliminare?", choices=jurors)]
                answers = inquirer.prompt(q)
                if answers:
                    name_to_delete = answers['del_name']
            else:
                print("\nGiurati esistenti:")
                for i, name in enumerate(jurors, 1):
                    print(f"  [{i}] {name}")

                while True:
                    try:
                        choice_idx = int(_input_or_exit("Numero del giurato da eliminare: ")) - 1
                        if 0 <= choice_idx < len(jurors):
                            name_to_delete = jurors[choice_idx]
                            break
                        else:
                            print("Scelta non valida.")
                    except (ValueError, IndexError):
                        print("Inserisci un numero valido.")

            if name_to_delete:
                if _confirm_or_exit(f"Sei sicuro di voler eliminare '{name_to_delete}' e i suoi voti?", default=False):
                    shutil.rmtree(judges_dir / name_to_delete)
                    print(f"🗑️  Giurato '{name_to_delete}' eliminato.")
                else:
                    print("Operazione annullata.")

        elif "Torna" in action:
            break


def _action_sync_files(base: Path, folder_name: str):
    print("\n### 🔄 Sincronizzazione Foto e Criteri ###")
    pictures_path = base / "pictures"
    photo_paths = [p for p in pictures_path.iterdir() if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg'}]
    photos_exist = bool(photo_paths)

    jury_kit_dir = base / "jury_kit"
    csv_path = jury_kit_dir / f"{_make_snake(folder_name)} giuria.csv"

    existing_criteria = _read_existing_criteria(csv_path)
    print("\nCriteri attuali:", ", ".join(existing_criteria) if existing_criteria else "Nessuno")
    if _confirm_or_exit("Vuoi modificare i criteri?", default=not existing_criteria):
        placeholders = existing_criteria or ["Attinenza al tema", "Tecnica", "Creatività", "Impressione generale"]
        final_criteria = _collect_criteria_from(placeholders)
    else:
        final_criteria = existing_criteria
    criteria_changed = final_criteria != existing_criteria

    photos_changed = False
    current_titles = []
    if photos_exist:
        current_titles = sorted([_parse_filename(p)[1] for p in photo_paths])
        old_titles = _read_existing_titles(csv_path)
        photos_changed = sorted(current_titles) != sorted(old_titles)
    else:
        print("\nNessuna foto trovata. La sincronizzazione riguarderà solo i criteri.")
        if _read_existing_titles(csv_path): photos_changed = True

    if not photos_changed and not criteria_changed:
        print("\nNessuna modifica rilevata. Tutto è già sincronizzato.")
        _input_or_exit("Premi Invio per continuare...")
        return

    print("\n--- Anteprima Modifiche ---")
    if photos_changed and photos_exist:
        print(f"  +/- Verranno sincronizzate {len(current_titles)} foto.")
    elif photos_changed and not photos_exist:
        print("  - Rilevata la rimozione di tutte le foto.")
    if criteria_changed: print("  ✏️ I criteri di valutazione sono stati modificati.")
    print("--------------------------")

    if _confirm_or_exit("Procedere con le modifiche?", default=True):
        titles_for_csv = current_titles
        if photos_changed and photos_exist: random.shuffle(titles_for_csv)

        _write_consolidated_csv(csv_path, final_criteria, titles_for_csv)
        print(f"✅ File '{csv_path.name}' aggiornato in 'jury_kit'.")

        if photos_exist:
            ppt_path = jury_kit_dir / f"{_make_snake(folder_name)}.pptx"
            parsed_photos = {_parse_filename(p)[1]: p for p in photo_paths}
            ordered_pairs = [(t, parsed_photos[t]) for t in titles_for_csv if t in parsed_photos]

            _build_ppt(ppt_path, ordered_pairs)
            print(f"✅ Presentazione '{ppt_path.name}' aggiornata in 'jury_kit'.")

            _update_original_pictures_folder(jury_kit_dir, ordered_pairs)

        archive_base_path = base / f"{_make_snake(folder_name)}_jury_kit"
        _create_jury_kit_zip(jury_kit_dir, archive_base_path)

    else:
        print("❌ Operazione annullata.")

    _input_or_exit("Premi Invio per tornare al menu...")


def _action_generate_leaderboard(base: Path, folder_name: str):
    print("\n### 🏆 Generazione Classifica Finale ###")

    # --- CONTROLLO DI ROBUSTEZZA ---
    # Controlla la presenza di python-pptx qui, prima di iniziare.
    if Presentation is None:
        print("\n❌ ERRORE: La libreria 'python-pptx' è necessaria per creare la presentazione.")
        print("   Per installarla, esegui dal terminale: pip install python-pptx")
        _input_or_exit("Premi Invio per tornare al menu...")
        return

    pictures_path = base / "pictures"
    judges_dir = base / "judges"
    jury_kit_dir = base / "jury_kit"
    csv_path = jury_kit_dir / f"{_make_snake(folder_name)} giuria.csv"

    photo_paths = [p for p in pictures_path.iterdir() if p.is_file()]
    criteria = _read_existing_criteria(csv_path)
    juror_dirs = [d for d in judges_dir.iterdir() if d.is_dir()]
    submitted_csvs = _find_judge_csvs(judges_dir)

    can_generate = all([photo_paths, criteria, juror_dirs, submitted_csvs])

    if not can_generate:
        print("Impossibile generare la classifica. Condizioni non soddisfatte:")
        if not photo_paths: print("  - ❌ Nessuna foto trovata.")
        if not criteria: print("  - ❌ Nessun criterio definito.")
        if not juror_dirs: print("  - ❌ Nessun giurato registrato.")
        if not submitted_csvs: print("  - ❌ Nessun giurato ha consegnato i voti.")
        _input_or_exit("\nPremi Invio per tornare al menu...")
        return

    _generate_leaderboard_logic(base, csv_path)
    _open_folder(base / "leaderboard")
    _input_or_exit("Premi Invio per tornare al menu...")


def _action_edit_deadline(root_dir: Path, contest_name: str):
    print("\n### ✏️  Modifica Data di Scadenza ###")
    log_path = _get_log_path(root_dir)
    log_data = _read_log(log_path)
    current_deadline = log_data.get("contests", {}).get(contest_name, {}).get("deadline")

    print(f"Data di scadenza attuale: {current_deadline or 'Non impostata'}")

    while True:
        new_date_str = _input_or_exit("Nuova data (GG/MM/AAAA) o vuoto per rimuovere: ").strip()
        if not new_date_str:
            _update_contest_in_log(log_path, contest_name, None)
            print("✅ Data di scadenza rimossa.")
            break
        try:
            datetime.datetime.strptime(new_date_str, '%d/%m/%Y')
            _update_contest_in_log(log_path, contest_name, new_date_str)
            print(f"✅ Data di scadenza aggiornata a {new_date_str}.")
            break
        except ValueError:
            print("Formato data non valido. Usa GG/MM/AAAA. Riprova.")

    _input_or_exit("Premi Invio per tornare al menu...")


# --- LOGICA PRINCIPALE (CORE) ---

def _select_or_create_contest(root_dir: Path) -> tuple[Path, str] | None:
    """Seleziona un concorso o ne crea uno nuovo, gestendo i separatori."""
    log_path = _get_log_path(root_dir)
    log_data = _read_log(log_path)
    today = datetime.date.today()

    existing_contests = sorted([d.name for d in root_dir.iterdir() if d.is_dir()])
    active_contests, expired_contests = [], []

    for contest_name in existing_contests:
        info = log_data.get("contests", {}).get(contest_name, {})
        deadline_str = info.get("deadline")
        deadline_date = _parse_date_flexible(deadline_str)
        if deadline_date:
            if deadline_date < today:
                expired_contests.append(contest_name)
            else:
                active_contests.append(contest_name)
        else:
            active_contests.append(contest_name)

    new_opt = ">> CREA UN NUOVO CONCORSO <<"
    active_separator = "--- Concorsi Attivi ---"
    expired_separator = "--- Concorsi Scaduti ---"
    separators = [active_separator, expired_separator]

    while True:
        choices = [new_opt]
        if active_contests:
            choices.append(active_separator)
            choices.extend(active_contests)
        if expired_contests:
            choices.append(expired_separator)
            choices.extend(expired_contests)

        if inquirer:
            q = [inquirer.List('contest', message="Scegli un'azione o un concorso", choices=choices,
                               carousel=True)]
            answers = inquirer.prompt(q)
            if not answers: return None
            chosen_name = answers['contest']

            if chosen_name in separators:
                print("Selezione non valida. Scegli un nome di concorso o un'azione dalla lista.")
                continue
        else:
            print("\nScegli un'opzione:")
            print(f"  [1] {new_opt}")

            all_contests = active_contests + expired_contests
            current_idx = 2

            if active_contests:
                print("\n--- Concorsi Attivi ---")
                for name in active_contests:
                    print(f"  [{current_idx}] {name}")
                    current_idx += 1

            if expired_contests:
                print("\n--- Concorsi Scaduti ---")
                for name in expired_contests:
                    print(f"  [{current_idx}] {name}")
                    current_idx += 1

            while True:
                try:
                    choice = int(_input_or_exit("\nScelta: "))
                    if choice == 1:
                        chosen_name = new_opt
                        break
                    elif 2 <= choice < 2 + len(all_contests):
                        chosen_name = all_contests[choice - 2]
                        break
                    else:
                        print("Scelta non valida.")
                except ValueError:
                    print("Inserisci un numero.")

        break

    if chosen_name == new_opt:
        name = _input_or_exit("Nome del nuovo concorso: ")
        safe_name = _sanitize_name(name)

        while True:
            deadline_str = _input_or_exit("Data di scadenza (GG/MM/AAAA, opzionale): ").strip()
            if not deadline_str:
                deadline = None
                break
            try:
                datetime.datetime.strptime(deadline_str, '%d/%m/%Y')
                deadline = deadline_str
                break
            except ValueError:
                print("Formato data non valido. Riprova.")

        _update_contest_in_log(log_path, safe_name, deadline)
        return root_dir / safe_name, safe_name
    else:
        return root_dir / chosen_name, chosen_name


def _collect_criteria_from(placeholders: list[str]) -> list[str]:
    criteria = []
    print("\n### Definizione/Modifica Criteri di Valutazione ###")
    prompt_suffix = "(Invio per usare, 'no' per scartare, o scrivi per sostituire): "

    for ph in placeholders:
        ans = _input_or_exit(f"Criterio [{ph}] {prompt_suffix}").strip()
        if ans == "":
            criteria.append(ph)
        elif ans.lower() != "no":
            criteria.append(ans)

    while True:
        more = _input_or_exit("Aggiungi un altro criterio (vuoto per finire): ").strip()
        if not more: break
        criteria.append(more)
    return criteria


def _update_original_pictures_folder(jury_kit_dir: Path, title_path_pairs: list[tuple[str, Path]]):
    """Crea/aggiorna la cartella 'original_pictures' dentro a 'jury_kit' con le foto del concorso."""
    original_pictures_dir = jury_kit_dir / "original_pictures"

    if original_pictures_dir.exists():
        shutil.rmtree(original_pictures_dir)
    original_pictures_dir.mkdir(exist_ok=True)

    copied_count = 0
    for title, original_path in title_path_pairs:
        safe_title = _sanitize_name(title)
        new_filename = f"{safe_title}{original_path.suffix}"
        destination_path = original_pictures_dir / new_filename

        try:
            shutil.copy(original_path, destination_path)
            copied_count += 1
        except Exception as e:
            print(f"ERRORE: Impossibile copiare '{original_path.name}' in '{destination_path}': {e}")

    print(f"✅ Cartella 'original_pictures' aggiornata con {copied_count} foto.")


def _create_jury_kit_zip(jury_kit_dir: Path, archive_base_name: Path):
    """Crea un archivio ZIP della cartella jury_kit."""
    try:
        zip_path = archive_base_name.parent / f"{archive_base_name.name}.zip"
        if zip_path.exists():
            os.remove(zip_path)

        shutil.make_archive(
            base_name=str(archive_base_name),
            format='zip',
            root_dir=jury_kit_dir
        )
        print(f"✅ Creato/Aggiornato archivio ZIP: '{archive_base_name.name}.zip'")
    except Exception as e:
        print(f"ERRORE: Impossibile creare l'archivio ZIP: {e}")


# --- LOGICA DI GENERAZIONE (PPT E CLASSIFICA) ---
def _build_ppt(ppt_path: Path, title_path_pairs: list[tuple[str, Path]]) -> None:
    if Presentation is None:
        print("\nAVVISO: `python-pptx` non installato. Salto creazione presentazione.")
        return
    prs = Presentation()
    slide_w, slide_h = prs.slide_width, prs.slide_height
    blank_layout = prs.slide_layouts[6]
    bottom_band_h, top_margin, side_margin = Inches(0.4), Inches(0.1), Inches(0.1)
    avail_w, avail_h = slide_w - 2 * side_margin, slide_h - bottom_band_h - top_margin

    for title, img_path in title_path_pairs:
        slide = prs.slides.add_slide(blank_layout)
        try:
            pic = slide.shapes.add_picture(str(img_path), left=side_margin, top=top_margin)
            orig_w, orig_h = pic.image.size
            scale = min(avail_w / orig_w, avail_h / orig_h)
            new_w, new_h = int(orig_w * scale), int(orig_h * scale)
            pic.width, pic.height = new_w, new_h
            pic.left, pic.top = int((slide_w - new_w) / 2), top_margin

            tx_box = slide.shapes.add_textbox(0, slide_h - bottom_band_h, slide_w, bottom_band_h)
            tf = tx_box.text_frame
            tf.clear()
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = title
            font = run.font
            font.size = Pt(22)
            font.bold = True
        except Exception as e:
            print(f"ERRORE: Impossibile aggiungere l'immagine '{img_path.name}': {e}")
    prs.save(str(ppt_path))


def _build_leaderboard_ppt(ppt_path: Path, ranked_entries: list[tuple[int, str, Path]]) -> bool:
    """Crea la presentazione PowerPoint e restituisce True in caso di successo, False altrimenti."""
    if Presentation is None:
        return False

    try:
        prs = Presentation()
        blank_layout = prs.slide_layouts[6]
        slide_w, slide_h = prs.slide_width, prs.slide_height

        for rank, title, img_path in ranked_entries:
            # Slide con il testo
            title_slide = prs.slides.add_slide(blank_layout)
            tx_box = title_slide.shapes.add_textbox(Inches(0.5), Inches(0.5), slide_w - Inches(1), slide_h - Inches(1))
            tf = tx_box.text_frame
            tf.clear()
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            author, _ = _parse_filename(img_path)

            p_pos = tf.paragraphs[0]
            p_pos.alignment = PP_ALIGN.CENTER
            run_pos = p_pos.add_run()
            run_pos.text = f"{rank}° Classificato"
            run_pos.font.size, run_pos.font.bold = Pt(54), True

            p_title = tf.add_paragraph()
            p_title.alignment = PP_ALIGN.CENTER
            run_title = p_title.add_run()
            run_title.text = title
            run_title.font.size = Pt(32)

            p_author = tf.add_paragraph()
            p_author.alignment = PP_ALIGN.CENTER
            run_author = p_author.add_run()
            run_author.text = f"di {author}"
            run_author.font.size, run_author.font.italic = Pt(24), True

            # Slide con l'immagine
            img_slide = prs.slides.add_slide(blank_layout)
            try:
                pic = img_slide.shapes.add_picture(str(img_path), 0, 0)
                img_w, img_h = pic.image.size
                scale = min(slide_w / img_w, slide_h / img_h)
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                pic.width, pic.height = new_w, new_h
                pic.left, pic.top = int((slide_w - new_w) / 2), int((slide_h - new_h) / 2)
            except FileNotFoundError:
                print(f"⚠️  AVVISO: File immagine non trovato per '{title}': {img_path}")
                # Aggiunge un testo di errore sulla slide
                err_box = img_slide.shapes.add_textbox(Inches(1), Inches(1), slide_w - Inches(2), slide_h - Inches(2))
                err_tf = err_box.text_frame
                err_tf.text = f"Immagine non trovata:\n{img_path.name}"
                err_tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            except Exception as e:
                print(f"ERRORE: Impossibile aggiungere l'immagine '{img_path.name}': {e}")

        prs.save(str(ppt_path))
        return True

    except Exception as e:
        print(f"\n❌ ERRORE CRITICO durante la creazione della presentazione PowerPoint: {e}")
        if ppt_path.exists():
            try:
                os.remove(ppt_path)  # Tenta di pulire file corrotti
            except OSError:
                pass
        return False


def _find_judge_csvs(judges_dir: Path) -> list[Path]:
    if not judges_dir.exists(): return []
    return [f for d in judges_dir.iterdir() if d.is_dir() for f in d.iterdir() if
            f.is_file() and f.suffix.lower() == ".csv"]


def _generate_leaderboard_logic(base: Path, master_csv: Path) -> None:
    judges_dir = base / "judges"
    all_juror_dirs = [d for d in judges_dir.iterdir() if d.is_dir()]
    judge_csvs = _find_judge_csvs(judges_dir)
    submitted_jurors = {p.parent.name for p in judge_csvs}
    missing_jurors = [d.name for d in all_juror_dirs if d.name not in submitted_jurors]

    print("\nGenerazione classifica in corso...")
    if missing_jurors:
        print(f"⚠️  ATTENZIONE: Trovati i file di {len(submitted_jurors)} giurati su {len(all_juror_dirs)}.")
        print(f"   Mancano i voti di: {', '.join(missing_jurors)}")
        if not _confirm_or_exit("Generare classifica con dati parziali?", default=False):
            print("Generazione classifica annullata.");
            return

    criteria = _read_existing_criteria(master_csv)
    titles = _read_existing_titles(master_csv)
    values: dict[tuple[str, str], list[float]] = defaultdict(list)

    for jcsv in judge_csvs:
        try:
            with jcsv.open("r", encoding="utf-8-sig", newline="") as f:
                first_line = f.readline()
                if not first_line.startswith('sep='):
                    f.seek(0)

                reader = csv.reader(f, delimiter=';')
                header = next(reader, [])
                crit_to_idx = {name: idx for idx, name in enumerate(header[1:], start=1) if name}
                for row in reader:
                    if not row: continue
                    title, s_val = row[0], ""
                    if title not in titles: continue
                    for crit in criteria:
                        col = crit_to_idx.get(crit)
                        if col is not None and col < len(row) and row[col].strip():
                            try:
                                s_val = row[col].strip().replace(",", ".")
                                values[(title, crit)].append(float(s_val))
                            except ValueError:
                                print(f"AVVISO: Voto non valido ('{s_val}') in {jcsv.parent.name}")
        except Exception as e:
            print(f"ERRORE: Impossibile leggere '{jcsv}': {e}")

    header = ["Posizione", "Titolo"] + criteria + ["Media Totale"]
    scored = []
    for title in titles:
        criterion_means = [sum(v) / len(v) for c in criteria if (v := values.get((title, c)))]
        final_score = sum(criterion_means) / len(criterion_means) if criterion_means else -1.0
        row_cells = [f"{(sum(v) / len(v)):.2f}" if (v := values.get((title, c))) else "" for c in criteria]
        scored.append((title, row_cells, final_score))

    scored.sort(key=lambda x: (-x[2], x[0]))

    out_rows = [header]
    rank, last_score = 0, float('inf')
    for title, cells, total in scored:
        if total < last_score:
            rank += 1
            last_score = total
        rank_str = str(rank) if total >= 0 else "N/D"
        out_rows.append([rank_str, title] + cells + [f"{total:.2f}" if total >= 0 else "N/D"])

    leaderboard_dir = base / "leaderboard"
    leaderboard_dir.mkdir(exist_ok=True)
    leaderboard_csv = leaderboard_dir / "classifica.csv"
    with leaderboard_csv.open("w", encoding="utf-8-sig", newline="") as f:
        f.write('sep=;\n')
        csv.writer(f, delimiter=';').writerows(out_rows)
    print(f"✅ Classifica CSV salvata in: {leaderboard_csv.name}")

    winners_data = [s for s in scored if s[2] >= 0]
    if winners_data:
        all_ranks = [int(row[0]) for row in out_rows[1:] if row[0].isdigit()]
        if not all_ranks:
            print("ℹ️ Nessun classificato con punteggio valido. Salto creazione presentazione.")
            return

        unique_ranks = sorted(list(set(all_ranks)))
        rank_cutoff = unique_ranks[min(9, len(unique_ranks) - 1)]

        ppt_entries = []
        pictures_dir = base / "pictures"
        title_path_map = {_parse_filename(p)[1]: p for p in pictures_dir.iterdir() if p.is_file()}

        for row in out_rows[1:]:
            if not row[0].isdigit(): continue

            current_rank = int(row[0])
            if current_rank <= rank_cutoff:
                s_title = row[1]
                if s_title in title_path_map:
                    ppt_entries.append((current_rank, s_title, title_path_map[s_title]))
                else:
                    print(
                        f"⚠️  AVVISO: La foto '{s_title}' è in classifica ma non è stata trovata nella cartella 'pictures'.")
            else:
                break

        if ppt_entries:
            ppt_entries.reverse()
            ppt_path = leaderboard_dir / "classifica.pptx"

            if _build_leaderboard_ppt(ppt_path, ppt_entries):
                print(f"✅ Presentazione classifica salvata in: {ppt_path.name}")
        else:
            print("ℹ️ Nessuna foto trovata per i primi classificati. Salto creazione presentazione.")


# --- FUNZIONE MAIN ---

def main() -> None:
    print("---" * 15)
    print("   Benvenuto nello strumento di gestione concorsi fotografici!   ")
    print("---" * 15)

    root_dir = Path.cwd() / "Concorsi Orizzonti Fotografici"
    root_dir.mkdir(exist_ok=True)

    contest_selection = _select_or_create_contest(root_dir)
    if not contest_selection:
        print("Nessun concorso selezionato. Uscita.");
        return
    base, folder_name = contest_selection

    if not base.exists():
        base.mkdir(parents=True)
        print(f"\n✅ Creata nuova cartella per il concorso: '{base.name}'")

    for sub in ["pictures", "jury_kit", "leaderboard", "judges"]:
        (base / sub).mkdir(exist_ok=True)

    while True:
        _display_contest_status(base, folder_name)

        choices = {
            "sync": "🔄  Sincronizza e Crea/Aggiorna Jury Kit",
            "jurors": "🛠️  Gestisci Giurati",
            "deadline": "✏️  Modifica data di scadenza",
            "leaderboard": "🏆  Genera Classifica Finale",
            "open": "📂  Apri la cartella del concorso",
            "exit": "🚪  Esci"
        }

        if inquirer:
            q = [inquirer.List('action', message="Menu Principale", choices=list(choices.values()), carousel=True)]
            answers = inquirer.prompt(q)
            if not answers: break
            chosen_value = answers['action']
            chosen_key = next(key for key, value in choices.items() if value == chosen_value)
        else:
            choice_map = list(choices.keys())
            for i, key in enumerate(choice_map, 1): print(f"  [{i}] {choices[key]}")
            while True:
                try:
                    num = int(_input_or_exit("Scegli un'azione: "))
                    if 1 <= num <= len(choice_map):
                        chosen_key = choice_map[num - 1];
                        break
                    else:
                        print("Scelta non valida.")
                except ValueError:
                    print("Inserisci un numero.")

        if chosen_key == "sync":
            _action_sync_files(base, folder_name)
        elif chosen_key == "jurors":
            _action_manage_jurors(base / "judges")
        elif chosen_key == "deadline":
            _action_edit_deadline(root_dir, folder_name)
        elif chosen_key == "leaderboard":
            _action_generate_leaderboard(base, folder_name)
        elif chosen_key == "open":
            _open_folder(base)
        elif chosen_key == "exit":
            break

    print("\nGrazie per aver usato lo strumento. Arrivederci! 👋")


if __name__ == "__main__":
    if Presentation is None:
        print("AVVISO: `python-pptx` non installato, funzionalità di presentazione disabilitate.")
        print("Per abilitarli, esegui: pip install python-pptx\n")
    if inquirer is None:
        print("AVVISO: `inquirer` non installato o non sei in un terminale interattivo.")
        print("Verrà usata un'interfaccia a menu numerico.\n")

    main()