import pygame, sys, os
from random import randint
from galaxian import Galaxian
from rocketship import RocketShip
from states import States
from star import Star
from functions import plusOrMinusOne, removeDestroyed


#-------------------------------------------------------------------------------
#                                 GAME PARAMETERS
#-------------------------------------------------------------------------------
SCREEN_WIDTH = 690
SCREEN_HEIGHT = 740

FPS = 60
X_SPACE = 48 # centre distance between galaxians while in formation
NEW_LIFE_BONUS = 10000

#-------------------------------------------------------------------------------
#                                 GAME FUNCTIONS
#-------------------------------------------------------------------------------    

def updateHiScore():
    global highScore
    
    hiScoreFile = open('hiscore', 'w')
    hiScoreFile.write(str(highScore))
    hiScoreFile.close()




def attackPlayer(galaxians, galaxianAliveArray):
    state = States()
    
    if len(galaxians) > 4:
        availableToDive = []
        
        for f in range(len(galaxians)):
            if galaxians[f].state == state.FORMATION:
                availableToDive.append(f)
        
        if len(availableToDive) > 0:
            randomNumber = randint(0, len(availableToDive) - 1)
            
            # TESTING ONLY
            #if galaxians[availableToDive[randomNumber]].number != 17 and galaxians[availableToDive[randomNumber]].number != 33:
            #    return
            #randomNumber = 17
            
            # set up a formation dive team if a Yellow galaxian has been picked
            if galaxians[availableToDive[randomNumber]].number == 17 or galaxians[availableToDive[randomNumber]].number == 33:
                galaxians[availableToDive[randomNumber]].getTeam(galaxianAliveArray, galaxians)
                #print galaxians[availableToDive[randomNumber]].number
            
            galaxians[availableToDive[randomNumber]].changeState(state.LAUNCHING)
            
    else:
        for f in range(len(galaxians)):
            if galaxians[f].state == state.FORMATION:
                galaxians[f].changeState(state.LAUNCHING)
            elif galaxians[f].state == state.LANDING:
                galaxians[f].changeState(state.DIVING)
                galaxians[f].direction = 270



def exitPauseCheck():
    global gamePaused, gameOver
    
    for gameEvent in pygame.event.get():
        if (gameEvent.type == pygame.QUIT):
            sys.exit()
        if (gameEvent.type == pygame.KEYDOWN):
            if (gameEvent.key == pygame.K_ESCAPE):
                sys.exit()
            if (gameEvent.key == pygame.K_PAUSE):
                gamePaused = not gamePaused
            if (gameOver and gameEvent.key == pygame.K_SPACE):
                pygame.mixer.Sound(os.path.join("sounds", "start.ogg")).play().set_volume(0.2)
                gameOver = False
            # TESTING ONLY
            """
            if (gameEvent.key == pygame.K_BACKSPACE and not gameOver):
                # testing only
                for f in range(len(galaxians)):
                    if (galaxians[f].number != 17 and galaxians[f].number != 11 and galaxians[f].number != 22 and# and !=16
                        galaxians[f].number != 33 and galaxians[f].number != 27 and galaxians[f].number != 38):#and != 32
                        galaxians[f].destroyed = True
                #--------------
                #player.alive = False
                #explosions.append(Explosion(player.x, player.y, FPS, "player"))
            """
            
                
            

# the formation of galaxians is built in this fashion so that a quicker search can be done to 
# find the formation edge every time a galaxian gets destroyed
def buildGalaxians(galaxians):
    randPos = randint(18, SCREEN_WIDTH - (X_SPACE * 9 + 18))
    startFrame = 0
    galaxianFormation = (3, 4, 5, 6, 5, 5, 6, 5, 4, 3)
    counter = 0
    
    for cols in range(10):
        sprite = "blue"
        startFrame = (startFrame + 1) % 3
        for rows in range(galaxianFormation[cols]):
            if rows == 5:
                sprite = "yellow"
                startFrame = 0
            elif rows == 4:
                sprite = "red"
            elif rows == 3:
                sprite = "magenta"
            galaxians.append(Galaxian(sprite, FPS, randPos + cols * X_SPACE, 234 - 34 * rows, 
                                                startFrame, counter, SCREEN_WIDTH, SCREEN_HEIGHT))
            counter += 1
    
    return (randPos - 18, randPos + X_SPACE * 9 + 18)


# every time a galaxian is destroyed the formation left and right edge needs to be found

"""
- minMaxBorder is boolean array of galaxians marked either true/false
- edge was the starting edge (can be either left/right side) position
- counter is starting index of array to search through
- direction indicates the search direction through the array minMaxBorder"""
def getFormationEdge(minMaxBorder, edge, counter, direction):
    galaxianFormation = (3, 4, 5, 6, 5, 5, 6, 5, 4, 3)
    for cols in range(10):
        for rows in range(galaxianFormation[cols]):
            if minMaxBorder[counter]:
                return edge + X_SPACE * cols * direction
            counter += direction


# stops the formation from moving off the screen
def formationEdgeTest(move, minimum, maximum):
    if minimum + move < 0 or maximum + move > SCREEN_WIDTH:
        return -move
    return move

# decrements t, but stops at zero

def decrementTimer(t):
    if t > 0:
        t -= 1
    return t


# stops the formation moving side ways into a laser

def formationMove():
    state = States()
    for f in range(len(galaxians)):
        if galaxians[f].state == state.FORMATION:
            if formationMoveX > 0:
                if int(galaxians[f].x + 21) == player.laser.x:
                    return False
            else:
                if int(galaxians[f].x - 21) == player.laser.x:
                    return False
    return True

def displayInstructions(window, stars):
    global newLife
    exitPauseCheck()
    if gameOver:
        # draw instructions
        window.blit(spriteInstructions, (0,0))
        # player does not exist, so return None
        return None
    
    # put in random stars for starting a new game
    for f in range(30):#70
        stars.append(Star(FPS, SCREEN_WIDTH, SCREEN_HEIGHT))
        stars[f].x = randint(0, SCREEN_WIDTH - 3)
        stars[f].y = randint(0, SCREEN_HEIGHT)
    
    newLife = NEW_LIFE_BONUS
    # initialise player for new game
    return RocketShip(FPS, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 70, "rocketShip.png", "laser_yellow.png")

"""end functions"""

#-------------------------------------------------------------------------------
#                               INITIALISE GAME
#-------------------------------------------------------------------------------
pygame.mixer.pre_init(44100, -16, 16, 2048)
pygame.init()

pygame.display.set_icon(pygame.image.load(os.path.join("images", "icon.png")))
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaxian (1.1.2)")

pygame.mouse.set_visible(False)
gameOver = True
gamePaused = False
newLevel = True
divingTotal = 0
maxDiving = 3

formationMoveX = 0.8 * plusOrMinusOne()

# arrays of objects that need to be controlled
galaxians = []
explosions = []
lasers = []
backgroundStars = []
backgroundStarTimer = 0
bombs = []
floatingScores = []

player = None
newLife = 0



highScore = 0
try:
    hiScoreFile = open('hiscore', 'r')
    highScore = int(hiScoreFile.readline())
    hiScoreFile.close()
except IOError:
    hiScoreFile = open('hiscore', 'w')
    hiScoreFile.write("0")
    hiScoreFile.close()

    





# sprites
spriteInstructions = pygame.image.load(os.path.join("images", "instructions.png"))
spritePaused = pygame.image.load(os.path.join("images", "paused.png"))

# formation movement edge
startingLeftEdge = 0
startingRightEdge = 0
formationLeftEdge = 0
formationRightEdge = 0

# timers
newLevelTimer = FPS * 2
diveTimer = FPS

# text
fontArial = pygame.font.SysFont('arial', 18, True, False)

# colours
c_black = (0,0,0)
c_grey = (40,40,40)


gameTimer = pygame.time.Clock()

state = States()



#=======================================================================================
#
#                                        MAIN GAME LOOP
#
#=======================================================================================

while (True):
    
    #    -------------------------------------------------------------------------------
    #                   DISPLAY INSTRUCTIONS & WAIT FOR GAME START KEY PRESS
    #    -------------------------------------------------------------------------------
    while gameOver:
        gameTimer.tick(FPS)
        #print gameTimer.get_fps()
        window.fill(c_grey)
        player = displayInstructions(window, backgroundStars)
        pygame.display.flip()
    
    
    #    -------------------------------------------------------------------------------
    #                               BUILD NEW WAVE OF GALAXIANS
    #    -------------------------------------------------------------------------------
    if newLevelTimer == 0:
        # get original left and right edge of formation 
        (startingLeftEdge, startingRightEdge) = buildGalaxians(galaxians)
        
        
        # set all galaxians as in existence - a new formation has just been built
        minMaxBorder = [True for f in range(len(galaxians))]
        
        formationLeftEdge = startingLeftEdge
        formationRightEdge = startingRightEdge
        newLevelTimer = FPS * 2
        player.level += 1
        
    #    ------------------------- just the essentials here ----------------------------
    window.fill(c_black)
    gameTimer.tick(FPS)#tick_busy_loop(FPS)
    
    # check if the player wants to pause or terminate the game
    exitPauseCheck()
    

    #    -------------------------------------------------------------------------------
    #                                    MOVE OR PAUSE
    #    -------------------------------------------------------------------------------
    if not gamePaused:
        # TESTING ONLY
        #print gameTimer.get_fps()
        
        for f in range(len(floatingScores)):
            floatingScores[f].move()
        
        # generate background stars
        backgroundStarTimer = (backgroundStarTimer + 1) % (FPS / 3)#8
        if backgroundStarTimer == 0:
            backgroundStars.append(Star(FPS, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        for f in range(len(bombs)):
            bombs[f].move(player, explosions, SCREEN_HEIGHT)
        
        bombs = removeDestroyed(bombs)
        
        # if there are galaxians on the screen then move them
        if len(galaxians) > 0:
            
            #tests for formation meeting the screen edge. negates formationMoveX if found
            formationMoveX = formationEdgeTest(formationMoveX, formationLeftEdge, formationRightEdge)
            
            # this is passed to all the galaxians regardless of what state they are in
            # assumed the formation will not move, but this will be corrected in the IF statement below
            galaxianFormationMove = 0.0
            
            # the formation watches where player laser is. will not move side ways into a laser
            if player.laser.y > 260 or formationMove():
                startingLeftEdge += formationMoveX
                startingRightEdge += formationMoveX
                formationLeftEdge += formationMoveX
                formationRightEdge += formationMoveX
                galaxianFormationMove = formationMoveX
            
            
            upperLimit = 90 - player.level * 10
            if upperLimit < 20:
                upperLimit = 20
            
            diveTimer = decrementTimer(diveTimer)
            if  player.alive and (len(galaxians) <= 4 or 
                                                     (diveTimer == 0 and randint(0, upperLimit) == 0 and 
                                                      divingTotal < maxDiving + player.level / 3)):
                attackPlayer(galaxians, minMaxBorder)
                diveTimer = FPS / player.level
            
            divingTotal = 0
            for f in range(len(galaxians)):
                galaxians[f].move(explosions, galaxianFormationMove, player, bombs, floatingScores)
                # count the number of galaxians diving or getting ready to dive
                if (galaxians[f].state == state.DIVING or galaxians[f].state == state.LAUNCHING or 
                                                            galaxians[f].state == state.FORMATION_DIVING):
                    divingTotal += 1 
            
            # only need to test for a new formation edge when a galaxian is destroyed
            getBoundaryEdge = False
            
            for f in range(len(galaxians)):
                if galaxians[f].destroyed:
                    # do not BREAK. multiple galaxians can be destroyed with a single laser
                    minMaxBorder[galaxians[f].number] = False
                    getBoundaryEdge = True
        
            if getBoundaryEdge:
                formationLeftEdge = getFormationEdge(minMaxBorder, startingLeftEdge, 0, 1)
                formationRightEdge = getFormationEdge(minMaxBorder, startingRightEdge, 45, -1)
            
            galaxians = removeDestroyed(galaxians)
            
        else:
            newLevelTimer = decrementTimer(newLevelTimer)
        
        for f in range(len(backgroundStars)):
            backgroundStars[f].move()
        
        for f in range(len(explosions)):
            explosions[f].move()
        
        backgroundStars = removeDestroyed(backgroundStars)
        explosions = removeDestroyed(explosions)
        floatingScores = removeDestroyed(floatingScores)
            
        gameOver = player.move(galaxians, SCREEN_WIDTH)
        
        # clear these arrays
        if gameOver:
            galaxians = []
            backgroundStars = []
            updateHiScore()
            
        
    #    -------------------------------------------------------------------------------
    #                                       DRAW
    #    -------------------------------------------------------------------------------
    for f in range(len(backgroundStars)):
        backgroundStars[f].draw(window)
        
    for f in range(len(floatingScores)):
        floatingScores[f].draw(fontArial, window)
    
    player.draw(window, SCREEN_HEIGHT)
    
    # TESTING ONLY
    #pygame.draw.line(window, (255,255,255), (player.x, player.y), (player.x, 0))
    for f in range(len(bombs)):
        bombs[f].draw(window)
    
    for f in range (len(galaxians)):
        galaxians[f].draw(window)
    
    for f in range(len(explosions)):
        explosions[f].draw(window)
    
    if player.score - newLife >= 0:
        player.lives += 1
        newLife += NEW_LIFE_BONUS
    
    # update high score on the fly
    if highScore < player.score:
        highScore = player.score
    
    
    # draw player score, level & high score
    playerScoreTxt = fontArial.render("SCORE: " + str(player.score), 1, (205,55,255))
    window.blit(playerScoreTxt, (100, 5))
    highScoreTxt = fontArial.render("HI SCORE: " + str(highScore), 1, (205,55,255))
    window.blit(highScoreTxt, (SCREEN_WIDTH - 150, 5))
    levelTxt = fontArial.render("Level: " + str(player.level), 1, (205,55,255))
    window.blit(levelTxt, (20, 5))
    
    if gamePaused:
        window.blit(spritePaused, (0,0))
    # test rectangle only
    #testRect = pygame.draw.rect(window, (0,255,100), (formationLeftEdge, 246, formationRightEdge - formationLeftEdge, -200), 1)
    
    pygame.display.flip()
    
    
    
