import pygame
import random
import math
from queue import PriorityQueue
from keras.models import load_model, Sequential
from keras.layers import Dense, Dropout
from keras.backend import clear_session
import h5py
import numpy as np

clear_session()
# Initializing the model: 
train_inputs1 = np.load('training_data/train_inputs_para_30.npy')
train_targets1 = np.load('training_data/train_targets_para_30.npy')

train_inputs2 = np.load('training_files_from_google/reinforced_inputs_size_30_v2.npy')
train_targets2 = np.load('training_files_from_google/reinforced_targets_size_30_v2.npy')

train_inputs3 = np.load('training_files_from_google/reinforced_inputs_size_30_v3.npy')
train_targets3 = np.load('training_files_from_google/reinforced_targets_size_30_v3.npy')

temp_inputs = np.append(train_inputs1, train_inputs2)
temp_targets = np.append(train_targets1, train_targets2)

train_inputs = np.append(temp_inputs, train_inputs3)
train_targets = np.append(temp_targets, train_targets3)

model = Sequential()
model.add(Dense(8, input_dim=8, activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Dense(300, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(50, activation='relu'))
model.add(Dense(20, activation='relu'))
model.add(Dense(5, activation='relu'))
model.add(Dense(1, activation='relu'))

model.compile(loss='mean_squared_error', optimizer='nadam', metrics=['accuracy'])
history = model.fit(train_inputs, train_targets, validation_split=0.2, epochs = 100, batch_size = 5000)

#function to generate the test data 
# combines a state with all possible actions for neural network to predict the q_value
def generate_test(state, rads, speed_range):
    test_data = []
    for angle in rads:
        for speed in speed_range:
            test_data.append(state+[angle]+[speed])
    test_data = np.array(test_data)
    return test_data

# given ball positions, return the best action predicted by the model
def query_state(state):
    
    test_data = generate_test(state, rads, speed_range)

    predictions = model.predict(test_data)

    q_vals = np.concatenate((test_data, predictions), axis=1)
    q_vals = q_vals[q_vals[:,8].argsort()[::-1]]
    action = q_vals[0] 
    angle = action[6]
    speed = action[7]
    predicted_state_action = state+[angle]+[speed]

    return (predicted_state_action)

# game parameter initialization:

#window size
display_width =  720 
display_height = 620

#table boundaries
top = 10
right = 400
left = 10
bottom = 600

#colors
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0) 
blue = (0,0,255)
dark_green = (30,90,5) 

# game physics 
friction = 0.012
elasticity = 0.85
stop_speed = 0.5
max_speed = 10.0 

# some definitions of angles for initializing data:
degrees = [x for x in range(271)]
radians = [math.radians(a) for a in degrees]
degrees2 = [x for x in range(-89, 0)]
radians2 = [math.radians(a) for a in degrees2]
rads =  radians + radians2
speed_range = [x for x in range(1,11)] 
inputs = [] 
targets = []

# the ball class 
class Ball:
    
    def __init__(self, size = 30, position = (int(right/2),int(bottom/2)), color = (0,0,0), speed = 0.0, angle = 0):
        self.size =  size
        self.x = position[0]
        self.y = position[1]
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
    error = abs(goal_dist - dist) #the current 'wrong' distance between the balls - absolute is taken to handle relative ball positions
    start_pos = (b2.x, b2.y)
    the_q = PriorityQueue(maxsize = 800)
    the_q.put((error, start_pos)) # initiating the queue
    while the_q: 
        neighbors = [] 
        curr_error, curr_pos = the_q.get() # returns a "less wrong" position to minimize error (priority queue)
        if curr_error < 1: 
            return curr_pos 
        neighbors = get_neighbors(curr_pos)
        for pos in neighbors:
            new_dist = coord_distance(origin, pos)
            new_error = abs(goal_dist - new_dist) 
            if new_error < 1:
                return pos 
            the_q.put((new_error,pos)) #add neighbor to the queue for further search from them

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


def game_loop(no_of_rounds, state, inputs, targets):

    q_ball = Ball(color = white)
    red_ball = Ball(color = red, speed = 0.0)
    black_ball = Ball(color = black, speed = 5.0)
    
    q_ball.x = state[0]
    q_ball.y = state[1]
    
    red_ball.x = state[2]
    red_ball.y = state[3]
    
    black_ball.x = state[4]
    black_ball.y = state[5]

    balls = [q_ball, red_ball, black_ball] 

    stop = False
    rounds = 0
    
    collided_with_red = False
    collided_with_black = False
    game_round_start = False
    reward = 0

    while not stop:

        if q_ball.speed == 0 and red_ball.speed == 0.0 and black_ball.speed == 0.0:
            
            collided_with_red = False
            collided_with_black = False 
            
            q_ball.angle = state[6]
            q_ball.speed = state[7]
            
            action_state = [q_ball.x, q_ball.y, red_ball.x, red_ball.y, black_ball.x, black_ball.y, q_ball.angle, q_ball.speed]
            
            game_round_start = True
            rounds+=1
            reward = 0
            if rounds >= no_of_rounds:
                stop = True

        if collision_check(q_ball, red_ball) and game_round_start:
            collide(q_ball, red_ball)
            collided_with_red = True
            if collided_with_black:
                reward = 100
            else:
                reward = 10
                       
        if collision_check(q_ball, black_ball) and game_round_start:
            collide(q_ball, black_ball) 
            collided_with_black = True
            if collided_with_red:
                reward = 100
            else:
                reward = 10 

        if collision_check(red_ball, black_ball) and game_round_start:
            collide(red_ball, black_ball)

        for ball in balls:
            ball.move()
            ball.bounce()
            
        if q_ball.speed == 0.0 and red_ball.speed == 0.0 and black_ball.speed == 0.0 and game_round_start:
            game_round_start = False
            new_state = [q_ball.x, q_ball.y, red_ball.x, red_ball.y, black_ball.x, black_ball.y]
            state = query_state(new_state)
            if reward > 11:
                inputs.append(action_state)
                targets.append([reward])
                train_input = np.array([action_state])
                target = np.array([reward])
                model.fit(train_input, target)

    
    if len(inputs)>len(targets):
        inputs = inputs[:-1]
    return (inputs, targets)


for i in range(1000):
    inputs = [] 
    targets = []
    while len(targets) < 100:
        q_ball_x = random_pos()[0]
        q_ball_y = random_pos()[1]
        
        red_ball_x = random_pos()[0]
        red_ball_y = random_pos()[1]
        
        black_ball_x = random_pos()[0]
        black_ball_y = random_pos()[1]
        
        state = [q_ball_x, q_ball_y, red_ball_x, red_ball_y, black_ball_x, black_ball_y]
        predicted_state_action = query_state(state)

        inputs, targets = game_loop(100, predicted_state_action, inputs, targets)
        print(len(inputs))

    train_inputs = np.array(inputs)
    train_targets = np.array(targets)

    #model.fit(train_inputs, train_targets)
    model.save('reinforced.h5')    
    print (" \n ITERATION = ", i) 
    


