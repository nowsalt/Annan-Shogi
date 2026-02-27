"""駒種と駒の定義."""

from enum import Enum

from annan_shogi.core.color import Color


class PieceType(Enum):
    """駒の種類 (成り駒を含む)."""

    # 基本駒
    FU = "FU"    # 歩兵
    KY = "KY"    # 香車
    KE = "KE"    # 桂馬
    GI = "GI"    # 銀将
    KI = "KI"    # 金将
    KA = "KA"    # 角行
    HI = "HI"    # 飛車
    OU = "OU"    # 王将/玉将

    # 成り駒
    TO = "TO"    # と金 (成歩)
    NY = "NY"    # 成香
    NK = "NK"    # 成桂
    NG = "NG"    # 成銀
    UM = "UM"    # 馬 (成角)
    RY = "RY"    # 龍 (成飛)

    @property
    def is_promoted(self) -> bool:
        """成り駒かどうかを返す."""
        return self in _PROMOTED_TYPES

    @property
    def promoted(self) -> "PieceType":
        """成った後の駒種を返す. 成れない駒はValueError."""
        if self in _PROMOTE_MAP:
            return _PROMOTE_MAP[self]
        raise ValueError(f"{self.value} は成れません")

    @property
    def demoted(self) -> "PieceType":
        """成る前の駒種を返す. 成り駒でなければそのまま返す."""
        return _DEMOTE_MAP.get(self, self)

    @property
    def can_promote(self) -> bool:
        """成ることができる駒かどうか."""
        return self in _PROMOTE_MAP

    def to_japanese(self) -> str:
        """日本語の2文字表記を返す."""
        return _JAPANESE_NAMES[self]


# 成りの対応表
_PROMOTE_MAP: dict[PieceType, PieceType] = {
    PieceType.FU: PieceType.TO,
    PieceType.KY: PieceType.NY,
    PieceType.KE: PieceType.NK,
    PieceType.GI: PieceType.NG,
    PieceType.KA: PieceType.UM,
    PieceType.HI: PieceType.RY,
}

_DEMOTE_MAP: dict[PieceType, PieceType] = {v: k for k, v in _PROMOTE_MAP.items()}

_PROMOTED_TYPES: set[PieceType] = set(_DEMOTE_MAP.keys())

# 日本語表記
_JAPANESE_NAMES: dict[PieceType, str] = {
    PieceType.FU: "歩", PieceType.KY: "香", PieceType.KE: "桂",
    PieceType.GI: "銀", PieceType.KI: "金", PieceType.KA: "角",
    PieceType.HI: "飛", PieceType.OU: "王",
    PieceType.TO: "と", PieceType.NY: "杏", PieceType.NK: "圭",
    PieceType.NG: "全", PieceType.UM: "馬", PieceType.RY: "龍",
}

# 持ち駒にできる駒種 (成り駒でない基本駒、王将を除く)
HAND_PIECE_TYPES: list[PieceType] = [
    PieceType.HI, PieceType.KA, PieceType.KI, PieceType.GI,
    PieceType.KE, PieceType.KY, PieceType.FU,
]


class Piece:
    """盤上の駒 (駒種 + 手番)."""

    __slots__ = ("piece_type", "color")

    def __init__(self, piece_type: PieceType, color: Color) -> None:
        self.piece_type = piece_type
        self.color = color

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Piece):
            return NotImplemented
        return self.piece_type == other.piece_type and self.color == other.color

    def __hash__(self) -> int:
        return hash((self.piece_type, self.color))

    def __repr__(self) -> str:
        sign = "+" if self.color is Color.BLACK else "-"
        return f"{sign}{self.piece_type.value}"

    def to_display(self) -> str:
        """盤面表示用の3文字表記を返す (例: '+FU', '-KA')."""
        sign = "+" if self.color is Color.BLACK else "-"
        return f"{sign}{self.piece_type.value}"
