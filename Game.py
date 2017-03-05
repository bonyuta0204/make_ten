# coding: utf-8


import CBoard
import Player



class Game(object):
    """Gameをプレイするクラス。プレイヤーを簡単にかえられるようにする。結果を表示できるようにする。"""

    def __init__(self, player, table_size=4):
        """初期化。playerにplayerのインスタンスをいれる。"""
        self.player = player
        self.table_size = table_size

    def play(self, show=False, result=True, board=False, max_num=3):
        """実際にプレーをする。(ゲーム後の盤面,終了時のTurn数,最高の数字)をタプルで出力する。
        showがTrueの時はそれぞれの盤面とその時に何を選んだかを表示する。
        resultがTrueの時は終了後のみ盤面と最高の数字を表示する。
        また、boardを指定した場合、始めの局面がboardから始まる
        Parameter:
            show: bool
                show board each turn when True
            result: bool
                show result when True
            board; CBoard instanse
                set initial board to designated board
            max_num: int
                initialize board in a way that max number of init board is max_num
        """
        if not board:
            game_board = CBoard.Board(table_size=self.table_size)
            game_board.init_board(max_num=max_num)
        else:
            # game_board = board.clone()  # boardを指定した場合には始めの盤面がboardから始める。
            game_board = board

        while True:
            if not game_board.is_game_end():
                # ゲームが続く場合
                if show:
                    print("Turn", game_board.get_turn_num())
                    game_board.print_board()
                next_c = self.player.next_cell(game_board)
                game_board.select_cell(next_c)
                if show:
                    print(next_c)

            else:
                if result:
                    print("play over!")
                    print("Turn" + str(game_board.get_turn_num()))
                    game_board.print_board()
                    print("Max number was" + str(game_board.max_board()))  # boardにMaximumを足す)

                return (game_board.get_board(), game_board.get_turn_num(),
                        game_board.max_board(), game_board.get_max_adjacent(),
                        game_board.get_sum_adjacent())


def play():
    history = []
    for i in range(100):
        g = Game(Player.Random())
        history.append(g.play(result=False))
    return history


if __name__ == "__main__":
    play()
