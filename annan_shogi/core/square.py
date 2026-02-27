"""9x9盤面のマス目定義."""

from __future__ import annotations

from annan_shogi.core.color import Color

# 筋 (file): 1〜9 (右から左)
# 段 (rank): a〜i (上から下)
_RANK_CHARS = "abcdefghi"


class Square:
    """マス目座標 (file: 1-9, rank: 0-8).

    file は将棋の筋 (右が1, 左が9)。
    rank は内部的に 0=一段目(a) 〜 8=九段目(i)。
    """

    __slots__ = ("file", "rank")

    def __init__(self, file: int, rank: int) -> None:
        if not (1 <= file <= 9 and 0 <= rank <= 8):
            raise ValueError(f"範囲外の座標: file={file}, rank={rank}")
        self.file = file
        self.rank = rank

    @classmethod
    def from_sfen(cls, s: str) -> Square:
        """SFEN形式 (例: '7g') からSquareを生成."""
        file = int(s[0])
        rank = _RANK_CHARS.index(s[1])
        return cls(file, rank)

    def to_sfen(self) -> str:
        """SFEN形式の文字列を返す (例: '7g')."""
        return f"{self.file}{_RANK_CHARS[self.rank]}"

    def below(self, color: Color) -> Square | None:
        """手番から見た「直下」のマスを返す.

        先手(BLACK)の直下 = rank+1 (盤面で下方向)
        後手(WHITE)の直下 = rank-1 (盤面で上方向)
        盤外ならNoneを返す。
        """
        if color is Color.BLACK:
            new_rank = self.rank + 1
        else:
            new_rank = self.rank - 1
        if 0 <= new_rank <= 8:
            return Square(self.file, new_rank)
        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Square):
            return NotImplemented
        return self.file == other.file and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.file, self.rank))

    def __repr__(self) -> str:
        return f"SQ_{self.file}{_RANK_CHARS[self.rank].upper()}"


def all_squares() -> list[Square]:
    """全81マスのリストを返す (9a〜1i の順)."""
    return [Square(f, r) for r in range(9) for f in range(9, 0, -1)]
