'''
this file will be responsible for handling user input and displaying the current game state
'''
import pygame as p
import numpy as np
import ChessEngine
import ChessAI

WIDTH = HEIGHT = 612
DIMENSION = 8
SQ_SIZE = 512 // DIMENSION
MAX_FPS = 15
IMAGES = {}

#Global ditionary of images:
def loadImages():
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    ai = ChessAI.HeuristicAlphaBetaSearch()
    validMoves = np.array(gs.getValidMoves())
    moveMade = False  #flag var for when a move is made
    loadImages()
    running = True
    sqSelected = ()            #Keep track of the last click of the user (tuple: (row, col))
    playerClicks = []          #Keep track of player clicks (twp tuples: [Sq1, Sq2])
    gameOver = False
    depth = 2
    start = True
    while running:
        for e in p.event.get():
            if start:
                if e.type == p.KEYDOWN:
                    if e.key == p.K_1:
                        depth = 1
                    elif e.key == p.K_2:
                        depth = 2
                    elif e.key == p.K_3:
                        depth = 3
                    start = not start
            else:
                if not gs.whiteToMove:
                    move = ai.alphaBetaSearch(gs, depth)
                    if move != None:
                        gs.makeMove(move)
                    moveMade = True
                elif gs.whiteToMove:
                    if e.type == p.QUIT:
                        running = False
                    elif e.type == p.MOUSEBUTTONDOWN:
                        if not gameOver:
                            location = p.mouse.get_pos()   #(x,y) position of the mouse
                            if location[0] <= 50 or location[1] <= 50 or location[0] >= 565 or location[1] >= 565:
                                continue
                            col = (location[0] - 50)//SQ_SIZE
                            row = (location[1] - 50)//SQ_SIZE
                            if sqSelected == (row, col) :    #the user clicked the same square twice
                                sqSelected = ()  #deselsect
                                playerClicks = []    #clear player clicks
                            else:
                                sqSelected = (row, col)
                                playerClicks.append(sqSelected)
                                if len(playerClicks) == 2:  #after 2nd click
                                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                                    print(move.getChessNotation())
                                    for i in range(len(validMoves)):
                                        if move == validMoves[i]:
                                            gs.makeMove(validMoves[i])
                                            moveMade = True
                                            sqSelected = ()   #reset user clicks
                                            playerClicks = []
                                    if not moveMade:
                                        playerClicks = [sqSelected]
                if e.type == p.KEYDOWN:
                    if e.key == p.K_z:    #undo when 'z' is pressed
                        gs.undoMove()
                        gs.undoMove()
                        moveMade = True
                        gameOver = False
                    if e.key == p.K_x:    #restart game when 'x' is pressed
                        gs.restartGame()
                        sqSelected = ()   #reset user clicks
                        playerClicks = []
                        moveMade = True
                        start = True


        if moveMade:
            validMoves = np.array(gs.getValidMoves())
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black WINS by checkmate!")
            else:
                drawText(screen, "White WINS by checkmate!")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, " Stalemate!")
        if start:
            drawText(screen, "Enter level from 1 to 3")
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):    #selected a piece that can be moved
            #highlight selected squares
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(180)   #transparency value
            s.fill((106, 90, 205))
            screen.blit(s, (c*SQ_SIZE + 50, r*SQ_SIZE +50))
            #highlighting valid moves from that square
            s.set_alpha(80)
            s.fill((255, 0, 230))
            for move in validMoves:
                if r == move.startRow and c == move.startCol:
                    screen.blit(s, (move.endCol * SQ_SIZE + 50, move.endRow * SQ_SIZE + 50))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


#draws the squars on the board. The top left square is light
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    font = p.font.SysFont('Times New Roman', 14)
    font2 = p.font.SysFont('Times New Roman', 16)
    p.draw.rect(screen, ((255,0,230)), p.Rect(48, 48, 516, 516))
    text = font2.render("press 'z' to UNDO move                                                     press 'x' to RESTART game", True,((139, 0, 139)))
    screen.blit(text,(30, 3))
    i = 8
    n = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H"}
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            s = p.draw.rect(screen, color, p.Rect(c*SQ_SIZE + 50, r*SQ_SIZE +50, SQ_SIZE, SQ_SIZE))
            if c % 8 == 0:
                text = font.render(str(i), True,((255,0,230)))
                screen.blit(text,(38, r*SQ_SIZE +70))
                i -= 1
            if r == 7:
                text = font.render(str(n[c]), True, ((255,0,230)))
                screen.blit(text,(c*SQ_SIZE +70, 568))
                i -= 1

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE +50, r*SQ_SIZE +50, SQ_SIZE, SQ_SIZE))

def drawText(screen, text):
    font = p.font.SysFont("Comic Sans MS", 40, True, False)
    textObject = font.render(text, 0, ((255, 0, 255)))
    textLocation = p.Rect(50, 50, 512, 512).move(512/2 - textObject.get_width()/2, 512 / 2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, ((0, 255, 127)))
    screen.blit(textObject, textLocation.move(3, -3))

if __name__ == "__main__":
    main()