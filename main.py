import os
import json
import chess

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup

WOOD_LIGHT = (0.78, 0.57, 0.34, 1)
WOOD_DARK  = (0.36, 0.20, 0.10, 1)
WOOD_FRAME = (0.20, 0.105, 0.055, 1)
GOLD       = (0.96, 0.75, 0.32, 1)
CREAM      = (0.98, 0.91, 0.76, 1)
GREEN      = (0.30, 0.64, 0.36, 1)
RED        = (0.78, 0.22, 0.18, 1)
BG         = (0.10, 0.075, 0.06, 1)

SYMBOLS = {
    chess.KING: "♔", chess.QUEEN: "♕", chess.ROOK: "♖",
    chess.BISHOP: "♗", chess.KNIGHT: "♘", chess.PAWN: "♙"
}
VALUES = {
    chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
    chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
}

def piece_symbol(piece):
    if not piece:
        return ""
    symbol = SYMBOLS.get(piece.piece_type, "")
    return symbol if piece.color == chess.WHITE else symbol.lower()

class HomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(14))
        layout.add_widget(Widget())
        layout.add_widget(Label(
            text="[b]AJEDREZ DE MADERA[/b]", markup=True,
            font_size="30sp", color=GOLD, size_hint_y=None, height=dp(62)
        ))
        layout.add_widget(Label(
            text="Dos jugadores · Un mismo teléfono",
            font_size="16sp", color=CREAM, size_hint_y=None, height=dp(34)
        ))
        layout.add_widget(Widget())
        new_btn = self.make_button("Jugar partida nueva")
        new_btn.bind(on_release=lambda *_: self.app.new_game())
        layout.add_widget(new_btn)
        self.resume_btn = self.make_button("Reanudar partida")
        self.resume_btn.bind(on_release=lambda *_: self.app.resume_game())
        layout.add_widget(self.resume_btn)
        layout.add_widget(Widget())
        layout.add_widget(Label(
            text="Tablero giratorio · Puntuación · Guardado local",
            font_size="12sp", color=(0.8, 0.72, 0.6, 1),
            size_hint_y=None, height=dp(30)
        ))
        self.add_widget(layout)

    def make_button(self, title):
        return Button(
            text=title, size_hint_y=None, height=dp(54), font_size="18sp",
            color=CREAM, background_normal="", background_down="",
            background_color=WOOD_DARK
        )

class GameScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(7), spacing=dp(4))

        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        top.add_widget(Label(
            text="[b]AJEDREZ DE MADERA[/b]", markup=True,
            color=GOLD, font_size="18sp", halign="left"
        ))
        pause_btn = Button(
            text="Ⅱ  Pausa", size_hint_x=None, width=dp(100),
            background_normal="", background_color=WOOD_DARK, color=CREAM
        )
        pause_btn.bind(on_release=lambda *_: self.app.pause_menu())
        top.add_widget(pause_btn)
        root.add_widget(top)

        self.status = Label(
            text="Turno: blancas", font_size="15sp",
            size_hint_y=None, height=dp(25), color=CREAM
        )
        root.add_widget(self.status)

        self.board_grid = GridLayout(cols=8, rows=8, spacing=dp(1), size_hint=(1, 1))
        root.add_widget(self.board_grid)

        self.score_label = Label(
            text="", font_size="14sp", size_hint_y=None, height=dp(28), color=GOLD
        )
        root.add_widget(self.score_label)
        self.last_label = Label(
            text="Último movimiento: —", font_size="12sp",
            size_hint_y=None, height=dp(22), color=CREAM
        )
        root.add_widget(self.last_label)
        self.add_widget(root)

    def render_board(self):
        self.board_grid.clear_widgets()
        # El tablero gira 180 grados después de cada jugada para que
        # quien tenga el turno quede visualmente en la parte inferior.
        flipped = self.app.board.turn == chess.BLACK
        for row in range(8):
            for col in range(8):
                if flipped:
                    file_index = 7 - col
                    rank_index = row
                else:
                    file_index = col
                    rank_index = 7 - row
                square = chess.square(file_index, rank_index)
                piece = self.app.board.piece_at(square)
                color = WOOD_LIGHT if (row + col) % 2 == 0 else WOOD_DARK
                if square == self.app.selected:
                    color = GOLD
                elif square in self.app.targets:
                    color = GREEN

                text = piece_symbol(piece)
                btn = SquareButton(
                    text=text, background_color=color, background_normal="",
                    color=(0.08, 0.06, 0.04, 1) if piece and piece.color == chess.WHITE
                          else (0.98, 0.94, 0.84, 1),
                    font_size="30sp" if text else "12sp",
                    square=square
                )
                btn.bind(on_release=self.app.on_square_tap)
                self.board_grid.add_widget(btn)

    def update_labels(self):
        if self.app.board.is_checkmate():
            winner = "Negras" if self.app.board.turn == chess.WHITE else "Blancas"
            status = f"¡Jaque mate! Ganan {winner}"
        elif self.app.board.is_stalemate():
            status = "Tablas por ahogado"
        elif self.app.board.is_insufficient_material() or self.app.board.can_claim_draw():
            status = "Posibles tablas"
        elif self.app.board.is_check():
            status = "¡Jaque! Turno de " + ("blancas" if self.app.board.turn else "negras")
        else:
            status = "Turno: " + ("blancas" if self.app.board.turn else "negras")
        self.status.text = status
        self.score_label.text = (
            f"Blancas: {self.app.scores['white']} puntos     "
            f"Negras: {self.app.scores['black']} puntos"
        )
        if self.app.board.move_stack:
            self.last_label.text = "Último movimiento: " + self.app.board.peek().uci()
        else:
            self.last_label.text = "Último movimiento: —"

class SquareButton(Button):
    def __init__(self, square, **kwargs):
        super().__init__(**kwargs)
        self.square = square

class ChessApp(App):
    def build(self):
        self.title = "Ajedrez de Madera"
        Window.clearcolor = BG
        self.save_path = os.path.join(self.user_data_dir, "partida_guardada.json")
        self.board = chess.Board()
        self.scores = {"white": 0, "black": 0}
        self.selected = None
        self.targets = set()
        self.saved_exists = os.path.exists(self.save_path)
        self.last_saved_state = None

        self.manager = ScreenManager(transition=FadeTransition(duration=0.15))
        self.home = HomeScreen(self, name="home")
        self.game = GameScreen(self, name="game")
        self.manager.add_widget(self.home)
        self.manager.add_widget(self.game)
        self.refresh_home()
        return self.manager

    def refresh_home(self):
        self.home.resume_btn.disabled = not os.path.exists(self.save_path)
        self.home.resume_btn.opacity = 1 if os.path.exists(self.save_path) else 0.5

    def snapshot(self):
        return {
            "fen": self.board.fen(),
            "moves": [move.uci() for move in self.board.move_stack],
            "scores": self.scores,
        }

    def save_game(self):
        data = self.snapshot()
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.saved_exists = True
        self.last_saved_state = data
        self.refresh_home()
        self.show_message("Partida guardada", "La partida quedó guardada en este teléfono.")

    def load_game(self, show_errors=True):
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            board = chess.Board()
            for uci in data.get("moves", []):
                board.push_uci(uci)
            # Si el archivo solo contiene FEN, permite recuperar la posición.
            if not data.get("moves") and data.get("fen"):
                board.set_fen(data["fen"])
            self.board = board
            self.scores = {
                "white": int(data.get("scores", {}).get("white", 0)),
                "black": int(data.get("scores", {}).get("black", 0))
            }
            self.selected = None
            self.targets = set()
            return True
        except Exception:
            if show_errors:
                self.show_message("No se pudo cargar", "El archivo guardado no se pudo abrir.")
            return False

    def new_game(self):
        self.board = chess.Board()
        self.scores = {"white": 0, "black": 0}
        self.selected = None
        self.targets = set()
        self.manager.current = "game"
        self.render_game()

    def resume_game(self):
        if self.load_game():
            self.manager.current = "game"
            self.render_game()

    def render_game(self):
        self.game.render_board()
        self.game.update_labels()

    def on_square_tap(self, button):
        if self.board.is_game_over(claim_draw=True):
            self.show_message("Partida terminada", "Inicia una partida nueva para seguir jugando.")
            return
        square = button.square
        piece = self.board.piece_at(square)

        if self.selected is None:
            if piece and piece.color == self.board.turn:
                self.selected = square
                self.targets = {m.to_square for m in self.board.legal_moves if m.from_square == square}
        else:
            move = chess.Move(self.selected, square)
            # Promoción automática a dama.
            moving_piece = self.board.piece_at(self.selected)
            if moving_piece and moving_piece.piece_type == chess.PAWN:
                rank = chess.square_rank(square)
                if rank in (0, 7):
                    move = chess.Move(self.selected, square, promotion=chess.QUEEN)

            legal_move = next((m for m in self.board.legal_moves
                               if m.from_square == move.from_square
                               and m.to_square == move.to_square
                               and m.promotion == move.promotion), None)
            if legal_move:
                mover = "white" if self.board.turn == chess.WHITE else "black"
                captured = self.board.piece_at(square)
                if self.board.is_en_passant(legal_move):
                    captured = chess.Piece(chess.PAWN, not self.board.turn)
                if captured:
                    self.scores[mover] += VALUES.get(captured.piece_type, 0)
                self.board.push(legal_move)
                if self.board.is_checkmate():
                    self.scores[mover] += 10
                elif self.board.is_stalemate() or self.board.is_insufficient_material():
                    self.scores["white"] += 3
                    self.scores["black"] += 3
                self.selected = None
                self.targets = set()
                self.render_game()
                if self.board.is_game_over(claim_draw=True):
                    self.show_message("Fin de la partida", self.game.status.text)
                return

            if piece and piece.color == self.board.turn:
                self.selected = square
                self.targets = {m.to_square for m in self.board.legal_moves if m.from_square == square}
            else:
                self.selected = None
                self.targets = set()
        self.render_game()

    def pause_menu(self):
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        title = Label(text="[b]Partida pausada[/b]", markup=True, color=GOLD,
                      size_hint_y=None, height=dp(40), font_size="20sp")
        content.add_widget(title)

        resume = self.menu_button("Reanudar partida")
        resume.bind(on_release=lambda *_: popup.dismiss())
        content.add_widget(resume)

        save_exit = self.menu_button("Guardar partida y salir")
        save_exit.bind(on_release=lambda *_: self.save_and_exit(popup))
        content.add_widget(save_exit)

        exit_no_save = self.menu_button("Salir sin guardar")
        exit_no_save.bind(on_release=lambda *_: self.exit_without_saving(popup))
        content.add_widget(exit_no_save)

        popup = Popup(title="", content=content, size_hint=(0.88, None),
                      height=dp(300), auto_dismiss=False,
                      background_color=WOOD_FRAME, separator_color=GOLD)
        popup.open()

    def menu_button(self, title):
        return Button(text=title, size_hint_y=None, height=dp(48),
                      background_normal="", background_color=WOOD_DARK, color=CREAM,
                      font_size="16sp")

    def save_and_exit(self, popup):
        data = self.snapshot()
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.saved_exists = True
        self.refresh_home()
        popup.dismiss()
        self.manager.current = "home"

    def exit_without_saving(self, popup):
        popup.dismiss()
        # No se modifica ni se elimina el guardado anterior.
        self.manager.current = "home"
        self.refresh_home()

    def show_message(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(Label(text=message, color=CREAM, halign="center"))
        close = self.menu_button("Aceptar")
        content.add_widget(close)
        popup = Popup(title=title, content=content, size_hint=(0.86, None),
                      height=dp(190), background_color=WOOD_FRAME,
                      separator_color=GOLD)
        close.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    ChessApp().run()
