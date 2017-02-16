# coding: utf-8

# In[1]:

import sys
import Board

from PyQt5.QtWidgets import (QWidget, QApplication, QFrame, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout)
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer
import time
import Player


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.board = GUIBoard()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 1000, 600)
        self.setWindowTitle("Board Test")

        start_btn = QPushButton("start")
        start_btn.clicked.connect(self.board.start)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.board.init_board)

        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(self.board.pause)

        vbox_btn = QVBoxLayout()
        vbox_btn.addStretch(1)
        vbox_btn.addWidget(pause_btn)
        vbox_btn.addWidget(start_btn)
        vbox_btn.addWidget(reset_btn)

        vbox_board = QVBoxLayout()
        vbox_board.addWidget(self.board)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_board)
        hbox.addLayout(vbox_btn)

        self.setLayout(hbox)

        self.show()


class GUIBoard(QFrame):
    """盤面のクラス"""

    # Class Constant
    BOARD_SIZE = 500

    def __init__(self):
        """盤面の初期化。完全ランダムで埋める.Playerの選択も"""
        super().__init__()

        self.init_ui()
        self.init_board()

    def init_board(self):
        self.Board = Board.Board()
        self.player = Player.MonteCarloSecond(second=0.5)
        self.ispaused = True
        self.resize(500, 500)
        self.Board_drawn = self.Board
        self.drop_timer = QTimer(self)
        self.drop_timer.setInterval(200)
        self.drop_timer.timeout.connect(self.draw_dropped)

    def step(self):
        """step one turn"""
        if not self.ispaused:  # ポーズ中でなければすすめる
            if not self.Board.is_game_end():
                self.timer.stop()
                next_c = self.player.next_cell(self.Board)

                # draw before_drop
                self.Board_drawn = self.Board.select_cell(next_c, return_board_before_drop=True)
                self.drop_timer.start()

                # draw after_drop
                self.timer.start()
                self.update()

            else:
                print(self.Board.turn_number)
                self.timer.stop()
                self.ispaused = True

    def draw_dropped(self):
        """Boardをおとした後の盤面を表示する"""
        self.drop_timer.stop()
        self.Board_drawn = self.Board
        self.update()

    def start(self):
        """AIをスタートする"""
        self.ispaused = False
        self.timer = QTimer(self)
        self.timer.setInterval(300)

        self.timer.timeout.connect(self.step)

        self.timer.start()

    def pause(self):
        """AIをストップする"""
        self.ispaused = True
        self.timer.stop()

    def mousePressEvent(self, event):
        """when mouse clicked"""
        self.mouse_step(event.x(), event.y())

    def mouse_step(self, x, y):
        """select cell which is clicked by mouse"""
        cell = 0
        cell_size = self._get_cell_size()
        for i in range(Board.TABLE_SIZE):
            for j in range(Board.TABLE_SIZE):
                if j * cell_size <= x < (j + 1) * cell_size:
                    if i * cell_size <= y < (i + 1) * cell_size:
                        cell = (i, j)
        if cell in self.Board.selectable_list():
            if not self.Board.is_game_end():
                next_c = cell

                self.Board_drawn = self.Board.select_cell(next_c, return_board_before_drop=True)
                self.drop_timer.start()
                self.update()

    def init_ui(self):
        """GUIBoardのUIの初期化"""
        self.resize(GUIBoard.BOARD_SIZE, GUIBoard.BOARD_SIZE)

    def _get_cell_size(self):
        """それぞれのマスの大きさをピクセル数で返す"""
        return 500 // Board.TABLE_SIZE

    def paintEvent(self, event):
        print("QpainterCalled")

        self._draw_board(self.Board_drawn)

    def _draw_a_cell(self, painter, i, j, value):
        """Draw cell(i, j), value is the number of the cell"""
        colorTable = ["white", 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00, "black", "green", "yellow", "orange"]

        color = QColor(colorTable[value])
        painter.fillRect(j * self._get_cell_size(), i * self._get_cell_size(), self._get_cell_size() - 1,
                         self._get_cell_size() - 1, color)

        font = QFont("Times", 40)
        painter.setFont(font)
        pen_color = QColor("white")
        painter.setPen(pen_color)
        painter.drawText(j * self._get_cell_size(), i * self._get_cell_size(), self._get_cell_size() - 1,
                         self._get_cell_size() - 1,
                         Qt.AlignCenter, str(value))

    def _draw_board(self, board):
        painter = QPainter(self)
        for i in range(Board.TABLE_SIZE):
            for j in range(Board.TABLE_SIZE):
                self._draw_a_cell(painter, i, j, board.board[i][j])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
