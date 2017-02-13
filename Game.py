# coding: utf-8


import copy
import Board
import Player
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput


# In[10]:

class Game(object):
    """Gameをプレイするクラス。プレイヤーを簡単にかえられるようにする。結果を表示できるようにする。"""

    def __init__(self, player):
        """初期化。playerにplayerのインスタンスをいれる。"""
        self.player = player

    def play(self, show=False, result=True, board=False):
        """実際にプレーをする。(ゲーム後の盤面,終了時のTurn数,最高の数字)をタプルで出力する。
        showがTrueの時はそれぞれの盤面とその時に何を選んだかを表示する。
        resultがTrueの時は終了後のみ盤面と最高の数字を表示する。
        また、boardを指定した場合、始めの局面がboardから始まる"""
        game_board = Board.Board()
        if board:
            game_board.board = copy.deepcopy(board.board)  # boardを指定した場合には始めの盤面がboardから始める。
        n = 0
        while n < 100000:
            if not game_board.is_game_end():
                # ゲームが続く場合
                if show:
                    print("Turn", game_board.turn_number)
                    game_board.print_board()
                else:
                    pass

                next_c = self.player.next_cell(game_board)
                if next_c is False:
                    print(u"中断されました")
                    return game_board.board, game_board.turn_number, game_board.max_board()

                else:
                    pass
                game_board.select_cell(next_c)
                n += 1
                if show:
                    print(next_c)
                else:
                    pass
            else:
                if result:
                    print("play over!")
                    print("Turn" + str(game_board.turn_number))
                    game_board.print_board()
                    print("Max number was" + str(game_board.max_board()))  # boardにMaximumを足す)

                else:
                    pass
                return game_board.board, game_board.turn_number, game_board.max_board()


def play():
    history = []
    for i in range(100):
        g = Game(Player.Random())
        history.append(g.play(result=False))
    return history


if __name__ == "__main__":
    graphviz = GraphvizOutput()
    graphviz.output_file = "profile.png"
    with PyCallGraph(output=graphviz):
        play()

