"""合法手の生成.

安南ルールを適用した合法手生成、王手判定、禁手チェックを行う。
"""

from __future__ import annotations

from annan_shogi.core.board import Board
from annan_shogi.core.color import Color
from annan_shogi.core.move import Move
from annan_shogi.core.piece import HAND_PIECE_TYPES, Piece, PieceType
from annan_shogi.core.square import Square
from annan_shogi.core.stand import Stand
from annan_shogi.rules.annan_rule import get_effective_movements


def generate_moves(
    board: Board, stand: Stand, color: Color
) -> list[Move]:
    """全ての盤上移動と駒打ちの候補手を生成する (擬似合法手)."""
    moves: list[Move] = []
    _generate_board_moves(board, color, moves)
    _generate_drop_moves(board, stand, color, moves)
    return moves


def _generate_board_moves(
    board: Board, color: Color, moves: list[Move]
) -> None:
    """盤上の駒の移動手を生成する."""
    for sq, piece in board.pieces(color):
        move_patterns = get_effective_movements(board, sq, color)

        for directions, slide in move_patterns:
            for df, dr in directions:
                _trace_direction(board, sq, piece, df, dr, slide, color, moves)


def _trace_direction(
    board: Board,
    src: Square,
    piece: Piece,
    df: int,
    dr: int,
    slide: bool,
    color: Color,
    moves: list[Move],
) -> None:
    """1方向をたどり、移動先を候補手に追加する."""
    f, r = src.file, src.rank
    while True:
        f += df
        r += dr
        if not (1 <= f <= 9 and 0 <= r <= 8):
            break  # 盤外

        dst = Square(f, r)
        target = board[dst]

        if target is not None and target.color is color:
            break  # 味方の駒がある → これ以上進めない

        # 成りの判定
        can_promote = _can_promote(piece.piece_type, src, dst, color)
        must_promote = _must_promote(piece.piece_type, dst, color)

        if can_promote:
            moves.append(Move(dst=dst, src=src, promote=True))
        if not must_promote:
            moves.append(Move(dst=dst, src=src, promote=False))

        if target is not None:
            break  # 相手の駒を取った → これ以上進めない
        if not slide:
            break  # スライドしない駒


def _can_promote(piece_type: PieceType, src: Square, dst: Square, color: Color) -> bool:
    """成ることができるかどうか."""
    if not piece_type.can_promote:
        return False
    if color is Color.BLACK:
        return src.rank <= 2 or dst.rank <= 2  # 一〜三段目
    else:
        return src.rank >= 6 or dst.rank >= 6  # 七〜九段目


def _must_promote(piece_type: PieceType, dst: Square, color: Color) -> bool:
    """行きどころのない駒であっても、安南ルールでは成りを強制しない."""
    return False


def _generate_drop_moves(
    board: Board, stand: Stand, color: Color, moves: list[Move]
) -> None:
    """持ち駒を打つ手を生成する."""
    # 歩のある筋を記録 (二歩チェック用)
    pawn_files: set[int] = set()
    for sq, piece in board.pieces(color):
        if piece.piece_type is PieceType.FU:
            pawn_files.add(sq.file)

    for pt in HAND_PIECE_TYPES:
        if not stand.has(pt):
            continue
        for rank in range(9):
            for file in range(1, 10):
                sq = Square(file, rank)
                if board[sq] is not None:
                    continue  # 駒がある場所には打てない

                # 禁手チェック: 二歩のみ (行きどころのない場所にも打てる)
                if pt is PieceType.FU and file in pawn_files:
                    continue

                moves.append(Move(dst=sq, drop=pt))


def is_in_check(board: Board, color: Color) -> bool:
    """指定手番の王が王手されているか."""
    king_sq = board.find_king(color)
    if king_sq is None:
        return False
    return _is_square_attacked(board, king_sq, color.opponent)


def _is_square_attacked(board: Board, target_sq: Square, attacker_color: Color) -> bool:
    """指定マスが攻撃側の駒に攻撃されているか."""
    for sq, piece in board.pieces(attacker_color):
        move_patterns = get_effective_movements(board, sq, attacker_color)

        for directions, slide in move_patterns:
            for df, dr in directions:
                f, r = sq.file, sq.rank
                while True:
                    f += df
                    r += dr
                    if not (1 <= f <= 9 and 0 <= r <= 8):
                        break
                    check_sq = Square(f, r)
                    if check_sq == target_sq:
                        return True
                    if board[check_sq] is not None:
                        break  # 駒がある → これ以上先は利かない
                    if not slide:
                        break
    return False


def get_legal_moves(board: Board, stand: Stand, color: Color) -> list[Move]:
    """合法手のリストを返す.

    擬似合法手から、自玉が王手になる手と打ち歩詰めを除外する。
    """
    pseudo_moves = generate_moves(board, stand, color)
    legal: list[Move] = []

    for move in pseudo_moves:
        # 手を適用して自玉が王手されていないか確認
        new_board = _apply_move_to_board(board, move, color)
        if is_in_check(new_board, color):
            continue

        # 打ち歩詰めチェック
        if move.is_drop and move.drop is PieceType.FU:
            if _is_pawn_drop_mate(new_board, color):
                continue

        legal.append(move)

    return legal


def _apply_move_to_board(board: Board, move: Move, color: Color) -> Board:
    """指し手を盤面にのみ適用した新しいBoardを返す (持ち駒は考慮しない)."""
    new = board.copy()

    if move.is_drop:
        assert move.drop is not None
        new[move.dst] = Piece(move.drop, color)
    else:
        assert move.src is not None
        piece = new[move.src]
        assert piece is not None

        new[move.src] = None
        if move.promote:
            new[move.dst] = Piece(piece.piece_type.promoted, color)
        else:
            new[move.dst] = piece

    return new


def _is_pawn_drop_mate(board: Board, dropper_color: Color) -> bool:
    """打ち歩詰めの判定.

    歩を打った直後の盤面で、相手の王が詰んでいるかチェック。
    """
    opponent = dropper_color.opponent

    # 相手が王手回避できるか確認
    if not is_in_check(board, opponent):
        return False  # 王手ではない

    # 相手の全ての合法手 (簡易: 擬似合法手で王手回避できるか)
    pseudo = generate_moves(board, Stand(), opponent)  # 持ち駒は空で簡易判定
    for m in pseudo:
        new_board = _apply_move_to_board(board, m, opponent)
        if not is_in_check(new_board, opponent):
            return False  # 回避手がある → 詰みではない
    return True  # 回避手なし → 打ち歩詰め
