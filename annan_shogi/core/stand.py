"""持ち駒の管理."""

from __future__ import annotations

import copy

from annan_shogi.core.piece import HAND_PIECE_TYPES, PieceType


class Stand:
    """持ち駒 (手番ごとに1つ).

    各駒種の所持数を管理する。
    """

    def __init__(self) -> None:
        self._pieces: dict[PieceType, int] = {pt: 0 for pt in HAND_PIECE_TYPES}

    def count(self, piece_type: PieceType) -> int:
        """指定駒種の持ち駒数を返す."""
        return self._pieces.get(piece_type, 0)

    def add(self, piece_type: PieceType) -> None:
        """持ち駒に1枚追加する（成り駒は元に戻す）."""
        base = piece_type.demoted
        if base not in self._pieces:
            raise ValueError(f"{piece_type} は持ち駒にできません")
        self._pieces[base] += 1

    def remove(self, piece_type: PieceType) -> None:
        """持ち駒から1枚消費する."""
        if self._pieces.get(piece_type, 0) <= 0:
            raise ValueError(f"{piece_type} の持ち駒がありません")
        self._pieces[piece_type] -= 1

    def has(self, piece_type: PieceType) -> bool:
        """指定駒種を1枚以上持っているか."""
        return self._pieces.get(piece_type, 0) > 0

    def to_dict(self) -> dict[PieceType, int]:
        """所持数が1以上の駒種の辞書を返す."""
        return {pt: n for pt, n in self._pieces.items() if n > 0}

    def copy(self) -> Stand:
        """コピーを返す."""
        new = Stand()
        new._pieces = copy.copy(self._pieces)
        return new

    def __repr__(self) -> str:
        items = self.to_dict()
        if not items:
            return "-"
        return ",".join(
            pt.value + ("" if n == 1 else f"x{n}")
            for pt, n in items.items()
        )
