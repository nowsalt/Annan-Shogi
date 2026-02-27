"""初期配置の定義.

安南将棋の初期配置: 飛車と角行の前の歩 (2筋・8筋) が1マス前進。
"""

from annan_shogi.core.board import Board
from annan_shogi.core.color import Color
from annan_shogi.core.piece import Piece, PieceType
from annan_shogi.core.square import Square
from annan_shogi.core.stand import Stand

# 先手 (BLACK) の一段目 (rank=8, I段)
_BLACK_BACK_RANK = [
    (9, PieceType.KY), (8, PieceType.KE), (7, PieceType.GI),
    (6, PieceType.KI), (5, PieceType.OU), (4, PieceType.KI),
    (3, PieceType.GI), (2, PieceType.KE), (1, PieceType.KY),
]

# 後手 (WHITE) の一段目 (rank=0, A段)
_WHITE_BACK_RANK = [
    (9, PieceType.KY), (8, PieceType.KE), (7, PieceType.GI),
    (6, PieceType.KI), (5, PieceType.OU), (4, PieceType.KI),
    (3, PieceType.GI), (2, PieceType.KE), (1, PieceType.KY),
]


def create_initial_board() -> Board:
    """安南将棋の初期盤面を作成する."""
    board = Board()

    # --- 後手 (WHITE) ---
    # 一段目 (A段, rank=0)
    for file, pt in _WHITE_BACK_RANK:
        board[Square(file, 0)] = Piece(pt, Color.WHITE)

    # 二段目 (B段, rank=1): 飛車(8筋)と角(2筋)
    board[Square(8, 1)] = Piece(PieceType.HI, Color.WHITE)
    board[Square(2, 1)] = Piece(PieceType.KA, Color.WHITE)

    # 三段目 (C段, rank=2): 歩 (2筋と8筋を除く)
    for file in range(1, 10):
        if file not in (2, 8):
            board[Square(file, 2)] = Piece(PieceType.FU, Color.WHITE)

    # 2筋と8筋の歩は1マス前進 → D段 (rank=3)
    board[Square(2, 3)] = Piece(PieceType.FU, Color.WHITE)
    board[Square(8, 3)] = Piece(PieceType.FU, Color.WHITE)

    # --- 先手 (BLACK) ---
    # 九段目 (I段, rank=8)
    for file, pt in _BLACK_BACK_RANK:
        board[Square(file, 8)] = Piece(pt, Color.BLACK)

    # 八段目 (H段, rank=7): 角(8筋)と飛車(2筋)
    board[Square(8, 7)] = Piece(PieceType.KA, Color.BLACK)
    board[Square(2, 7)] = Piece(PieceType.HI, Color.BLACK)

    # 七段目 (G段, rank=6): 歩 (2筋と8筋を除く)
    for file in range(1, 10):
        if file not in (2, 8):
            board[Square(file, 6)] = Piece(PieceType.FU, Color.BLACK)

    # 2筋と8筋の歩は1マス前進 → F段 (rank=5)
    board[Square(2, 5)] = Piece(PieceType.FU, Color.BLACK)
    board[Square(8, 5)] = Piece(PieceType.FU, Color.BLACK)

    return board


def create_initial_stands() -> dict[Color, Stand]:
    """初期持ち駒 (空) を作成する."""
    return {Color.BLACK: Stand(), Color.WHITE: Stand()}
