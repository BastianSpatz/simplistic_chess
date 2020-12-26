import pygame as p
import os 
import random
import sys
import engine
import Ai

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

def highlight_in_check(screen, gamestate):
    if gamestate.in_check():
        if gamestate.whiteToMove:
            row, col = gamestate.whitheKingSq
        elif not gamestate.whiteToMove:
            row, col = gamestate.blackKingSq
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("red"))
        screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))

def highlight_last_move(screen, gamestate):
    if len(gamestate.moveLog) != 0:
        lastMove = gamestate.moveLog[-1]
        rowStart = lastMove.startRow
        colStart = lastMove.startCol
        rowEnd = lastMove.endRow
        colEnd = lastMove.endCol
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color("green"))
        screen.blit(s, (colStart*SQ_SIZE, rowStart*SQ_SIZE))
        screen.blit(s, (colEnd*SQ_SIZE, rowEnd*SQ_SIZE))

def draw_gamestate(screen, gamestate, squareSelected, allMoves):
    if len(allMoves) != 0:
        draw_board(screen) #draw the squares
        highlight_last_move(screen, gamestate)
        highlight_square(screen, gamestate, squareSelected, allMoves) #highlight the squares
        highlight_in_check(screen, gamestate)
        draw_pieces(screen, gamestate.board) #draw pieces ontop of screen
    else:
        draw_replay(screen, gamestate)

def draw_replay(screen, gamestate):
    p.font.init() # you have to call this at the start, 
    myfont = p.font.SysFont('arial', 30)
    if gamestate.checkmate:
        textsurface = myfont.render('Checkmate.', True, (220, 0, 0))
    elif gamestate.stalemate:
        textsurface = myfont.render('Stalemate.', True, (220, 0, 0))
    screen.blit(textsurface, (WIDTH // 8, HEIGHT // 4))
    textsurface = myfont.render('Press r to play again.', True, (220, 0, 0))
    screen.blit(textsurface, (WIDTH // 8, HEIGHT // 2))

def main():
    playAgainstAi = True
    p.init
    p.font.init()
    
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
                    # reset user input
                    for i in range(len(allMoves)):
                        if move == allMoves[i]:
                            gamestate.make_move(allMoves[i])
                            '''
                            Important lesson:
                                I create the move in the main, but i need to execute the equivalent move in my list,
                                since i can't give information like enpassant. These are constructed in the engine.
                            '''
                            if playAgainstAi:
                                value, move = Ai.min_max_search(3, gamestate, "b", alpha = -10**16, beta = 10**16)
                                if move != None:
                                    gamestate.make_move(move)
                            moveMade = True
                            squareSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [squareSelected]
                    
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:
                    gamestate.undo_move()
                    moveMade = True
                elif e.key == p.K_r and playing == False:
                    # weird logic; make play again screen
                    main()
                elif e.key == p.K_SPACE and playing == False:
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
    