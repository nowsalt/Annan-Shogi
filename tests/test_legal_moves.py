"""合法手生成のテスト."""

from annan_shogi.core.board import Board
from annan_shogi.core.color import Color
from annan_shogi.core.move import Move
from annan_shogi.core.piece import Piece, PieceType
from annan_shogi.core.square import Square
from annan_shogi.core.stand import Stand
from annan_shogi.rules.legal_moves import get_legal_moves, is_in_check
from annan_shogi.rules.initial_position import create_initial_board


def test_initial_legal_moves():
    """初期配置で合法手が生成されることを確認."""
    board = create_initial_board()
    stand = Stand()
    moves = get_legal_moves(board, stand, Color.BLACK)
    assert len(moves) > 0


def test_check_detection():
    """歩が王の前にいる場合、王手と判定される."""
    board = Board()
    board[Square(5, 5)] = Piece(PieceType.OU, Color.BLACK)
    board[Square(5, 4)] = Piece(PieceType.FU, Color.WHITE)

    assert is_in_check(board, Color.BLACK)
    assert not is_in_check(board, Color.WHITE)


def test_annan_check():
    """安南ルールによる王手: 歩の直下に飛車がある場合、歩は飛車の利きで王手できる."""
    board = Board()
    board[Square(5, 5)] = Piece(PieceType.OU, Color.BLACK)
    board[Square(5, 3)] = Piece(PieceType.FU, Color.WHITE)
    board[Square(5, 2)] = Piece(PieceType.HI, Color.WHITE)

    assert is_in_check(board, Color.BLACK)


def test_king_affected_by_annan():
    """王将も安南ルールの影響を受ける: 直下に龍があれは龍の動きになる."""
    board = Board()
    board[Square(5, 5)] = Piece(PieceType.OU, Color.BLACK)
    board[Square(5, 6)] = Piece(PieceType.RY, Color.BLACK)

    moves = get_legal_moves(board, Stand(), Color.BLACK)
    # 王が龍のように前方に2マス以上移動可能
    assert Move(src=Square(5, 5), dst=Square(5, 3)) in moves
