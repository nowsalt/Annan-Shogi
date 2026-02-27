"""安南ルールのテスト."""

from annan_shogi.core.board import Board
from annan_shogi.core.color import Color
from annan_shogi.core.piece import Piece, PieceType
from annan_shogi.core.square import Square
from annan_shogi.rules.annan_rule import get_effective_piece_type


def test_no_piece_below():
    """直下に味方駒がない場合、本来の駒種を返す."""
    board = Board()
    sq = Square(5, 5)
    board[sq] = Piece(PieceType.FU, Color.BLACK)

    effective = get_effective_piece_type(board, sq, Color.BLACK)
    assert effective is PieceType.FU


def test_friendly_piece_below():
    """直下に味方の飛車がある場合、歩は飛車の動きを得る."""
    board = Board()
    sq = Square(5, 5)
    below_sq = sq.below(Color.BLACK)

    board[sq] = Piece(PieceType.FU, Color.BLACK)
    board[below_sq] = Piece(PieceType.HI, Color.BLACK)

    effective = get_effective_piece_type(board, sq, Color.BLACK)
    assert effective is PieceType.HI


def test_enemy_piece_below():
    """直下に敵の駒がある場合、本来の動きを保つ."""
    board = Board()
    sq = Square(5, 5)
    below_sq = sq.below(Color.BLACK)

    board[sq] = Piece(PieceType.FU, Color.BLACK)
    board[below_sq] = Piece(PieceType.HI, Color.WHITE)

    effective = get_effective_piece_type(board, sq, Color.BLACK)
    assert effective is PieceType.FU


def test_white_perspective():
    """後手視点: 直下(rank-1)に味方駒がある場合."""
    board = Board()
    sq = Square(5, 5)
    # 後手の直下はrank-1 → rank=4
    below_sq = sq.below(Color.WHITE)

    board[sq] = Piece(PieceType.KE, Color.WHITE)
    board[below_sq] = Piece(PieceType.KA, Color.WHITE)

    effective = get_effective_piece_type(board, sq, Color.WHITE)
    assert effective is PieceType.KA
