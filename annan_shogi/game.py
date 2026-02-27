"""ゲーム進行・SFEN入出力・履歴管理."""

from __future__ import annotations

from typing import Optional, Union

from annan_shogi.core.board import Board
from annan_shogi.core.color import Color
from annan_shogi.core.move import Move
from annan_shogi.core.piece import Piece, PieceType
from annan_shogi.core.square import Square
from annan_shogi.core.stand import Stand
from annan_shogi.display.text_display import format_board
from annan_shogi.rules.initial_position import create_initial_board, create_initial_stands
from annan_shogi.state import Result, State


class Game:
    """安南将棋のゲーム.

    使用例
    ------
    >>> game = Game()
    >>> print(game)
    Turn: BLACK
    White: -
    ...
    >>> game.apply("7g7f")
    >>> game.result
    <Result.ONGOING: 'ONGOING'>
    """

    def __init__(self, sfen: Optional[str] = None) -> None:
        if sfen is not None:
            self._state = _parse_sfen(sfen)
        else:
            board = create_initial_board()
            stands = create_initial_stands()
            self._state = State(board, stands, Color.BLACK)
        self._move_history: list[Move] = []
        self._state_history: list[State] = []
        self._move_count = 1

    # --- プロパティ ---

    @property
    def turn(self) -> Color:
        """現在の手番."""
        return self._state.turn

    @property
    def result(self) -> Result:
        """ゲーム結果."""
        return self._state.result

    @property
    def board(self) -> Board:
        """現在の盤面."""
        return self._state.board

    @property
    def state(self) -> State:
        """現在の状態."""
        return self._state

    def stand(self, color: Color) -> dict[PieceType, int]:
        """指定手番の持ち駒."""
        return self._state.stands[color].to_dict()

    def in_check(self) -> bool:
        """現在の手番の王が王手されているか."""
        return self._state.in_check()

    def ply(self) -> int:
        """開始からの手数."""
        return len(self._move_history)

    # --- 操作 ---

    def apply(self, move: Union[Move, str, list]) -> "Game":
        """指し手を適用する.

        引数
        ----
        move : Move, str, or list
            指し手 or SFEN文字列 or それらのリスト
        """
        if isinstance(move, list):
            for m in move:
                self.apply(m)
            return self

        if isinstance(move, str):
            move = Move.from_sfen(move)

        self._state_history.append(self._state)
        self._move_history.append(move)
        self._state = self._state.apply_move(move)
        self._move_count += 1
        return self

    def undo(self) -> "Game":
        """1手戻す."""
        if not self._state_history:
            raise ValueError("これ以上戻せません")
        self._state = self._state_history.pop()
        self._move_history.pop()
        self._move_count -= 1
        return self

    def resign(self) -> "Game":
        """投了."""
        if self._state.turn is Color.BLACK:
            self._state.result = Result.WHITE_WIN
        else:
            self._state.result = Result.BLACK_WIN
        return self

    def get_legal_moves(self) -> list[Move]:
        """合法手のリストを返す."""
        if self._state.result is not Result.ONGOING:
            return []
        return self._state.get_legal_moves()

    def is_legal(self, move: Union[Move, str]) -> bool:
        """指定の手が合法かどうか."""
        if isinstance(move, str):
            move = Move.from_sfen(move)
        return move in self.get_legal_moves()

    # --- SFEN ---

    def to_sfen(self) -> str:
        """現在の状態をSFEN文字列で返す."""
        return _to_sfen(self._state, self._move_count)

    # --- 表示 ---

    def __str__(self) -> str:
        if self._state.result is not Result.ONGOING:
            return f"{self._state.result.value}\n{format_board(self._state)}"
        return format_board(self._state)

    def __repr__(self) -> str:
        return f'Game(sfen="{self.to_sfen()}")'


# --- SFEN パーサ / シリアライザ ---

_SFEN_PIECE_MAP: dict[str, PieceType] = {
    "P": PieceType.FU, "L": PieceType.KY, "N": PieceType.KE,
    "S": PieceType.GI, "G": PieceType.KI, "B": PieceType.KA,
    "R": PieceType.HI, "K": PieceType.OU,
    "+P": PieceType.TO, "+L": PieceType.NY, "+N": PieceType.NK,
    "+S": PieceType.NG, "+B": PieceType.UM, "+R": PieceType.RY,
}

_PIECE_TO_SFEN: dict[PieceType, str] = {
    PieceType.FU: "P", PieceType.KY: "L", PieceType.KE: "N",
    PieceType.GI: "S", PieceType.KI: "G", PieceType.KA: "B",
    PieceType.HI: "R", PieceType.OU: "K",
    PieceType.TO: "+P", PieceType.NY: "+L", PieceType.NK: "+N",
    PieceType.NG: "+S", PieceType.UM: "+B", PieceType.RY: "+R",
}


def _parse_sfen(sfen: str) -> State:
    """SFEN文字列をパースしてStateを返す."""
    parts = sfen.split()
    board_str = parts[0]
    turn_str = parts[1] if len(parts) > 1 else "b"
    hand_str = parts[2] if len(parts) > 2 else "-"

    board = _parse_board(board_str)
    turn = Color.BLACK if turn_str == "b" else Color.WHITE
    stands = _parse_hands(hand_str)

    return State(board, stands, turn)


def _parse_board(board_str: str) -> Board:
    """SFEN盤面文字列をパースする."""
    board = Board()
    ranks = board_str.split("/")
    for rank_idx, rank_str in enumerate(ranks):
        file = 9
        i = 0
        while i < len(rank_str):
            ch = rank_str[i]
            if ch.isdigit():
                file -= int(ch)
                i += 1
            elif ch == "+":
                # 成り駒
                key = rank_str[i:i + 2]
                upper_key = "+" + key[1].upper()
                pt = _SFEN_PIECE_MAP[upper_key]
                color = Color.BLACK if key[1].isupper() else Color.WHITE
                board[Square(file, rank_idx)] = Piece(pt, color)
                file -= 1
                i += 2
            else:
                key = ch.upper()
                pt = _SFEN_PIECE_MAP[key]
                color = Color.BLACK if ch.isupper() else Color.WHITE
                board[Square(file, rank_idx)] = Piece(pt, color)
                file -= 1
                i += 1
    return board


def _parse_hands(hand_str: str) -> dict[Color, Stand]:
    """SFEN持ち駒文字列をパースする."""
    stands = {Color.BLACK: Stand(), Color.WHITE: Stand()}
    if hand_str == "-":
        return stands

    i = 0
    while i < len(hand_str):
        count = 0
        while i < len(hand_str) and hand_str[i].isdigit():
            count = count * 10 + int(hand_str[i])
            i += 1
        if count == 0:
            count = 1
        if i < len(hand_str):
            ch = hand_str[i]
            color = Color.BLACK if ch.isupper() else Color.WHITE
            pt = _SFEN_PIECE_MAP[ch.upper()]
            for _ in range(count):
                stands[color].add(pt)
            i += 1
    return stands


def _to_sfen(state: State, move_count: int) -> str:
    """StateをSFEN文字列に変換する."""
    board_str = _board_to_sfen(state.board)
    turn_str = "b" if state.turn is Color.BLACK else "w"
    hand_str = _hands_to_sfen(state.stands)
    return f"{board_str} {turn_str} {hand_str} {move_count}"


def _board_to_sfen(board: Board) -> str:
    """盤面をSFEN文字列に変換する."""
    ranks: list[str] = []
    for rank in range(9):
        rank_str = ""
        empty = 0
        for file in range(9, 0, -1):
            piece = board[Square(file, rank)]
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    rank_str += str(empty)
                    empty = 0
                sfen_char = _PIECE_TO_SFEN[piece.piece_type]
                if piece.color is Color.WHITE:
                    if sfen_char.startswith("+"):
                        sfen_char = "+" + sfen_char[1:].lower()
                    else:
                        sfen_char = sfen_char.lower()
                rank_str += sfen_char
        if empty > 0:
            rank_str += str(empty)
        ranks.append(rank_str)
    return "/".join(ranks)


def _hands_to_sfen(stands: dict[Color, Stand]) -> str:
    """持ち駒をSFEN文字列に変換する."""
    result = ""
    for color in [Color.BLACK, Color.WHITE]:
        for pt, count in stands[color].to_dict().items():
            if count > 0:
                sfen_char = _PIECE_TO_SFEN[pt]
                if color is Color.WHITE:
                    sfen_char = sfen_char.lower()
                if count > 1:
                    result += str(count)
                result += sfen_char
    return result if result else "-"
