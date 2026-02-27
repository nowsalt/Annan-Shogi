"""コア型のテスト."""

from annan_shogi.core.color import Color
from annan_shogi.core.piece import PieceType
from annan_shogi.core.square import Square
from annan_shogi.core.move import Move


def test_color_opponent():
    """手番の反転テスト."""
    assert Color.BLACK.opponent is Color.WHITE
    assert Color.WHITE.opponent is Color.BLACK


def test_piece_promotion():
    """駒の成りテスト."""
    assert PieceType.FU.promoted is PieceType.TO
    assert PieceType.KA.promoted is PieceType.UM
    assert PieceType.TO.demoted is PieceType.FU
    assert PieceType.KI.can_promote is False
    assert PieceType.FU.can_promote is True


def test_square_below():
    """直下のマス取得テスト."""
    sq = Square(7, 3)
    # 先手の直下はrank+1
    assert sq.below(Color.BLACK) == Square(7, 4)
    # 後手の直下はrank-1
    assert sq.below(Color.WHITE) == Square(7, 2)
    # 盤外の場合はNone
    assert Square(5, 0).below(Color.WHITE) is None
    assert Square(5, 8).below(Color.BLACK) is None


def test_move_sfen():
    """指し手のSFEN変換テスト."""
    # 盤上移動
    m1 = Move.from_sfen("7g7f")
    assert m1.src == Square(7, 6)
    assert m1.dst == Square(7, 5)
    assert m1.to_sfen() == "7g7f"

    # 成り
    m2 = Move.from_sfen("7g7f+")
    assert m2.promote is True

    # 駒打ち
    m3 = Move.from_sfen("P*5e")
    assert m3.is_drop
    assert m3.drop is PieceType.FU
    assert m3.to_sfen() == "P*5e"
