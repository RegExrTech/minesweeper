import random
import colorama # pip3 install colorama
from colorama import Fore, Back, Style

class Cell():

    def __init__(self, row, col, state = ' '):
        self.row = row
        self.col = col
        self.state = state
        self.chars = ''
        self.hidden = True
        self.flagged = False
        self.numTouchingFlags = 0
        self.neighbors = []

    def getString(self, game_over=False):
        if self.hidden:
            return Back.BLACK + "   " + Style.RESET_ALL + "|"
        if self.flagged == True:
            if game_over:
                return Back.LIGHTWHITE_EX + ' ' + Fore.RED + self.state + ' ' + Style.RESET_ALL  + '|'
            else:
                return ' ' + Fore.RED + 'F' + Style.RESET_ALL + ' |'
        if self.state == '0':
                color = Fore.BLACK
        elif self.state == '1':
                color = Fore.CYAN
        elif self.state == '2':
                color = Fore.GREEN
        elif self.state == '3':
                color = Fore.LIGHTMAGENTA_EX
        elif self.state == '4':
                color = Fore.BLUE
        elif self.state == '5':
                color = Fore.MAGENTA
        elif self.state == '6':
                color = Fore.YELLOW
        elif self.state == '7':
                color = Fore.LIGHTGREEN_EX
        elif self.state == '8':
                color = Fore.BLACK
        else:
                color = Style.RESET_ALL

        return ' ' + color + self.state + Style.RESET_ALL + ' |'


class Board():

    def __init__(self, row, col, numMines):
        self.numMoves = 0
        self.numFlagged = 0
        self.row = row
        self.col = col
        self.numMines = numMines
        self.mat = []
        self.clearMat()
        self.firstMove = True
        self.freeSpaces = (row*col) - numMines
        self.displayBoard()

    def getCell(self, row, col):
        '''Given a coordinate pair, return the corresponding cell'''
        return self.mat[row][col]

    def move(self, command, row, col):
        '''Given a command and cell coordinates, handle the game logic'''

        cell = self.mat[row][col]
        if self.firstMove:  # if it is the first move of the game
            self.freeSpaces -= 1
            self.firstMove = False
            self.makeBoard(row, col)
            self.unhideNeighbors(row, col)
        elif command == 'F' and cell.hidden: # if the flag a spot
            cell.hidden = False
            cell.flagged = True
            self.numFlagged += 1
            self.updateNeighborFlagCount(row, col, 1)
        elif command == 'F' and cell.flagged: # if they unflag a spot
            cell.hidden = True
            cell.flagged = False
            self.numFlagged -= 1
            self.updateNeighborFlagCount(row, col, -1)
        elif command == 'F': # all other F commands are illegal
            print("That was not a legal move!")
        elif command == 'C' and cell.hidden: # if they open a new spot
            cell.hidden = False
            if cell.state == 'M':
                self.unhideBoard()
                self.displayBoard(game_over=True)
                print('You lose')
                return 0
            self.freeSpaces -= 1
        elif command == 'C' and cell.flagged: # if you open a flagged spot
            print("That was not a legal move!")
        elif command == 'C' and not cell.hidden: # if the click an opened spot
            if cell.numTouchingFlags == int(cell.state):
                no_mines_found = self.unhideNeighbors(row, col)
                print(no_mines_found)
                if not no_mines_found:
                    self.unhideBoard()
                    self.displayBoard(game_over=True)
                    print('You lose')
                    return 0
        if self.freeSpaces == 0:
            self.numFlagged = self.numMines
            self.unhideBoard()
            self.displayBoard()
            print("You win!")
            print("Total number of moves taken: " + str(self.numMoves + 1))
            return 0

        self.displayBoard()

        self.numMoves += 1
        return 1


    def unhideBoard(self):
        '''Every cell becomes unhidden and displays the board again.
        useful for when a player beats or loses the game.'''
        for i in range(self.row):
            for j in range(self.col):
                self.mat[i][j].hidden = False


    def unhideNeighbors(self, i, j):
        '''The neighbors of a move are revealed. If any of those neighbors
        have neighbors which need to be revealed, they are added to the queue.
        If any neighbors being revealed are mines, return False
        '''
        l = [[i, j]]
        while(len(l) > 0):
            self.mat[l[0][0]][l[0][1]].hidden = False
            neighbors = getNeighbors(l[0][0], l[0][1], self.row, self.col)
            for pair in neighbors:
                cell = self.mat[pair[0]][pair[1]]
                print(pair, cell.state, cell.flagged)
                if cell.state == "M" and not cell.flagged:
                    return False
                if (pair not in l) and (cell.hidden) and (cell.numTouchingFlags == int(cell.state)):
                    l.append(pair)
            self.showNeighbors(l[0][0], l[0][1])
            l.remove(l[0])
        return True


    def showNeighbors(self, i, j):
        '''For a given cell coordinate pair, make all hidden neighbors unhidden'''
        neighbors = getNeighbors(i, j, self.row, self.col)
        for n in neighbors:
            cell = self.getCell(n[0], n[1])
            if cell.hidden:
                cell.hidden = False
                self.freeSpaces -= 1



    def updateNeighborFlagCount(self, i, j, num):
        '''For a given cell oordinate pair being flagged or unflagged, update
        its neighbors' flag counts by 1 or -1 respectivly'''
        neighbors = getNeighbors(i, j, self.row, self.col)
        for n in neighbors:
            self.mat[n[0]][n[1]].numTouchingFlags += num



    def clearMat(self):
        '''Make a blank matrix. Used to init the board.'''
        self.mat = []
        for i in range(self.row):
            self.mat.append([])
            for j in range(self.col):
                cell = Cell(i, j, ' ')
                self.mat[-1].append(cell)


    def displayBoard(self, game_over=False):
        '''Generate the string to represent the board.'''
        minesMessageLength = 4*self.col + 1
        message = "Mines left: " + str(self.numMines - self.numFlagged)
        minesMessageLength -= len(message)
        leftSpacing = '=' * ((minesMessageLength-2)//2)
        rightSpacing = '=' * (minesMessageLength-2-len(leftSpacing))
        message = leftSpacing + ' ' + message + ' ' + rightSpacing

        board = "\n   " + message
        board += "\n\n    "
        for i in range(self.col):
                board += " " + str(i%10) + "  "
        board += "\n   " +('-'*(4*(self.col))) + '-\n'
        for i in range(self.row):
            board += (" " + str(i%10) + " |")
            for j in range(self.col):
                board += self.getCell(i, j).getString(game_over)
            board += '\n   ' + ('-'*(4*(self.col))) + '-\n'
        print(board)


    def makeBoard(self, i, j):
        '''Given an initial move, make the board for the game. The first move
        should always be a "0". The mines are placed with this in mind.'''
        self.clearMat()
        for x in range(self.numMines):
            while(True):
                row = random.choice(range(self.row))
                col = random.choice(range(self.col))

                if self.mat[row][col].state != 'M' and (not self.checkIfNeighbors(i, j, row, col)):
                    self.mat[row][col].state = 'M'
                    break
        for i in range(self.row):
            for j in range(self.col):
                if self.mat[i][j].state != 'M':
                    numClose = 0
                    neighbors = getNeighbors(i, j, self.row, self.col)
                    for n in neighbors:
                        numClose += self.testForMine(n[0], n[1])
                    self.mat[i][j].state = str(numClose)


    def checkIfNeighbors(self, row1, col1, row2, col2):
        '''Determines if two pairs of cell coordinates are neighbors'''
        if (abs(row1 - row2) < 2) and (abs(col1 - col2) < 2):
            return True


    def testForMine(self, row, col):
        '''Returns 1 if the given cell coordinates represent a Mine'''
        if self.mat[row][col].state == 'M':
            return 1
        else:
            return 0



'''Lambda expression to return a list of coordinate pairs as a list
which represent the neighbors of the given coordinates, with respect
to the limits of the board size (X, Y)'''
getNeighbors = lambda x, y, X, Y : [[x2, y2] for x2 in range(x-1, x+2)
                               for y2 in range(y-1, y+2)
                               if (-1 < x < X and
                                   -1 < y < Y and
                                   (x != x2 or y != y2) and
                                   (-1 < x2 < X) and
                                   (-1 < y2 < Y))]



def main():
    print("\n\nWelcome to Minesweeper!\nPlease select your board size, or choose custom to make a custom board.\n")
    print("[1] Small  (9x9, 10 mines)\n[2] Medium (16x16, 40 mines)\n[3] Large  (16x30, 99 mines)\n[4] Custom")
    choice = getInt("\n>> ")
    if choice == 1:
        row = 9
        col = 9
        mines = 10
    elif choice == 2:
        row = 16
        col = 16
        mines = 40
    elif choice == 3:
        row = 16
        col = 30
        mines = 99
    else:
        while(True):
            print("Please input the following: ")
            row = getInt("  Number of rows: ")
            col = getInt("  Number of colums: ")
            mines = getInt("  Number of mines: ")
            if ((row*col) >= (mines + 9)):
                break
            print(Fore.RED + "Please try again, with fewer mines or a larger board.\n" + Style.RESET_ALL)
    b = Board(row, col, mines)
    status = 1
    print("\nMoves should be done in the following format: [Command] [row] [col]\nCommands take the form of [C] or [F], for 'Click' or 'Flag' respectivly.\n")
    while(status):
        move = input("Please enter your command: ")
        move = move.split()
        if len(move) != 3:
            print(Fore.RED + "Not a valid move, try again." + Style.RESET_ALL)
            continue
        if (isAnInt(move[1]) and isAnInt(move[2])):
            move[1] = int(move[1])
            move[2] = int(move[2])
            if move[1] >= row:
                print(Fore.RED + "Not a valid row selection." + Style.RESET_ALL)
            elif move[2] > col:
                print(Fore.RED + "Not a valid colum selection." + Style.RESET_ALL)
            else:
                command = move[0].upper()
                if command == 'C' or command == 'F':
                    status = b.move(command, move[1], move[2])
                else:
                    print(Fore.RED + "That was not a valid command option. Please try again." + Style.RESET_ALL)

def isAnInt(i):
    '''Tests if a given string input can be cast to an int'''
    try:
        i = int(i)
        return True
    except:
        print(Fore.RED + "That was not a number. Please try again." + Style.RESET_ALL)
        return False

def getInt(message):
    '''Given a message to display to the user, ensure they give an int as
    input'''
    while(True):
        num = input(message)
        try:
            num = int(num)
            return num
        except:
            print(Fore.RED + "That was not a valid number. Please try again.\n" + Style.RESET_ALL)


main()
