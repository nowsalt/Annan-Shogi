"""テキスト表示 (vshogi風の盤面出力)."""

from annan_shogi.core.color import Color
from annan_shogi.core.square import Square
from annan_shogi.state import State

_RANK_LABELS = "ABCDEFGHI"


def format_board(state: State) -> str:
    """盤面をvshogi風のテキストで整形する."""
    lines: list[str] = []

    # 手番
    lines.append(f"Turn: {state.turn}")

    # 後手の持ち駒
    lines.append(f"White: {state.stands[Color.WHITE]!r}")

    # 筋ラベル
    header = "  "
    for f in range(9, 0, -1):
        header += f"  {f} "
    lines.append(header)

    # 盤面
    divider = "  +" + "---+" * 9

    for rank in range(9):
        lines.append(divider)
        row = f"{_RANK_LABELS[rank]} |"
        for file in range(9, 0, -1):
            piece = state.board[Square(file, rank)]
            if piece is None:
                row += "   |"
            else:
                row += piece.to_display() + "|"
        lines.append(row)
    lines.append(divider)

    # 先手の持ち駒
    lines.append(f"Black: {state.stands[Color.BLACK]!r}")

    return "\n".join(lines)
