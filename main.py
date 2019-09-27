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
    
    try:
        hiScoreFile = open('hiscore', 'w')
        hiScoreFile.write(str(highScore))
        hiScoreFile.close()
    except IOError:
        #oops!
        print "Cannot write High Score to HD "




def attackPlayer(galaxians, galaxianAliveArray):
    state = States()
    
    if len(galaxians) > 4:
        availableToDive = []
        
        for f in range(len(galaxians)):
            if galaxians[f].state == state.FORMATION:
                availableToDive.append(f)
        
        if len(availableToDive) > 0:
            randomNumber = randint(0, len(availableToDive) - 1)
            # ------------
            # TESTING ONLY
            # only want leaders to dive for now
            #if galaxians[availableToDive[randomNumber]].colour != "yellow":
            #    return
            # ------------
            if galaxians[availableToDive[randomNumber]].colour == "yellow":
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
            """
            # TESTING ONLY
            if (gameEvent.key == pygame.K_BACKSPACE and not gameOver):
                # testing only
                for f in range(len(galaxians)):
                    if galaxians[f].colour != "yellow" and galaxians[f].colour != "red":
                        galaxians[f].destroyed = True
                #--------------
                #player.alive = False
                #explosions.append(Explosion(player.x, player.y, FPS, "player"))
            """
            
                
            

# the formation of galaxians is built in this fashion so that a quicker search can be done to 
# find the formation edge every time a galaxian gets destroyed
def buildGalaxians(galaxians, galaxianFormation):
    randPos = randint(18, SCREEN_WIDTH - (X_SPACE * 9 + 18))
    startFrame = 0
    
    counter = 0
    
    for cols in range(len(galaxianFormation)):
        sprite = "blue"
        startFrame = (startFrame + 1) % 4
        for rows in range(galaxianFormation[cols]):
            if rows == 5:
                sprite = "yellow"
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
    global currentGalaxianFormation
    tempFormation = currentGalaxianFormation
    # this fixes the problem when there is 1 extra yellow galaxian from the
    # previous level. otherwise it is okay if there are 0 or 2 extra galaxians
    if len(minMaxBorder) == 47 and direction == -1:
        tempFormation = [3,4,5,6,5,6,6,5,4,3]
    for cols in range(len(tempFormation)):
        for rows in range(tempFormation[cols]):
            if minMaxBorder[counter]:
                return edge + X_SPACE * cols * direction
            counter += direction
    return 0


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
    for f in range(70):#30
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
pygame.mixer.pre_init(44100, -16, 16, 4096)
pygame.init()

pygame.display.set_icon(pygame.image.load(os.path.join("images", "icon.png")))
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaxian (1.2.0)")

pygame.mouse.set_visible(False)
gameOver = True
gamePaused = False

divingTotal = 0
maxDiving = 3

formationMoveX = 0.8 * plusOrMinusOne()

# arrays of objects that need to be controlled
galaxians = []
explosions = []
backgroundStars = []
backgroundStarTimer = 0
bombs = []
floatingScores = []

player = None
newLife = 0

# when leaders join next level
extraGalaxians = 0


highScore = 0
try:
    hiScoreFile = open('hiscore', 'r')
    highScore = int(hiScoreFile.readline())
    hiScoreFile.close()
except IOError:
    try:
        hiScoreFile = open('hiscore', 'w')
        hiScoreFile.write("0")
        hiScoreFile.close()
    except IOError:
        print "Cannot create high score file on the HD!"

    





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
fontArial = pygame.font.Font(os.path.join("fonts", "DejaVuSansMono-Bold.ttf"), 14)
#fontArial = pygame.font.SysFont('arial', 18, True, False)

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
        # add extra leaders from previous level
        currentGalaxianFormation = [3, 4, 5, 6, 5, 5, 6, 5, 4, 3]
        for f in range(extraGalaxians):
            currentGalaxianFormation[4 + f] = 6
            
        # get original left and right edge of formation
        (startingLeftEdge, startingRightEdge) = buildGalaxians(galaxians, currentGalaxianFormation)
        
        # set all galaxians as in existence - a new formation has just been built
        minMaxBorder = [True for f in range(len(galaxians))]
        
        formationLeftEdge = startingLeftEdge
        formationRightEdge = startingRightEdge
        newLevelTimer = FPS * 2
        player.level += 1
        extraGalaxians = 0
        
    #    ------------------------- just the essentials here ----------------------------
    window.fill(c_black)
    gameTimer.tick(FPS)#tick_busy_loop(FPS)
    
    # check if the player wants to pause or terminate the game
    exitPauseCheck()
    

    #    -------------------------------------------------------------------------------
    #                                    MOVE OR PAUSE
    #    -------------------------------------------------------------------------------
    if not gamePaused:
        # ------------
        # TESTING ONLY
        #print gameTimer.get_fps()
        # ------------
        
        for f in range(len(floatingScores)):
            floatingScores[f].move()

        # generate background stars
        backgroundStarTimer = (backgroundStarTimer + 1) % (FPS / 8)#3
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
            if player.alive and (len(galaxians) <= 4 or 
                                                     (diveTimer == 0 and randint(0, upperLimit) == 0 and 
                                                      divingTotal < maxDiving + player.level / 3)):
                attackPlayer(galaxians, minMaxBorder)
                diveTimer = FPS / player.level
            
            # assume no galaxians have been destroyed so get boundary edge is not necessary
            getBoundaryEdge = False
            # assume none are diving
            divingTotal = 0
            
            for f in range(len(galaxians)):
                galaxians[f].move(explosions, galaxianFormationMove, player, bombs, floatingScores, extraGalaxians)
                
                if galaxians[f].destroyed:
                    minMaxBorder[galaxians[f].number] = False
                    getBoundaryEdge = True
                elif galaxians[f].escaped:
                    minMaxBorder[galaxians[f].number] = False
                    getBoundaryEdge = True
                    galaxians[f].destroyed = True
                    extraGalaxians += 1
                # count the number of galaxians diving or getting ready to dive
                elif (galaxians[f].state == state.DIVING or galaxians[f].state == state.LAUNCHING or 
                                                            galaxians[f].state == state.FORMATION_DIVING):
                    divingTotal += 1
            # if a galaxian is destroyed or escaped then find the formation edges again 
            if getBoundaryEdge:
                formationLeftEdge = getFormationEdge(minMaxBorder, startingLeftEdge, 0, 1)
                formationRightEdge = getFormationEdge(minMaxBorder, startingRightEdge, len(minMaxBorder) - 1, -1)
            
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
            extraGalaxians = 0
            updateHiScore()
            
        
    #    -------------------------------------------------------------------------------
    #                                       DRAW
    #    -------------------------------------------------------------------------------
    for f in range(len(backgroundStars)):
        backgroundStars[f].draw(window)
        
    for f in range(len(floatingScores)):
        floatingScores[f].draw(fontArial, window)
    
    player.draw(window, SCREEN_HEIGHT)
    # ---------------
    # TESTING ONLY
    #pygame.draw.line(window, (255,255,255), (player.x, player.y), (player.x, 0))
    # ---------------
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
    # -------------------
    # TESTING ONLY
    #pygame.draw.rect(window, (0,255,100), (formationLeftEdge, 246, formationRightEdge - formationLeftEdge, -200), 1)
    # -------------------
    
    pygame.display.flip()
    
    
    