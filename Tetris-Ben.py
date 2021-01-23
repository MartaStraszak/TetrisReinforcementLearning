import numpy as np
import pygame, sys, random
from pygame.locals import *
from boardClass import *
from gameControl import *
from drawGame import *
from GameStateForBen import BenState
from agentClass import AgentBen


# mrBen = AgentBen()
#mrBen.trainUsingData('HumanTraining.txt',3)
# mrBen.trainRL(500)
smartBenWeights = np.array([-1.53, 2.03, 0.35, 0.79, 0.80, 0.90, 0.72, 0.85, 0.81, 0.23, 1.72, -0.93, 0.97, -12.85, 3.57, 4.02, -3.62, 3.32])
mrBen = AgentBen(smartBenWeights)

fps=180
windowWidth = 500
windowHeight = 600
fpsClock = pygame.time.Clock()

keyFuse = 0.2
dropSpeed = 0.05

pygame.init()


screen = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Tetris')
drawer = GameDrawer(screen)
game = GameState('Human')
stepCounter = 0
while True:
    stepCounter += 1.0/fps
    screen.fill((204,204,255))
    if game.isGameOver():
        print('Final Score '+str(game.score))
        game = GameState('Human')

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                game.movePiece((0,-1))
                buttonDelay['keyLeft']=1.0/fps
            if event.key == pygame.K_RIGHT:
                game.movePiece((0,1))
                buttonDelay['keyRight']=1.0/fps
            if event.key == pygame.K_UP:
                game.rotatePiece()
            if event.key == pygame.K_DOWN:
                game.movePiece((1,0))
            if event.key == pygame.K_SPACE:
                game.hardDrop()
                
    
            
            
    if stepCounter >= dropSpeed:  
        if game.currentPiecePos == (0,4):
            currBoard = BenState(gameState = game)
            currPieceType = game.currentPiece.type
            qval,action = mrBen.proposeAction(currBoard,currPieceType,epsGreedy=0.00)
            shift,rot = action
            #mrBen.updateWeights(currBoard, currPieceType, action)
            for i in range(rot):
                game.rotatePiece()
            game.movePiece((0,shift))

                
            
                
        game.performStep()
        stepCounter = 0.0
    drawer.drawGame(game)
    pygame.display.update()
    fpsClock.tick(fps)

