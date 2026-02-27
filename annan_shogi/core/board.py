"""9x9盤面の管理."""

from __future__ import annotations

import copy
from typing import Optional

from annan_shogi.core.color import Color
from annan_shogi.core.piece import Piece, PieceType
from annan_shogi.core.square import Square


class Board:
    """9x9の将棋盤面.

    内部は _grid[rank][file_index] で管理。
    file_index = 9 - file (file=9 が index 0, file=1 が index 8)。
    """

    RANKS = 9
    FILES = 9

    def __init__(self) -> None:
        self._grid: list[list[Optional[Piece]]] = [
            [None] * self.FILES for _ in range(self.RANKS)
        ]

    def _file_to_index(self, file: int) -> int:
        return self.FILES - file

    def __getitem__(self, sq: Square) -> Optional[Piece]:
        """指定マスの駒を返す (なければNone)."""
        return self._grid[sq.rank][self._file_to_index(sq.file)]

    def __setitem__(self, sq: Square, piece: Optional[Piece]) -> None:
        """指定マスに駒を配置する (Noneで空にする)."""
        self._grid[sq.rank][self._file_to_index(sq.file)] = piece

    def copy(self) -> Board:
        """盤面のディープコピーを返す."""
        new = Board()
        new._grid = copy.deepcopy(self._grid)
        return new

    def find_king(self, color: Color) -> Optional[Square]:
        """指定手番の王の位置を返す."""
        for rank in range(self.RANKS):
            for file in range(self.FILES, 0, -1):
                sq = Square(file, rank)
                piece = self[sq]
                if piece and piece.piece_type is PieceType.OU and piece.color is color:
                    return sq
        return None

    def pieces(self, color: Optional[Color] = None):
        """盤上の駒を (Square, Piece) のリストで返す.

        colorを指定すると、その手番の駒のみを返す。
        """
        result: list[tuple[Square, Piece]] = []
        for rank in range(self.RANKS):
            for file in range(self.FILES, 0, -1):
                sq = Square(file, rank)
                piece = self[sq]
                if piece is not None:
                    if color is None or piece.color is color:
                        result.append((sq, piece))
        return result
