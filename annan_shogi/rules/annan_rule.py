"""安南ルール: 直下の味方駒の動きを得る.

安南将棋の核心ルール:
- 味方の駒が縦に隣接している場合、上の駒は直下の駒の動き方に変化する
- 直下に味方の駒がない場合、本来の動きをする
"""

from annan_shogi.core.board import Board
from annan_shogi.core.color import Color
from annan_shogi.core.piece import PieceType
from annan_shogi.core.square import Square
from annan_shogi.rules.movement import get_piece_movements


def get_effective_piece_type(board: Board, square: Square, color: Color) -> PieceType:
    """安南ルールを適用した「実効的な駒種」を返す.

    直下に味方の駒がある場合、直下の駒種を返す。
    直下に味方の駒がない場合、元の駒種を返す。
    """
    piece = board[square]
    if piece is None:
        raise ValueError(f"{square} に駒がありません")

    below_sq = square.below(color)
    if below_sq is not None:
        below_piece = board[below_sq]
        if below_piece is not None and below_piece.color is color:
            return below_piece.piece_type
    return piece.piece_type


def get_effective_movements(
    board: Board, square: Square, color: Color
) -> list[tuple[list[tuple[int, int]], bool]]:
    """安南ルールを適用した移動パターンを返す."""
    effective_type = get_effective_piece_type(board, square, color)
    is_black = color is Color.BLACK
    return get_piece_movements(effective_type, is_black)
