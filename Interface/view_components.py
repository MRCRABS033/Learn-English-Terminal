from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Label, Static

from Interface.view_texts import DEFAULT_MESSAGE


class MenuPanel(Widget):
    def compose(self) -> ComposeResult:
        with Vertical(id="left-panel", classes="panel"):
            yield Label("Menu", classes="panel-title")
            with Vertical(id="menu-buttons"):
                yield Button("Jugar", id="show_game", variant="primary")
                yield Button("Ver palabras", id="show_words")
                yield Button("Agregar palabra", id="show_form")
                yield Button("Reglas", id="show_rules")
                yield Button("Mapa POS", id="show_pos_mapping")
                yield Button("Tiempos", id="show_tenses")
                yield Button("Salir", id="exit", variant="error")


class VocabularyTablePanel(Widget):
    def compose(self) -> ComposeResult:
        with Vertical(id="center-panel", classes="panel"):
            yield Label("Vocabulario", classes="panel-title")
            yield Static("Entradas guardadas", classes="panel-subtitle")
            yield DataTable(id="words_table")


class WordCapturePanel(Widget):
    def compose(self) -> ComposeResult:
        with Vertical(id="right-panel", classes="panel"):
            yield Label("Resultados y Captura", classes="panel-title")
            yield Static("Feedback + formulario", classes="panel-subtitle")
            with Vertical(id="study-view"):
                with VerticalScroll(id="message_scroll"):
                    yield Static(DEFAULT_MESSAGE, id="message")
                with Vertical(id="word-form"):
                    yield Input(placeholder="Palabra en ingles", id="english_word_input")
                    yield Button("Buscar en catalogo", id="lookup_catalog_word")
                    yield Static("Catalogo: sin busqueda", id="catalog_match_info")
                    yield Input(placeholder="Significado en espanol", id="spanish_meaning_input")
                    yield Input(placeholder="Oracion de ejemplo en ingles", id="example_english_input")
                    yield Input(placeholder="Oracion de ejemplo en espanol", id="example_spanish_input")
                    yield Button("Guardar palabra", id="save_word", variant="success")
            with Vertical(id="game-view"):
                yield Static("Learn English Terminal | Juego: adivina traduccion + tiempo", id="game_title")
                yield Static("Presiona 'Siguiente' para empezar.", id="game_status")
                yield Static("-", id="game_word_prompt")
                yield Static("-", id="game_example_prompt")
                yield Input(placeholder="Traduccion al espanol", id="game_translation_input")
                yield Input(placeholder="Tiempo: presente / pasado / futuro", id="game_tense_input")
                with Horizontal(id="game-actions"):
                    yield Button("Comprobar", id="game_check", variant="success")
                    yield Button("Siguiente", id="game_next")
                    yield Button("Salir juego", id="game_exit", variant="warning")
