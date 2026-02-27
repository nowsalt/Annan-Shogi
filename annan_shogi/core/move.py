"""指し手の表現."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from annan_shogi.core.piece import PieceType
from annan_shogi.core.square import Square


@dataclass(frozen=True)
class Move:
    """指し手.

    盤上の駒を動かす場合: dst, src を指定 (promote=True で成り)
    持ち駒を打つ場合: dst, drop を指定 (src=None)
    """

    dst: Square
    src: Optional[Square] = None
    promote: bool = False
    drop: Optional[PieceType] = None

    def __post_init__(self) -> None:
        if self.src is None and self.drop is None:
            raise ValueError("src か drop のどちらかを指定してください")
        if self.src is not None and self.drop is not None:
            raise ValueError("src と drop は同時に指定できません")
        if self.drop is not None and self.promote:
            raise ValueError("打ち駒は成れません")

    @property
    def is_drop(self) -> bool:
        """持ち駒を打つ手かどうか."""
        return self.drop is not None

    @classmethod
    def from_sfen(cls, s: str) -> Move:
        """SFEN形式の指し手文字列をパース.

        盤上移動: '7g7f' or '7g7f+' (成り)
        駒打ち:  'P*5e'
        """
        if s[1] == "*":
            # 駒打ち: 'P*5e'
            piece_char = s[0]
            dst = Square.from_sfen(s[2:4])
            drop = _SFEN_TO_PIECE_TYPE[piece_char]
            return cls(dst=dst, drop=drop)
        else:
            # 盤上移動: '7g7f' or '7g7f+'
            src = Square.from_sfen(s[0:2])
            dst = Square.from_sfen(s[2:4])
            promote = len(s) > 4 and s[4] == "+"
            return cls(dst=dst, src=src, promote=promote)

    def to_sfen(self) -> str:
        """SFEN形式の文字列を返す."""
        if self.is_drop:
            assert self.drop is not None
            char = _PIECE_TYPE_TO_SFEN[self.drop]
            return f"{char}*{self.dst.to_sfen()}"
        else:
            assert self.src is not None
            s = f"{self.src.to_sfen()}{self.dst.to_sfen()}"
            if self.promote:
                s += "+"
            return s

    def __repr__(self) -> str:
        if self.is_drop:
            return f"Move(drop={self.drop!r}, dst={self.dst!r})"
        parts = f"Move(src={self.src!r}, dst={self.dst!r}"
        if self.promote:
            parts += ", promote=True"
        return parts + ")"


# SFEN用の駒種⇔文字変換
_SFEN_TO_PIECE_TYPE: dict[str, PieceType] = {
    "P": PieceType.FU, "L": PieceType.KY, "N": PieceType.KE,
    "S": PieceType.GI, "G": PieceType.KI, "B": PieceType.KA,
    "R": PieceType.HI, "K": PieceType.OU,
}

_PIECE_TYPE_TO_SFEN: dict[PieceType, str] = {v: k for k, v in _SFEN_TO_PIECE_TYPE.items()}
