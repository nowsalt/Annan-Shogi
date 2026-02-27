"""ゲーム状態: Board + Stand + Turn を統合."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from annan_shogi.core.board import Board
from annan_shogi.core.color import Color
from annan_shogi.core.move import Move
from annan_shogi.core.piece import Piece, PieceType
from annan_shogi.core.stand import Stand
from annan_shogi.rules.legal_moves import get_legal_moves, is_in_check


class Result(Enum):
    """ゲーム結果."""

    ONGOING = "ONGOING"
    BLACK_WIN = "BLACK_WIN"
    WHITE_WIN = "WHITE_WIN"
    DRAW = "DRAW"


class State:
    """ゲーム状態 (盤面 + 持ち駒 + 手番 + 結果)."""

    def __init__(
        self,
        board: Board,
        stands: dict[Color, Stand],
        turn: Color = Color.BLACK,
    ) -> None:
        self.board = board
        self.stands = stands
        self.turn = turn
        self.result = Result.ONGOING

    def copy(self) -> State:
        """状態のコピーを返す."""
        new = State(
            board=self.board.copy(),
            stands={c: s.copy() for c, s in self.stands.items()},
            turn=self.turn,
        )
        new.result = self.result
        return new

    def apply_move(self, move: Move) -> State:
        """指し手を適用した新しいStateを返す."""
        new = self.copy()
        _apply_move(new, move)
        new.turn = new.turn.opponent
        _update_result(new)
        return new

    def get_legal_moves(self) -> list[Move]:
        """現在の手番の合法手リストを返す."""
        return get_legal_moves(self.board, self.stands[self.turn], self.turn)

    def in_check(self) -> bool:
        """現在の手番の王が王手されているか."""
        return is_in_check(self.board, self.turn)


def _apply_move(state: State, move: Move) -> None:
    """State を直接変更する (内部用)."""
    color = state.turn
    board = state.board
    stand = state.stands[color]

    if move.is_drop:
        assert move.drop is not None
        stand.remove(move.drop)
        board[move.dst] = Piece(move.drop, color)
    else:
        assert move.src is not None
        piece = board[move.src]
        assert piece is not None

        # 移動先に相手の駒がある場合、取る
        captured = board[move.dst]
        if captured is not None:
            stand.add(captured.piece_type)

        # 移動元を空にして移動先に配置
        board[move.src] = None
        if move.promote:
            board[move.dst] = Piece(piece.piece_type.promoted, color)
        else:
            board[move.dst] = piece


def _update_result(state: State) -> None:
    """ゲーム結果を更新する (相手の合法手がなければ勝ち)."""
    if state.result is not Result.ONGOING:
        return

    legal = state.get_legal_moves()
    if not legal:
        # 現在の手番に合法手がない → 前の手番の勝ち
        if state.turn is Color.BLACK:
            state.result = Result.WHITE_WIN
        else:
            state.result = Result.BLACK_WIN
