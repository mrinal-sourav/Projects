import pygame
import random
import math
from queue import PriorityQueue

# game parameter initialization:

# window size
display_width =  720 
display_height = 620

# table boundaries
top = 10
right = 400
left = 10
bottom = 600

# colors
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0) 
blue = (0,0,255)
dark_green = (30,90,5) 

# to keep score 
score_board = {'score': [0, 0], 'player': ['Human Player Score', 'Select Q-ball to play']} 

# game initiations:  
pygame.init()
game_display = pygame.display.set_mode((display_width, display_height))
clock = pygame.time.Clock() 

# game physics 
friction = 0.012
elasticity = 0.85
stop_speed = 0.5
max_speed = 10.0

# the ball class 
class Ball:
    
    def __init__(self, size = 30, position = (int(right/2),int(bottom/2)), color = (0,0,0), speed = 0.0, angle = 0):
        self.size =  size
        self.x = position[0]
        self.y = position[1]
        self.pos = position
        self.color = color
        self.speed = speed 
        self.angle = angle
        self.selected = False
        self.a = None
        self.b = None
        
    def modulo_angle(self, angle_in_rad):
        degrees = math.degrees(angle_in_rad)
        degrees = degrees % 360 
        modulated_angle = math.radians(degrees)
        return modulated_angle

    def display(self, a = None,b = None):
        pygame.draw.circle(game_display,  self.color, (int(self.x), int(self.y)), self.size)
        if self.selected:
            pygame.draw.line(game_display, green, (self.x,self.y), (self.a, self.b), 3)

    def move(self):
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.speed -= friction 
        if self.speed < stop_speed:
            self.speed = 0.0 
            #self.angle = 0
        if self.speed > max_speed:
            self.speed = max_speed

    def bounce(self):
        if self.x >= (right + left) - self.size:
            self.x = 2*((right + left) - self.size) - self.x
            self.angle = self.modulo_angle(-self.angle)
            self.speed *= elasticity

        elif self.x <= self.size + left:
            self.x = 2*(self.size + left) - self.x
            self.angle = self.modulo_angle(-self.angle)
            self.speed *= elasticity

        if self.y >= (bottom + top) - self.size:
            self.y = 2*((bottom + top) - self.size) - self.y
            self.angle = self.modulo_angle(math.pi - self.angle)
            self.speed *= elasticity

        elif self.y <= self.size + top:
            self.y = 2*(self.size + top) - self.y
            self.angle = self.modulo_angle(math.pi - self.angle)
            self.speed *= elasticity    

# functions for the game

def text_objects(score, font):
    text_surface = font.render(score, True, black) 
    return text_surface, text_surface.get_rect()
    

def message_display(score_board):
    text = pygame.font.Font('freesansbold.ttf', 20)
    text_surface_1, text_frame_1 = text_objects(score_board['player'][0] +' : '+ str(score_board['score'][0]), text)
    text_surface_2, text_frame_2 = text_objects(score_board['player'][1], text)
    text_frame_1.center = (((display_width - 150), (200)))
    text_frame_2.center = (((display_width - 150), (225)))
    game_display.blit(text_surface_1, text_frame_1)
    game_display.blit(text_surface_2, text_frame_2) 

def random_pos():
    x_pos = random.randint(left+20, right-20) 
    y_pos = random.randint(top+20,bottom-20)
    return (x_pos,y_pos)

def q_ball_select(q_ball, x, y):
    if math.hypot(q_ball.x - x, q_ball.y - y) <= q_ball.size:
        q_ball.selected = True
        q_ball.color = blue 
        q_ball.speed = 0
        q_ball.a = x 
        q_ball.b = y

def q_ball_unselect(q_ball):
    q_ball.selected = False
    q_ball.color = white
    q_ball.a = None 
    q_ball.b = None 

def q_ball_setab(q_ball, x, y):
    q_ball.a = x 
    q_ball.b = y 

# Collision physics and a_star
def coord_distance(pos1,pos2):
    dx = pos1[0] - pos2[0] 
    dy = pos1[1] - pos2[1]
    distance = math.hypot(dx, dy)
    return distance

def collision_check(ball1, ball2):
    distance = coord_distance((ball1.x,ball1.y), (ball2.x,ball2.y))
    return distance <= (ball1.size + ball2.size) 

def get_neighbors(pos):
    x = pos[0]
    y = pos[1] 
    neighbors = [(x+1,y), (x-1,y), (x,y+1), (x,y-1),
                (x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1)]
    return neighbors

# a_star is used to search for the closest position ball2 could take
# to do away with overlap. 
# returns that position for ball2 
def a_star(b1,b2, dist): 
    origin = (b1.x,b1.y)
    goal_dist = 2*b1.size + 2   # the right distance between balls without overlap (+2 --> to be safe!)
    error = abs(goal_dist - dist) # the current 'wrong' distance between the balls - absolute is taken to handle relative ball positions
    start_pos = (b2.x, b2.y)
    the_queue = PriorityQueue(maxsize = 800)
    the_queue.put((error, start_pos)) # initiating the queue
    while the_queue: 
        neighbors = [] 
        curr_error, curr_pos = the_queue.get() # returns a "less wrong" position to minimize error (priority queue)
        if curr_error < 1: 
            return curr_pos 
        neighbors = get_neighbors(curr_pos)
        for pos in neighbors:
            new_dist = coord_distance(origin, pos)
            new_error = abs(goal_dist - new_dist) 
            if new_error < 1:
                return pos 
            the_queue.put((new_error,pos)) #add neighbor to the queue for further search from them

def modulo_angle(angle_in_rad):
    degrees = math.degrees(angle_in_rad)
    degrees = degrees % 360 
    modulated_angle = math.radians(degrees)
    return modulated_angle

def collide(b1,b2):
    dx = b1.x - b2.x 
    dy = b1.y - b2.y 

    tangent = math.atan2(dy, dx)
    b1.angle = modulo_angle(2*tangent - b1.angle)
    b2.angle = modulo_angle(2*tangent - b2.angle)

    # adjust overlap using a_star to find the best point without overlap
    distance = coord_distance((b1.x,b1.y),(b2.x,b2.y)) 
    new_x_for_b2, new_y_for_b2 = a_star(b1,b2, distance)
    b2.x = new_x_for_b2
    b2.y = new_y_for_b2

    if not collision_check(b1,b2):
        new_speed = elasticity * (b1.speed + b2.speed)/2
        b1.speed = b2.speed = new_speed


def game_loop():

    q_ball = Ball(color = white, speed = 2.0, angle = math.pi/2)
    red_ball = Ball(color = red, position = random_pos(), speed = 4.0, angle = (math.pi/3))
    black_ball = Ball(color = black, position = random_pos(), speed = 5.0, angle = -(math.pi/3))

    balls = [q_ball, red_ball, black_ball] 

    stop = False 
    game_round = 0 
    player_score = 0
    collision_count = 0
    collided_with_red = False
    collided_with_black = False

    while not stop:
        
        game_round += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                q_ball_select(q_ball, mouseX, mouseY)
                
            if event.type == pygame.MOUSEMOTION and q_ball.selected: 
                mouseX, mouseY = pygame.mouse.get_pos()
                q_ball_setab(q_ball, mouseX, mouseY)

            if event.type == pygame.MOUSEBUTTONUP and q_ball.selected:
                mouseX, mouseY = pygame.mouse.get_pos()
                dx = mouseX - q_ball.x    
                dy = mouseY - q_ball.y  
                q_ball.angle = math.atan2(dy, dx) + 0.5*math.pi
                q_ball.speed = math.hypot(dx, dy) * 0.06
                q_ball_unselect(q_ball)
                

        game_display.fill(white)
        pygame.draw.rect(game_display, dark_green, [left, top, right, bottom]) 

        if q_ball.speed == 0:
            collided_with_red = False
            collided_with_black = False

        if collision_check(q_ball, red_ball):
            collide(q_ball, red_ball)
            if collided_with_black:
                collision_count += 100
            else:
                collision_count += 10
                collided_with_red = True
                    
        if collision_check(q_ball, black_ball):
            collide(q_ball, black_ball) 
            if collided_with_red:
                collision_count += 100
            else:
                collision_count += 10
                collided_with_black = True
        

        if collision_check(red_ball, black_ball):
            collide(red_ball, black_ball)

        score_board['score'][0] = collision_count
        
        for i, ball in enumerate(balls):
            ball.move()
            ball.bounce()

        for ball in balls:
            ball.display()

        message_display(score_board)
        pygame.display.update()
        clock.tick(60)

game_loop()
pygame.quit()
quit()