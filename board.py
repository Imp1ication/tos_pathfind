import random
import copy
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
        output = ""
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                output = output + str(stone)
            output = output + "\n"
        return output

    def _swap(self, _pos1, _pos2):
        swapTmp = self.runestones[_pos1[0]][_pos1[1]]
        self.runestones[_pos1[0]][_pos1[1]] = self.runestones[_pos2[0]][_pos2[1]]
        self.runestones[_pos2[0]][_pos2[1]] = swapTmp

    def initFromRandom(self):
        for rowIdx in range(self.numOfRows):
            for colIdx in range(self.numOfCols):
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

    def setCurrentPosition(self, _pos):
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = " "
        self.currentPosition = _pos
        self.previousPosition = self.currentPosition
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = "*"

    def getSuccessorList(self):
        successorList = list()
        for move in list(Move):
            newPosition = [sum(z) for z in zip(list(move.value), self.currentPosition)]
            if newPosition == self.previousPosition:
                continue
            if (
                0 <= newPosition[0] < self.numOfRows
                and 0 <= newPosition[1] < self.numOfCols
            ):
                newBoard = TosBoard()
                newBoard.runestones = [copy.copy(row) for row in self.runestones]
                newBoard.currentPosition = newPosition
                newBoard.previousPosition = self.currentPosition
                newBoard._swap(newPosition, self.currentPosition)
                successorList.append((newBoard, move))
        return successorList

    def evaluate_board(self):
        return 0


if __name__ == "__main__":
    board = TosBoard()
    board.initFromFile("input.txt")

    print(board)
