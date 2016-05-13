import pygame
import random
import sys


# items
BRICKW = 60
BRICKH = 20
PADDLEW = 80
PADDLEH = 15
BALLD = 16
BALLR = BALLD/2
BULLETW = 20
BULLETH = 10
LEGH = 20
LEGW = 10
#FIRE STUFF I'M TOO LAZY TO TAKE OFF CAPS LOCK AT THIS POINT

#colours
BLK = (0,0,0)
WTE = (255,255,255)
PADDLEC = (100,0,100)
BREAKABLES = (255,100,255)

#Game types
STATE_BALL_BEGIN = 0
STATE_BALL_PLAY = 1
STATE_BALL_WIN = 2
STATE_DEATH = 8

#System stuff / starting positions / maxplacements
SCREEN = 640,540
PAUSERECT = pygame.Rect(0,0,640,540)
MAXPADX = SCREEN[0] - PADDLEW -10
MAXBALLX = SCREEN[0] - BALLD
MAXBALLY = SCREEN[1] - BALLD
#PROLLY GOING TO USE THIS FOR JUMPING
MAXPADY = SCREEN[1] - 300
PADY = SCREEN[1] - PADDLEH - 30

class BallGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN)
        pygame.display.set_caption("CRaaAAAaaAaAAAZY BAaaAAAaaAALL")

        self.clock = pygame.time.Clock()

        if pygame.font:
            self.font = pygame.font.Font(None,30)
        else:
            self.font = None

        self.init_game()

    def init_game(self):
        self.moveVals = 3
        self.y_ofs = 35
        self.x_ofs = 640
        self.brickListFirst = []
        self.currMovingList = []
        self.tempXVals = 640
        self.tempYVals = 540
        self.lives = 10
        self.score = 0
        self.state = STATE_BALL_BEGIN
        self.bricksMoveDown = False
        self.bricksMoveLeft = True

        self.holBrick = pygame.Rect(0,0,0,0)
        self.paddle = pygame.Rect(300,PADY,PADDLEW,PADDLEH)
        self.ball = pygame.Rect(290, PADY - BALLD,BALLD,BALLD)
        self.ballvel = [5,-5]
        self.momentum = [0,0]
        self.buildUp = 3
        self.ground = pygame.Rect(0,SCREEN[1]-15,700,200)

    def createBricks(self,brickList):
        """ Leo: 4/29 Changed to allow for moving perpetual looping blocks"""
        holdValX = self.x_ofs
        holdValY = self.y_ofs
        for i in range(8):
            self.x_ofs = holdValX
            for j in range(8):
                randChanceNum = random.randint(0,100)
                if(not(randChanceNum % 2 == 0)):
                    brickList.append(pygame.Rect(self.x_ofs,self.y_ofs,BRICKW,BRICKH))
                self.x_ofs += BRICKW + 10
            self.y_ofs += BRICKH + 5
        self.y_ofs = holdValY
        self.x_ofs = holdValX

    def drawBreakable(self,brickList):
        Counter = 0
        if self.bricksMoveLeft:
            self.tempXVals -= 3
        if self.bricksMoveDown:
            self.tempYVals += 3
        for brick in brickList:
            if self.bricksMoveLeft:
                brick[0] -= 3
            if self.bricksMoveDown:
                brick[1] += 3
            pygame.draw.rect(self.screen, BREAKABLES,brick)

    def checkInput(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle.left -= 5
            if self.paddle.left <0:
                self.paddle.left = 0
                
        if keys[pygame.K_RIGHT]:
            self.paddle.left += 5
            if self.paddle.left > MAXPADX:
                self.paddle.left = MAXPADX

        if keys[pygame.K_RETURN] and (self.state == STATE_BALL_STR):
            self.state == STATE_BALL_BEGIN

        if keys[pygame.K_SPACE] and self.state == STATE_BALL_BEGIN:
            randChance = random.randint(0,1)
            if randChance == 1:
                self.ball_vel = [5,-5]
            else:
                self.ball_vel = [-5.5]
            self.state = STATE_BALL_PLAY
            
        elif keys[pygame.K_RETURN] and (self.state == STATE_DEATH):
            self.init_game()

    def moveBall(self):
        self.ball.left += self.ballvel[0]
        self.ball.top += self.ballvel[1]

        if self.ball.left <= 0:
            self.ball.left = 0
            self.ballvel[0] = -self.ballvel[0]

        elif self.ball.left >= MAXBALLX:
            self.ball.left = MAXBALLX
            self.ballvel[0] = -self.ballvel[0]

        if self.ball.top <= 0:
            self.ball.top = 0
            self.ballvel[1] = -self.ballvel[1]

        elif self.ball.top >= MAXBALLX:
            self.ball.top = MAXBALLX
            self.ballvel[1] = -self.ballvel[1]

    def moveBullet(self):
        self.bullet[1] -= 7
        
        if self.bullet[1] <= 0:
            self.bullet = pygame.Rect(0,0,0,0)
            self.shooting = False

    def handleColl(self):
        for brick in self.currMovingList:
            if self.ball.colliderect(brick):
                self.buildUp += 1
                self.score += self.buildUp
                self.momentum[0] -= .1
                self.momentum[1] += .1
                self.ballvel[1] += self.momentum[1]
                self.ballvel[1] = -self.ballvel[1]
                self.currMovingList.remove(brick)
                self.holBrick = brick
                break
        
        if self.ball.colliderect(self.paddle):
            self.ball.top = PADY - BALLD
            self.ballvel[1] = -self.ballvel[1]

        elif self.ball.colliderect(self.ground):
            self.buildUp = 3
            self.momentum = [0,0]
            self.ballvel = [5,-5]
            self.state = STATE_BALL_BEGIN
            self.lives -= 1

    def showStats(self):
        if self.font:
            font_surface = self.font.render("EXP: " + str(self.score) + " LIVES: " + str(self.lives),False , WTE)
            self.screen.blit(font_surface, (205,5))

    def showMessage(self,message):
        if self.font:
            size = self.font.size(message)
            font_surface = self.font.render(message,False,WTE)
            x = (SCREEN[0] - size[0])/2
            y = (SCREEN[1] - size[1])/2
            self.screen.blit(font_surface,(x,y))


    def run(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit
            self.clock.tick(50)
            self.screen.fill(BLK)
            self.checkInput()


            if self.state == STATE_BALL_PLAY:
                self.moveBall()
                self.handleColl()

            elif self.state == STATE_BALL_BEGIN:
                self.ball.left = self.paddle.left + self.paddle.width /2
                self.ball.top = self.paddle.top - self.ball.height
                self.showMessage("PRESS SPACE TO BEGIN")

            if self.lives == 0:
                self.state = STATE_DEATH

            if self.state == STATE_DEATH:
                self.showMessage("GAME OVER. PRESS ENTER TO PLAY AGAIN")
                self.checkInput()

                
            if len(self.currMovingList) == 0 or self.tempXVals < 85:
                del self.currMovingList
                self.createBricks(self.brickListFirst)
                self.currMovingList = self.brickListFirst
                self.tempXVals = 640

            self.drawBreakable(self.currMovingList)

            pygame.draw.rect(self.screen, PADDLEC, self.paddle)
            pygame.draw.rect(self.screen, PADDLEC , self.ground)
            pygame.draw.circle(self.screen, WTE , (self.ball.left + BALLR, self.ball.top + BALLR), BALLR)
            
            self.showStats()
            pygame.display.flip()


if __name__ == "__main__":
    BallGame().run()

                    

                    
                    

