import pygame as p
import os 
import random
import sys
import engine

WIDTH = HEIGHT = 512 #some power of 2 scaled to the images
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(os.path.join("Images", piece  + ".png")), (SQ_SIZE, SQ_SIZE))

def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
                color = colors[(row+col)%2]
                p.draw.rect(screen, color, ((col*SQ_SIZE, row*SQ_SIZE), (SQ_SIZE, SQ_SIZE)))

def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col] 
            if piece != "--":
                screen.blit(IMAGES[piece], (col*SQ_SIZE, row*SQ_SIZE))

def highlight_square(screen, gamestate, squareSelected, allMoves):
        if squareSelected != ():
            row, col = squareSelected
            if gamestate.board[row][col][0] == ("w" if gamestate.whiteToMove else "b"):
                s = p.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(p.Color("blue"))
                screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
                s.fill(p.Color("yellow"))
                for move in allMoves:
                    if move.startRow == row and move.startCol == col:
                        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def draw_gamestate(screen, gamestate, squareSelected, allMoves):
    draw_board(screen) #draw the squares
    highlight_square(screen, gamestate, squareSelected, allMoves) #highlight the squares
    draw_pieces(screen, gamestate.board) #draw pieces ontop of screen

def main():
    p.init

    # draw scrren
    screen = p.display.set_mode((WIDTH, HEIGHT))
    screen.fill(p.Color("white"))
    clock = p.time.Clock()

    # pass gamestate
    gamestate = engine.GameState()

    allMoves = gamestate.get_all_valid_moves()
    moveMade = False
    gameover = False

    # load images
    load_images()

    # keep track of user inputs 
    squareSelected = ()
    playerClicks = []

    running = True
    playing = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                position = p.mouse.get_pos()
                row = position[1]//SQ_SIZE
                col = position[0]//SQ_SIZE
                if  squareSelected == (row, col):
                    squareSelected = ()
                    playerClicks = [] 
                else:
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)

                if len(playerClicks) == 2:
                    move = engine.Move(list(playerClicks[0]), list(playerClicks[1]), gamestate.board)
                    squareSelected = ()
                    playerClicks = []
                    if move in allMoves:
                        gamestate.make_move(move) 
                    print(gamestate.whitheKingSq) if gamestate.whiteToMove else print(gamestate.blackKingSq)
                    print('\n')
                    # reset user input
                    moveMade = True
                    
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    gamestate.undo_move()
                    moveMade = True
                if e.key == p.K_r and playing == False:
                    # weird logic; make play again screen
                    main()
                else:
                    running = False
        if moveMade:
            allMoves = gamestate.get_all_valid_moves()
            moveMade = False
            if len(allMoves) == 0:
                playing = False
                
        draw_gamestate(screen, gamestate, squareSelected, allMoves)
        clock.tick(MAX_FPS)
        p.display.flip()

if __name__ == '__main__':
    main()
    