import pygame, math
from random import random


"""
- rotates a sprite
- image is the sprite
- angle in the rotation in degrees"""
def rotate(image, angle):
    return pygame.transform.rotate(image, angle)


"""
- this just matches the centre of the new rotated sprite with the centre of the original sprite
- oldImage is the original sprite
- rotatedImage is the sprite that has been rotated"""
def matchCentre(oldImage, rotatedImage):
    oldRect = oldImage.get_rect()
    newRect = rotatedImage.get_rect()
    newRect.center = oldRect.center
    newRect.x -= math.floor(oldRect.width / 2.0 + 0.5)
    newRect.y -= math.floor(oldRect.height / 2.0 + 0.5)
    return newRect


"""
- if you need the sprite pivot point not at the centre. this will call the matchCentre function first to align
- centre points of the sprites then move a set number of pixels
- oldImage is the original sprite
- rotatedImage is the new rotated sprite 
- distance is the offset distance for the new pivot point. can be negative
- angle is the angle the rotatedImage was turned
"""
def moveCentre(oldImage, rotatedImage, distance, angle):
    newRect = matchCentre(oldImage, rotatedImage)
    newRect.centerx += distance * math.cos(math.radians(angle))
    newRect.centery += distance * -math.sin(math.radians(angle))    
    return newRect


"""
- this limits objects movement around the screen, where objectlength is x0.5 the sprite width or height
- value is the current position
- limit is the upper number to test against e.g. the screen width of height - assuming the lower limit to be zero
- tolerance is a distance to increase or lower the upper limit"""
def limits(value, lowerLimit, upperLimit, objectlength = 0):
    if value + objectlength > upperLimit:
        value = upperLimit - objectlength
    elif value - objectlength < lowerLimit:
        value = lowerLimit + objectlength
    return value


"""
- this will test pos1 and it's length to see if any part of it falls within pos2 and it's length
- pos1 starting point of test length
- pos1length end point of test length
- pos2 starting point of test length
- pos2length end point of test length"""
def withinViewport(pos1, pos1length, pos2, pos2length):
    return (pos1 + pos1length > pos2 and pos1 < pos2 + pos2length)





"""
- this method keeps angles between 0 and 360
- angle is the direction passed to correct"""
def wrap360(angle):
    if angle > 360:
        angle -= 360
    elif angle < 0:
        angle += 360
    return angle


"""
- this method takes a vector and breaks it into it's x & y components
- direction is direction in degrees
- speed is just a multiplier
- returns a tuple of the 2 components"""
def vector(direction, speed):
    add_x = math.cos(math.radians(direction)) * speed
    add_y = -math.sin(math.radians(direction)) * speed
    return (add_x, add_y)


 
"""
- this method returns a direction from (x1,y1) to (x2,y2)
- x1, y1 is the start point
- x2, y2 is the finish point"""
def pointDirection(x1, y1, x2, y2):
    xDist = float(x1 - x2)
    yDist = float(y1 - y2)
    
    if xDist == 0:
        if yDist > 0:
            return 90
        elif yDist < 0:
            return 270
    
    if yDist == 0:
        if xDist < 0:
            return 0
        else:
            return 180
    
    return wrap360(math.degrees(math.atan(-yDist / xDist)) + 180 * (xDist > 0))

"""
- this method measures the distance between (x1,y1) and (x2,y2)
- x1, y1 is the first point
- x2, y2 is the second point"""
def pointDistance(x1, y1, x2, y2):
    return (math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2)))




"""
- returns a new array with specific numbered elements removed
- array is the array passed
- elementsToDelete is an array of the specific elements to remove"""
def removeElementSpecific(array, elementsToDelete):
    newArray = [0 for x in range(len(array) - len(elementsToDelete))]
    if len(newArray) == 0:
        newArray = []
        return newArray
    
    newIndex = 0
    moveOn = True
    for f in range(len(array)):
        newArray[newIndex] = array[f]
        
        for check in range(len(elementsToDelete)):
            if f == elementsToDelete[check]:
                moveOn = False
                break
            else:
                moveOn = True
        
        if moveOn:
            newIndex += 1
            if newIndex == len(newArray):
                return newArray


"""
- returns array with any elements with boolean 'destroyed = True' removed
- array is the array passed"""
def removeDestroyed(array):
    delete = []
    for f in range(len(array)):
        if array[f].destroyed:
            delete.append(f)
    
    if len(delete) > 0:
        array = removeElementSpecific(array, delete)
        
    return array


"""
- returns either +1 / -1
"""
def plusOrMinusOne():
    x = 0.5
    
    while x == 0.5:
        x = random()
    
    x -= 0.5
    
    return x / math.fabs(x)
    




def directionTest(direction):
    if (direction > 180):
        direction -= 360
        
    elif (direction < -180):
        direction += 360
    
    return direction

