"""各駒種の移動方向定義.

方向は (file_delta, rank_delta) のタプルで表現する。
file_delta > 0 は左方向 (筋の数値が増える方向)。
rank_delta > 0 は下方向 (段が進む方向)。

先手(BLACK)視点で定義し、後手はrank_deltaを反転して使用する。
"""

from annan_shogi.core.piece import PieceType

# 方向定数 (file_delta, rank_delta) — 先手視点
UP = (0, -1)
DOWN = (0, 1)
LEFT = (1, 0)
RIGHT = (-1, 0)
UP_LEFT = (1, -1)
UP_RIGHT = (-1, -1)
DOWN_LEFT = (1, 1)
DOWN_RIGHT = (-1, 1)
KNIGHT_LEFT = (1, -2)   # 桂馬左
KNIGHT_RIGHT = (-1, -2)  # 桂馬右


def _flip_rank(direction: tuple[int, int]) -> tuple[int, int]:
    """後手用にrank方向を反転する."""
    return (direction[0], -direction[1])


# --- 駒種ごとの移動定義 ---

# (方向リスト, スライドするか) のタプル
# スライド=True: 飛車・角・香のように複数マス移動可能

_PIECE_MOVES: dict[PieceType, tuple[list[tuple[int, int]], bool]] = {
    PieceType.FU: ([UP], False),
    PieceType.KY: ([UP], True),  # 香車はスライド
    PieceType.KE: ([KNIGHT_LEFT, KNIGHT_RIGHT], False),
    PieceType.GI: ([UP, UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT], False),
    PieceType.KI: ([UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT], False),
    PieceType.OU: ([UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT], False),

    # 成り駒は金将と同じ動き
    PieceType.TO: ([UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT], False),
    PieceType.NY: ([UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT], False),
    PieceType.NK: ([UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT], False),
    PieceType.NG: ([UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT], False),
}

# 角行: 斜め4方向スライド
_BISHOP_SLIDES = [UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]

# 飛車: 縦横4方向スライド
_ROOK_SLIDES = [UP, DOWN, LEFT, RIGHT]

# 馬 (成角): 斜めスライド + 縦横1マス
_HORSE_SLIDES = [UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]
_HORSE_STEPS = [UP, DOWN, LEFT, RIGHT]

# 龍 (成飛): 縦横スライド + 斜め1マス
_DRAGON_SLIDES = [UP, DOWN, LEFT, RIGHT]
_DRAGON_STEPS = [UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]


def get_piece_movements(
    piece_type: PieceType, is_black: bool
) -> list[tuple[list[tuple[int, int]], bool]]:
    """指定駒種の移動パターンを返す.

    戻り値: [(方向リスト, スライドするか), ...] のリスト。
    後手の場合はrank方向を自動反転する。
    """

    def flip_dirs(dirs: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if is_black:
            return dirs
        return [_flip_rank(d) for d in dirs]

    # 角行
    if piece_type is PieceType.KA:
        return [(flip_dirs(_BISHOP_SLIDES), True)]

    # 飛車
    if piece_type is PieceType.HI:
        return [(flip_dirs(_ROOK_SLIDES), True)]

    # 馬 (成角)
    if piece_type is PieceType.UM:
        return [
            (flip_dirs(_HORSE_SLIDES), True),
            (flip_dirs(_HORSE_STEPS), False),
        ]

    # 龍 (成飛)
    if piece_type is PieceType.RY:
        return [
            (flip_dirs(_DRAGON_SLIDES), True),
            (flip_dirs(_DRAGON_STEPS), False),
        ]

    # その他
    if piece_type in _PIECE_MOVES:
        dirs, slide = _PIECE_MOVES[piece_type]
        return [(flip_dirs(dirs), slide)]

    raise ValueError(f"未定義の駒種: {piece_type}")
