from peewee import IntegrityError
import random
import re
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static

from Interface.view_components import MenuPanel, VocabularyTablePanel, WordCapturePanel
from Interface.view_texts import RULES_TEXT, TENSES_TEXT
from Services.storage.dictionary_pos_rules import build_dictionary_pos_mapping_help_text
from Services.storage.vocabulary_service import InvalidEnglishExampleError, VocabularyService
from Services.validation.spanish_feedback import format_issue_es, format_suggestion_es


class LearnEnglishApp(App):
    TITLE = "Learn English Terminal"
    BINDINGS = [
        ("up", "menu_up", "Menu arriba"),
        ("down", "menu_down", "Menu abajo"),
    ]
    CSS = """
    Screen {
        layout: vertical;
        background: #0f1720;
        color: #d8e1ea;
    }

    #root {
        width: 100%;
        height: 1fr;
        layout: grid;
        grid-size: 3 1;
        grid-columns: 14% 41% 45%;
        grid-rows: 1fr;
        padding: 1;
    }

    .panel {
        height: 1fr;
        padding: 1 2;
        border: round #406a8f;
        background: #16212c;
        margin-right: 1;
    }

    #right-panel {
        margin-right: 0;
        border: round #5e7f53;
        background: #16241b;
    }

    #center-panel {
        border: round #8b6f3d;
        background: #231d14;
    }

    #left-panel {
        border: round #5c4e8c;
        background: #1d1830;
    }

    .panel-title {
        text-style: bold;
        color: #f2f6fb;
        margin-bottom: 0;
    }

    .panel-subtitle {
        color: #9fb2c4;
        margin-bottom: 1;
    }

    #menu-buttons {
        height: auto;
        margin-top: 1;
        width: 100%;
    }

    #menu-buttons Button {
        width: 100%;
        margin-bottom: 1;
        border: round #5e7390;
        background: #243447;
        color: #eef4fb;
        padding: 0 1;
    }

    #menu-buttons Button:focus {
        border: round #f0c36b;
        background: #32495f;
        text-style: bold;
    }

    #words_table {
        height: 1fr;
        margin-top: 1;
        border: round #8b6f3d;
        background: #1a1611;
    }

    #word-form {
        display: none;
        height: auto;
        margin-top: 1;
        border-top: solid #3e5a49;
        padding-top: 1;
    }

    #word-form.visible {
        display: block;
    }

    #game-view {
        display: none;
        height: 1fr;
        margin-top: 1;
        border-top: solid #3e5a49;
        padding-top: 1;
    }

    #game-view.visible {
        display: block;
    }

    #study-view.hidden {
        display: none;
    }

    #game_title {
        color: #f1f7d5;
        text-style: bold;
        margin-bottom: 1;
    }

    #game_status {
        color: #c7e7d0;
        border: round #3d5c4a;
        background: #102018;
        padding: 0 1;
        margin-bottom: 1;
    }

    #game_word_prompt {
        color: #fff1c4;
        text-style: bold;
        margin-bottom: 1;
    }

    #game_example_prompt {
        color: #bed9c5;
        border: round #304f3f;
        background: #0f1913;
        padding: 0 1;
        margin-bottom: 1;
    }

    #game_translation_input, #game_tense_input {
        margin-bottom: 1;
        border: round #527465;
        background: #111a15;
        color: #eff7f0;
    }

    #game-actions {
        height: auto;
    }

    #game-actions Button {
        width: 1fr;
        margin-right: 1;
    }

    #game-actions Button:last-child {
        margin-right: 0;
    }

    #word-form Input {
        margin-bottom: 1;
        border: round #527465;
        background: #111a15;
        color: #eff7f0;
    }

    #word-form Button {
        margin-top: 1;
        width: 100%;
        border: round #527465;
        background: #294136;
        color: #eff7f0;
    }

    #catalog_match_info {
        color: #b9cfbf;
        border: round #31483c;
        background: #101813;
        padding: 0 1;
        margin-bottom: 1;
    }

    #message_scroll {
        margin-top: 1;
        min-height: 6;
        height: 1fr;
        overflow-y: auto;
        border: round #3f5d49;
        background: #0f1812;
        padding: 0 1 1 1;
    }

    #message {
        width: 100%;
        height: auto;
        color: #dceee0;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.vocabulary_service = VocabularyService()
        self._table_entries = []
        self._editing_word_id: str | None = None
        self._game_current_entry = None
        self._game_current_tense: str | None = None
        self._game_score = 0
        self._game_rounds = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="root"):
            yield MenuPanel()
            yield VocabularyTablePanel()
            yield WordCapturePanel()
        yield Footer()

    def on_mount(self) -> None:
        self.vocabulary_service.initialize_database()
        self._setup_table()
        self._refresh_table()
        self._set_game_mode(False)
        try:
            self._focus_menu_button(0)
        except Exception:
            pass

    def on_unmount(self) -> None:
        self.vocabulary_service.close_database()

    def _setup_table(self) -> None:
        table = self.query_one("#words_table", DataTable)
        table.clear(columns=True)
        table.add_columns("Ingles", "Espanol", "Ejemplo EN", "Ejemplo ES")
        table.cursor_type = "row"

    def _refresh_table(self) -> None:
        table = self.query_one("#words_table", DataTable)
        table.clear()
        self._table_entries = self.vocabulary_service.list_vocabulary_entries()
        for entry in self._table_entries:
            table.add_row(
                entry.english_word,
                entry.spanish_meaning,
                entry.example_english,
                entry.example_spanish,
            )

    def _set_message(self, text: str) -> None:
        try:
            message_widget = self.query_one("#message", Static)
            message_widget.update(text)
            try:
                message_widget.refresh(layout=True)
            except Exception:
                pass
        except Exception:
            return
        try:
            self.query_one("#message_scroll").scroll_home(animate=False)
        except Exception:
            pass

    def _set_results_document_mode(self, enabled: bool) -> None:
        # En el layout de 3 paneles, la tabla vive en el panel central.
        # Este hook se mantiene para compatibilidad con el flujo actual.
        return

    def _set_game_mode(self, enabled: bool) -> None:
        study_view = self.query_one("#study-view", Vertical)
        game_view = self.query_one("#game-view", Vertical)
        if enabled:
            study_view.add_class("hidden")
            game_view.add_class("visible")
            self._toggle_form(False)
            self.query_one("#game_translation_input", Input).focus()
            try:
                subtitles = self.query(".panel-subtitle")
                if subtitles:
                    subtitles.last().update("Modo juego")
            except Exception:
                pass
        else:
            study_view.remove_class("hidden")
            game_view.remove_class("visible")
            try:
                subtitles = self.query(".panel-subtitle")
                if subtitles:
                    subtitles.last().update("Feedback + formulario")
            except Exception:
                pass

    @staticmethod
    def _map_primary_tense_to_game_label(primary_tense: str | None) -> str | None:
        if not primary_tense:
            return None
        if primary_tense.startswith("present"):
            return "presente"
        if primary_tense.startswith("past"):
            return "pasado"
        if primary_tense.startswith("future"):
            return "futuro"
        return None

    @staticmethod
    def _normalize_text_answer(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def _translation_matches(self, expected: str, answer: str) -> bool:
        normalized_answer = self._normalize_text_answer(answer)
        if not normalized_answer:
            return False
        normalized_expected = self._normalize_text_answer(expected)
        if normalized_expected == normalized_answer:
            return True
        options = [
            self._normalize_text_answer(part)
            for part in re.split(r"[,;/|]", expected)
            if self._normalize_text_answer(part)
        ]
        return normalized_answer in options

    def _game_candidates(self):
        candidates = []
        analyzer = self.vocabulary_service.rule_engine.sentence_analyzer
        for entry in self._table_entries:
            if not entry.english_word or not entry.spanish_meaning or not entry.example_english:
                continue
            analysis = analyzer.analyze_english(entry.example_english)
            tense_label = self._map_primary_tense_to_game_label(analysis.primary_tense_guess)
            if tense_label is None:
                continue
            candidates.append((entry, tense_label, analysis.primary_tense_guess))
        return candidates

    def _start_next_game_round(self) -> None:
        if not self._table_entries:
            self._refresh_table()
        candidates = self._game_candidates()
        if not candidates:
            self.query_one("#game_status", Static).update(
                "No hay suficientes palabras con ejemplo y tiempo detectable. Agrega ejemplos en presente/pasado/futuro."
            )
            self.query_one("#game_word_prompt", Static).update("-")
            self.query_one("#game_example_prompt", Static).update("-")
            self._game_current_entry = None
            self._game_current_tense = None
            return

        entry, tense_label, raw_tense = random.choice(candidates)
        self._game_current_entry = entry
        self._game_current_tense = tense_label
        self.query_one("#game_translation_input", Input).value = ""
        self.query_one("#game_tense_input", Input).value = ""
        self.query_one("#game_word_prompt", Static).update(f"Palabra: {entry.english_word}")
        self.query_one("#game_example_prompt", Static).update(f"Ejemplo EN: {entry.example_english}")
        self.query_one("#game_status", Static).update(
            f"Ronda {self._game_rounds + 1} | Puntaje {self._game_score}/{self._game_rounds}"
        )
        self.query_one("#game_translation_input", Input).focus()

    def _check_game_answer(self) -> None:
        if self._game_current_entry is None or self._game_current_tense is None:
            self.query_one("#game_status", Static).update("Primero presiona 'Siguiente' para cargar una palabra.")
            return
        translation_input = self.query_one("#game_translation_input", Input).value
        tense_input = self.query_one("#game_tense_input", Input).value
        translation_ok = self._translation_matches(self._game_current_entry.spanish_meaning, translation_input)
        tense_ok = self._normalize_text_answer(tense_input) == self._game_current_tense
        self._game_rounds += 1
        if translation_ok and tense_ok:
            self._game_score += 1
            self.query_one("#game_status", Static).update(
                f"Correcto. Puntaje {self._game_score}/{self._game_rounds}"
            )
        else:
            parts = []
            if not translation_ok:
                parts.append(f"traduccion esperada: {self._game_current_entry.spanish_meaning}")
            if not tense_ok:
                parts.append(f"tiempo esperado: {self._game_current_tense}")
            self.query_one("#game_status", Static).update(
                f"Incorrecto ({'; '.join(parts)}). Puntaje {self._game_score}/{self._game_rounds}"
            )

    def _show_document_text(self, text: str) -> None:
        try:
            self._toggle_form(False)
        except Exception:
            pass
        self._set_message(text)

    @staticmethod
    def _append_section(lines: list[str], title: str, items: list[str]) -> None:
        if not items:
            return
        if lines:
            lines.append("")
        lines.append(title)
        for item in items:
            lines.append(f"  - {item}")

    @staticmethod
    def _build_validation_summary(validation) -> str:
        errors = len(getattr(validation, "errors", []) or [])
        warnings = len(getattr(validation, "warnings", []) or [])
        pattern_warnings = len(getattr(validation, "pattern_warnings", []) or [])
        lexical_hints = len(getattr(validation, "lexical_hints", []) or [])
        pattern_hints = len(getattr(validation, "pattern_hints", []) or [])
        return (
            "Resumen validacion | "
            f"errores={errors} | avisos={warnings} | "
            f"warnings_patron={pattern_warnings} | pistas_patron={pattern_hints} | pistas_lexicas={lexical_hints}"
        )

    def _format_validation_feedback(self, validation, original_text: str | None = None) -> list[str]:
        lines: list[str] = []
        lines.append(self._build_validation_summary(validation))

        if validation.errors:
            self._append_section(
                lines,
                "Errores detectados (EN ejemplo)",
                [f"{issue.rule_id}: {format_issue_es(issue.rule_id, original_text)}" for issue in validation.errors],
            )

        if validation.warnings:
            self._append_section(
                lines,
                "Avisos detectados (EN ejemplo)",
                [f"{issue.rule_id}: {format_issue_es(issue.rule_id, original_text)}" for issue in validation.warnings],
            )

        pattern_warnings = getattr(validation, "pattern_warnings", [])
        pattern_hints = getattr(validation, "pattern_hints", [])
        lexical_hints = getattr(validation, "lexical_hints", [])

        if pattern_warnings:
            self._append_section(
                lines,
                "Warnings de patron",
                [f"{issue.rule_id}: {format_suggestion_es(issue.message)}" for issue in pattern_warnings],
            )

        if pattern_hints:
            self._append_section(
                lines,
                "Pistas de patron",
                [format_suggestion_es(hint) for hint in pattern_hints],
            )

        if lexical_hints:
            unknown_hints: list[str] = []
            semantic_hints: list[str] = []
            for hint in lexical_hints:
                target = unknown_hints if "No se encontro" in hint else semantic_hints
                target.append(format_suggestion_es(hint))
            if semantic_hints:
                self._append_section(lines, "Pistas lexicas", semantic_hints)
            if unknown_hints:
                preview = unknown_hints[:3]
                if len(unknown_hints) > 3:
                    preview.append(f"... y {len(unknown_hints) - 3} mas (diccionario local incompleto)")
                self._append_section(lines, "Diccionario local (faltantes)", preview)

        if validation.suggestions and not pattern_hints and not lexical_hints:
            self._append_section(
                lines,
                "Sugerencias",
                [format_suggestion_es(suggestion) for suggestion in validation.suggestions],
            )

        return lines

    def _get_menu_buttons(self) -> list[Button]:
        return [
            self.query_one("#show_game", Button),
            self.query_one("#show_words", Button),
            self.query_one("#show_form", Button),
            self.query_one("#show_rules", Button),
            self.query_one("#show_pos_mapping", Button),
            self.query_one("#show_tenses", Button),
            self.query_one("#exit", Button),
        ]

    def _focus_menu_button(self, index: int) -> None:
        menu_buttons = self._get_menu_buttons()
        if menu_buttons:
            menu_buttons[index % len(menu_buttons)].focus()

    def _move_menu_focus(self, step: int) -> None:
        menu_buttons = self._get_menu_buttons()
        if not menu_buttons:
            return

        focused = self.focused
        if focused is not None and focused not in menu_buttons:
            return

        current_index = 0
        for idx, button in enumerate(menu_buttons):
            if button is focused:
                current_index = idx
                break

        menu_buttons[(current_index + step) % len(menu_buttons)].focus()

    def _toggle_form(self, visible: bool) -> None:
        form = self.query_one("#word-form", Vertical)
        if visible:
            form.add_class("visible")
            self.query_one("#english_word_input", Input).focus()
        else:
            form.remove_class("visible")

    def _clear_form(self) -> None:
        self._editing_word_id = None
        for input_id in (
            "#english_word_input",
            "#spanish_meaning_input",
            "#example_english_input",
            "#example_spanish_input",
        ):
            self.query_one(input_id, Input).value = ""
        self.query_one("#catalog_match_info", Static).update("Catalogo: sin busqueda")

    def _prefill_form_for_entry(self, entry) -> None:
        self._editing_word_id = entry.word_id
        self.query_one("#english_word_input", Input).value = entry.english_word
        self.query_one("#spanish_meaning_input", Input).value = entry.spanish_meaning
        self.query_one("#example_english_input", Input).value = entry.example_english
        self.query_one("#example_spanish_input", Input).value = entry.example_spanish
        self.query_one("#catalog_match_info", Static).update(
            f"Editando: {entry.english_word} (id={entry.word_id[:8]})"
        )

    def _lookup_catalog_and_prefill(self) -> None:
        english_word = self.query_one("#english_word_input", Input).value.strip()
        if not english_word:
            self.query_one("#catalog_match_info", Static).update("Catalogo: escribe una palabra primero.")
            return

        match = self.vocabulary_service.lookup_catalog_word(english_word)
        if match is None:
            self.query_one("#catalog_match_info", Static).update(
                f"Catalogo: no se encontro '{english_word}'. Puedes guardar manualmente."
            )
            return

        self.query_one("#english_word_input", Input).value = match.english_word
        spanish_input = self.query_one("#spanish_meaning_input", Input)
        if not spanish_input.value.strip() and match.spanish_translation:
            spanish_input.value = match.spanish_translation

        self.query_one("#catalog_match_info", Static).update(
            "Catalogo: encontrada "
            f"'{match.english_word}' | POS={match.pos_normalized or 'unknown'} | "
            f"ES={match.spanish_translation or '(sin traduccion)'} | fuente={match.source}"
        )

    def action_menu_up(self) -> None:
        self._move_menu_focus(-1)

    def action_menu_down(self) -> None:
        self._move_menu_focus(1)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "show_words":
            self._set_game_mode(False)
            self._toggle_form(False)
            self._editing_word_id = None
            self._set_results_document_mode(False)
            try:
                subtitles = self.query(".panel-subtitle")
                if subtitles:
                    subtitles.last().update("Feedback + vocabulario guardado")
            except Exception:
                pass
            self._refresh_table()
            self._set_message("Listado actualizado desde la base de datos.")
            return

        if button_id == "show_form":
            self._set_game_mode(False)
            self._clear_form()
            self._toggle_form(True)
            self._set_results_document_mode(False)
            self._set_message(
                "Busca la palabra en catalogo, precarga traduccion/POS y luego agrega ejemplos EN/ES."
            )
            return

        if button_id == "lookup_catalog_word":
            self._lookup_catalog_and_prefill()
            self._set_message(
                "Busqueda en catalogo completada. Si existe, se precarga la traduccion y se usara su POS al guardar."
            )
            return

        if button_id == "show_game":
            self._set_game_mode(True)
            self._start_next_game_round()
            return

        if button_id == "show_rules":
            self._set_game_mode(False)
            self._show_document_text(RULES_TEXT)
            return

        if button_id == "show_tenses":
            self._set_game_mode(False)
            self._show_document_text(TENSES_TEXT)
            return

        if button_id == "show_pos_mapping":
            self._set_game_mode(False)
            self._show_document_text(build_dictionary_pos_mapping_help_text())
            return

        if button_id == "save_word":
            self._save_word()
            return

        if button_id == "game_next":
            self._start_next_game_round()
            return

        if button_id == "game_check":
            self._check_game_answer()
            return

        if button_id == "game_exit":
            self._set_game_mode(False)
            self._set_message("Saliste del juego. Puedes seguir editando palabras o revisar reglas.")
            return

        if button_id == "exit":
            self.exit()

    def _save_word(self) -> None:
        english_word = self.query_one("#english_word_input", Input).value.strip()
        spanish_meaning = self.query_one("#spanish_meaning_input", Input).value.strip()
        example_english = self.query_one("#example_english_input", Input).value.strip()
        example_spanish = self.query_one("#example_spanish_input", Input).value.strip()
        editing_word_id = self._editing_word_id

        try:
            catalog_match = self.vocabulary_service.lookup_catalog_word(english_word) if english_word else None
            if editing_word_id:
                word, validation = self.vocabulary_service.update_vocabulary_entry(
                    word_id=editing_word_id,
                    english_word=english_word,
                    spanish_meaning=spanish_meaning,
                    example_english=example_english,
                    example_spanish=example_spanish,
                )
            else:
                word, validation = self.vocabulary_service.create_vocabulary_entry(
                    english_word=english_word,
                    spanish_meaning=spanish_meaning,
                    example_english=example_english,
                    example_spanish=example_spanish,
                )
        except InvalidEnglishExampleError as exc:
            lines = ["No se guardo la palabra: la oracion en ingles tiene errores o avisos criticos."]
            lines.extend(self._format_validation_feedback(exc.validation_result, example_english))
            self._set_message("\n".join(lines))
            return
        except ValueError as exc:
            self._set_message(f"Error: {exc}")
            return
        except IntegrityError:
            self._set_message("Error de base de datos: revisa datos duplicados o llaves.")
            return

        self._refresh_table()
        self._clear_form()
        self._toggle_form(False)
        self._set_results_document_mode(False)

        action_label = "Actualizado" if editing_word_id else "Guardado"
        lines = [f"{action_label}: {word.word} -> {word.traduction}"]
        if catalog_match is not None:
            lines.append(
                f"Catalogo: POS={catalog_match.pos_normalized or 'unknown'} | fuente={catalog_match.source}"
            )
        lines.append("")
        lines.extend(self._format_validation_feedback(validation, example_english))

        self._set_message("\n".join(lines))

    def on_data_table_row_selected(self, event) -> None:
        table = self.query_one("#words_table", DataTable)
        row_index = getattr(event, "cursor_row", None)
        if row_index is None:
            row_index = getattr(table, "cursor_row", None)
        if row_index is None:
            return
        if not isinstance(row_index, int):
            try:
                row_index = int(row_index)
            except Exception:
                return
        if row_index < 0 or row_index >= len(self._table_entries):
            return

        entry = self._table_entries[row_index]
        self._toggle_form(True)
        self._prefill_form_for_entry(entry)
        self._set_message(
            "Modo edicion: actualiza la palabra, ejemplos o traduccion y presiona 'Guardar palabra'."
        )


def main() -> None:
    app = LearnEnglishApp()
    app.run()


if __name__ == "__main__":
    main()
