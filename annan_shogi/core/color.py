"""先手/後手を表す列挙型."""

from enum import Enum


class Color(Enum):
    """手番 (先手=BLACK, 後手=WHITE)."""

    BLACK = 0  # 先手
    WHITE = 1  # 後手

    @property
    def opponent(self) -> "Color":
        """相手の手番を返す."""
        return Color.WHITE if self is Color.BLACK else Color.BLACK

    def __str__(self) -> str:
        return "BLACK" if self is Color.BLACK else "WHITE"
