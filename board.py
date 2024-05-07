import random
from collections import defaultdict
import math
import copy
import queue
import itertools
from basic import StoneType, Runestone


class TosBoard:
    def __init__(self):
        self.numOfRows = 5
        self.numOfCols = 6
        self.runestones = [
            [Runestone()] * self.numOfCols for _ in range(self.numOfRows)
        ]
        self.currentPosition = [0, 0]
        self.previousPosition = self.currentPosition

    def __repr__(self):
        string = ""
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                string = string + str(stone)
            string = string + "\n"
        return string

    def _dropStones(self):
        stones = self.runestones

        # check if stone dropped
        for colIdx in range(self.numOfCols):
            for rowIdx in range(self.numOfRows - 1, 0, -1):
                if stones[rowIdx][colIdx].type == StoneType.NONE:
                    for r in range(rowIdx - 1, -1, -1):
                        if stones[r][colIdx].type != StoneType.NONE:
                            stones[rowIdx][colIdx] = stones[r][colIdx]
                            stones[r][colIdx] = Runestone()
                            break

    def initFromRandom(self):
        for rowIdx, colIdx in itertools.product(
            range(self.numOfRows), range(self.numOfCols)
        ):
            stone_type = list(StoneType)
            stone_type.remove(StoneType.NONE)

            stone = Runestone(random.choice(stone_type))
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
        tos_state = copy.deepcopy(self)
        stones = tos_state.runestones
        rm_stones = [[StoneType.NONE] * self.numOfCols for _ in range(self.numOfRows)]
        total_rm_count = 0
        total_combo = 0

        while True:
            rm_count = 0
            combo = 0

            # determine if the stone would be removed
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols - 2)
            ):
                if stones[rowIdx][colIdx].type == StoneType.NONE:
                    continue
                stone1 = stones[rowIdx][colIdx]
                stone2 = stones[rowIdx][colIdx + 1]
                stone3 = stones[rowIdx][colIdx + 2]
                if stone1.type == stone2.type == stone3.type:
                    for delta in range(3):
                        rm_stones[rowIdx][colIdx + delta] = stone1.type

            for colIdx, rowIdx in itertools.product(
                range(self.numOfCols), range(self.numOfRows - 2)
            ):
                if stones[rowIdx][colIdx].type == StoneType.NONE:
                    continue
                stone1 = stones[rowIdx][colIdx]
                stone2 = stones[rowIdx + 1][colIdx]
                stone3 = stones[rowIdx + 2][colIdx]
                if stone1.type == stone2.type == stone3.type:
                    for delta in range(3):
                        rm_stones[rowIdx + delta][colIdx] = stone1.type

            # calculate the number of stones removed and update the board
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols)
            ):
                if rm_stones[rowIdx][colIdx] != StoneType.NONE:
                    rm_count += 1
                    stones[rowIdx][colIdx] = Runestone()

            if rm_count == 0:
                break

            # calculate the combo, clear removed stones
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols)
            ):
                if rm_stones[rowIdx][colIdx] != StoneType.NONE:
                    combo = combo + 1
                    t = rm_stones[rowIdx][colIdx]
                    q = queue.Queue()
                    q.put((rowIdx, colIdx))
                    while not q.empty():
                        (r, c) = q.get()
                        rm_stones[r][c] = StoneType.NONE
                        if r + 1 < self.numOfRows and rm_stones[r + 1][c] == t:
                            q.put((r + 1, c))
                        if c + 1 < self.numOfCols and rm_stones[r][c + 1] == t:
                            q.put((r, c + 1))
                        if r - 1 >= 0 and rm_stones[r - 1][c] == t:
                            q.put((r - 1, c))
                        if c - 1 >= 0 and rm_stones[r][c - 1] == t:
                            q.put((r, c - 1))

            total_rm_count += rm_count
            total_combo += combo

            # check if stone dropped
            tos_state._dropStones()

            # print(tos_state)
        # print("Total Removed: ", total_rm_count)
        # print("Total Combo: ", total_combo)
        return total_rm_count, total_combo, tos_state

    def calculateScore(self, stones, combo):
        return 100 * ((stones + combo) * 0.25)

    def calculateDensity(self):
        stone_positions = defaultdict(list)

        # get all stone positions
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                if stone.type is not StoneType.NONE:
                    stone_positions[stone.type].append((row, col))

        # calculate average manhattan distance between stones
        avg_distances = {}

        for stone_type, positions in stone_positions.items():
            total_distance = 0
            num_pairs = 0
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    distance = abs(x1 - x2) + abs(y1 - y2)
                    total_distance += distance
                    num_pairs += 1
            avg_distance = total_distance / num_pairs if num_pairs > 0 else 0
            avg_distances[stone_type] = avg_distance

        # print average distances
        # for stone_type, avg_distance in avg_distances.items():
        #     print(f"Average distance for {stone_type}: {avg_distance}")

        # add up all average distances
        return sum(avg_distances.values())


if __name__ == "__main__":
    board = TosBoard()
    board.initFromFile("input2.txt")

    print(board)
    board.calculateDensity()
