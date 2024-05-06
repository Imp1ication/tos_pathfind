import random
import copy
import queue
import itertools
from basic import Move, StoneType, Runestone


class TosBoard:
    def __init__(self):
        self.numOfRows = 5
        self.numOfCols = 6
        self.runestones = [
            [Runestone()] * self.numOfCols for row in range(self.numOfRows)
        ]
        self.currentPosition = [0, 0]
        self.previousPosition = self.currentPosition

    def __repr__(self):
        return self.boardToString(self.runestones)

    def boardToString(self, _board):
        string = ""
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = _board[row][col]
                string = string + str(stone)
            string = string + "\n"
        return string

    def initFromRandom(self):
        for rowIdx, colIdx in itertools.product(
            range(self.numOfRows), range(self.numOfCols)
        ):
            stone = Runestone(random.choice(list(StoneType)))
            self.runestones[rowIdx][colIdx] = stone
        self.currentPosition = [
            random.randrange(self.numOfRows),
            random.randrange(self.numOfCols),
        ]
        self.previousPosition = self.currentPosition
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = "*"

    def initFromFile(self, _filePath):
        with open(_filePath, "r") as fin:
            for lineIdx, line in enumerate(fin):
                tokenList = line.strip().split()
                if len(tokenList) != 6:
                    continue
                for tokenIdx, token in enumerate(tokenList):
                    stone = Runestone()
                    if token == "D":
                        stone = Runestone(StoneType.DARK)
                    if token == "L":
                        stone = Runestone(StoneType.LIGHT)
                    if token == "W":
                        stone = Runestone(StoneType.WATER)
                    if token == "F":
                        stone = Runestone(StoneType.FIRE)
                    if token == "E":
                        stone = Runestone(StoneType.EARTH)
                    if token == "H":
                        stone = Runestone(StoneType.HEALTH)
                    self.runestones[lineIdx][tokenIdx] = stone

    def evaluate(self):
        # determine if the stone would be removed
        board = self.runestones.copy()
        removed = [[StoneType.NONE] * self.numOfCols for row in range(self.numOfRows)]
        total_rm_count = 0
        total_combo = 0

        while True:
            rm_count = 0
            combo = 0

            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols - 2)
            ):
                if board[rowIdx][colIdx].type == StoneType.NONE:
                    continue
                stone1 = board[rowIdx][colIdx]
                stone2 = board[rowIdx][colIdx + 1]
                stone3 = board[rowIdx][colIdx + 2]
                if stone1.type == stone2.type == stone3.type:
                    for delta in range(3):
                        removed[rowIdx][colIdx + delta] = stone1.type

            for colIdx, rowIdx in itertools.product(
                range(self.numOfCols), range(self.numOfRows - 2)
            ):
                if board[rowIdx][colIdx].type == StoneType.NONE:
                    continue
                stone1 = board[rowIdx][colIdx]
                stone2 = board[rowIdx + 1][colIdx]
                stone3 = board[rowIdx + 2][colIdx]
                if stone1.type == stone2.type == stone3.type:
                    for delta in range(3):
                        removed[rowIdx + delta][colIdx] = stone1.type

            # calculate the number of stones removed and change the board
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols)
            ):
                if removed[rowIdx][colIdx] != StoneType.NONE:
                    rm_count += 1
                    board[rowIdx][colIdx] = Runestone()

            if rm_count == 0:
                break

            # calculate the combo, clear removed stones
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols)
            ):
                if removed[rowIdx][colIdx] != StoneType.NONE:
                    combo = combo + 1
                    t = removed[rowIdx][colIdx]
                    q = queue.Queue()
                    q.put((rowIdx, colIdx))
                    while not q.empty():
                        (r, c) = q.get()
                        removed[r][c] = StoneType.NONE
                        if r + 1 < self.numOfRows and removed[r + 1][c] == t:
                            q.put((r + 1, c))
                        if c + 1 < self.numOfCols and removed[r][c + 1] == t:
                            q.put((r, c + 1))
                        if r - 1 >= 0 and removed[r - 1][c] == t:
                            q.put((r - 1, c))
                        if c - 1 >= 0 and removed[r][c - 1] == t:
                            q.put((r, c - 1))

            total_rm_count += rm_count
            total_combo += combo

            # check if stone dropped
            for colIdx in range(self.numOfCols):
                for rowIdx in range(self.numOfRows - 1, 0, -1):
                    if board[rowIdx][colIdx].type == StoneType.NONE:
                        for r in range(rowIdx - 1, -1, -1):
                            if board[r][colIdx].type != StoneType.NONE:
                                board[rowIdx][colIdx] = board[r][colIdx]
                                board[r][colIdx] = Runestone()
                                break

        # print(self.boardToString(board))
        # print("Total Removed: ", total_rm_count)
        # print("Total Combo: ", total_combo)
        return total_rm_count, total_combo

    def calculateScore(self, stones, combo):
        return 100 * ((stones + combo) * 0.25)


if __name__ == "__main__":
    board = TosBoard()
    board.initFromFile("input.txt")
    print(board)

    # print(board)
