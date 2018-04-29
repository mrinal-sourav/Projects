
 	Code can be found in the "Carom Billiards Source" folder. 

 	"game.py" is the simulation of Carom Billiards, without the Neural Network Model. 
	Imports required by game.py: 
		import pygame
		import random
		import math
		from queue import PriorityQueue  
	You can also play the game manually here. 

	"nn_test.py" uses a keras sequential model loaded from the "models" folder to predict 
	angle and speed for the q_ball. 
	Imports required by nn_test.py:
		import pygame
		import random
		import math
		from queue import PriorityQueue
		from keras.models import load_model, Sequential
		from keras.layers import Dense, Dropout
		import h5py
		import numpy as np