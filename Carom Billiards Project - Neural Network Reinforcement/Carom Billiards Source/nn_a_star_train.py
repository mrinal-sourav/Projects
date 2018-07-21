from keras.models import load_model, Sequential, save_model
from keras.layers import Dense, Dropout
from keras import backend as K
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import h5py
import numpy as np
from queue import PriorityQueue

# CONSTANTS

INITIAL_EPOCHS = 55
INITIAL_BATCH_SIZE = 24000
DESIRED_ACCURACY = 170

##############################################################################################################

# load training files
train_inputs = np.load('training_data/train_inputs_para_30_2.npy')
train_targets = np.load('training_data/train_targets_para_30_2.npy')

##############################################################################################################

# define the model 
def get_model():
    K.clear_session()
    model = Sequential()
    model.add(Dense(10, input_dim=8, activation='relu'))
    model.add(Dense(10, activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(300, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(200, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(20, activation='relu'))
    model.add(Dense(5, activation='relu'))
    model.add(Dense(1))

    model.compile(loss='mean_squared_error', optimizer='nadam')
    
    return model

##############################################################################################################

# initial training
model = get_model()
history = model.fit(train_inputs, train_targets, validation_split=0.1, epochs = INITIAL_EPOCHS, batch_size = INITIAL_BATCH_SIZE)

##############################################################################################################

# I now want to design an a_star method for training the model. 
# Lets assume that the tuple (epochs=20, batch_size = 20000) is a start node for the search 
# we will set a delta_epoch and a delta_batch, say:
delta_epoch = 5
delta_batch = 8000

nodes_explored = [] 

# we use the following function to take in the start node
# and return child nodes such that 
# if our start node is (20, 20000), delta_epoch=2 and delta_batch=1000
# our child nodes would be (22, 21000), (18,19000),(22, 19000), (18, 21000), (20, 21000), (20, 19000), (18, 20000), (22, 20000)
def get_children(node):
    epoch_0 = node[0]
    epoch_1 = node[0] + delta_epoch
    epoch_2 = node[0] - delta_epoch
    batch_size_0 = node[1]
    batch_size_1 = node[1] + delta_batch
    batch_size_2 = node[1] - delta_batch
    
    if epoch_2 < 3 :
        epoch_2 = 5 
        
    if batch_size_2 < 50: 
        batch_size_2 = 1500
        
    children = [(epoch_1, batch_size_1), 
                (epoch_2, batch_size_2), 
                (epoch_1, batch_size_2), 
                (epoch_2, batch_size_1),
                (epoch_0, batch_size_1),
                (epoch_0, batch_size_2), 
                (epoch_1, batch_size_0),
                (epoch_2, batch_size_0)]

    for child in children: 
        if child not in nodes_explored:
            nodes_explored.append(child)
        else:
            children.remove(child)

    return  list(set(children)) # returning non-duplicates in case of overlap

# This function takes in the history of a training and calculates the avg. difference between the 
# validation_loss and training_loss.
# This measure is an indication of the bias-variance tradeoff of a model. 
# If validation loss is higher than the training_loss, overfitting has occured.
# If validation loss is lesser than the training loss, this measure would be negative and optimal.
# So, we can now use a_star search for a model that returns the lowest value 
# returned by this function (even considering negative). 
def get_accuracy(history):
    final_val_loss = history.history['val_loss'][-4:]
    final_training_loss = history.history['loss'][-4:]
    average_val_loss = sum(final_val_loss * 2) / 4 
    average_training_loss = sum(final_training_loss) / 4 
    return average_val_loss - average_training_loss


##################################################################################################################
# initializing a_star

def save_plot(history, epochs, batch_size, pdf):
    acc = get_accuracy(history)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Epochs = ' + str(epochs) + ' | ' + 'Batch Size = ' + str(batch_size) + ' | ' + 'Accuracy = ' + str(acc))
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    pdf.savefig()
    plt.gcf().clear()

my_data = {'Creator': 'Mrinal Sourav', 'Author': 'Mrinal Sourav', 'Title': 'Plots for the A_Star Training'}
with PdfPages("models/a_star_simple_plots_10.pdf", metadata = my_data) as pdf:    
    # define initial data for a_star
    minimum_accuracy = 10000000
    q = PriorityQueue()
    accuracy = get_accuracy(history)
    print('\n ###### inititial_accuracy = ' + str(accuracy) + '\n')
    start_node = (INITIAL_EPOCHS, INITIAL_BATCH_SIZE)
    q.put((accuracy, start_node))
    save_plot(history, INITIAL_EPOCHS, INITIAL_BATCH_SIZE, pdf)

    # a_star loop begins here 

    while minimum_accuracy > DESIRED_ACCURACY and q.qsize() > 0:
        
        print ('\n\n QUEUE SIZE BEFORE GET = ' + str(q.qsize()))
        current_node = q.get() # returns a tuple within a tuple 

        print ('\n\n NODE SELECTED <<<------ Epochs = ' + str(current_node[1][0]) +  
            ' -------- BatchSize = ' + str(current_node[1][1]) + 
            ' --------- Accuracy = ' + str(current_node[0]) + ' -------->>>\n')

        parent_accuracy = current_node[0] # initializing accuracy for parent here
        
        children = get_children(current_node[1]) # children is a list of tuples

        for idx, child in enumerate(children): # child is a tuple
            K.clear_session()
            model = get_model()
            print ( '\n CHILD ' + str(idx+1) + ' out of ' +  str(len(children)) + 
                    ' :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: ')
            print ('\n\t BATCH SIZE = ' + str(child[1]))
            print ('\n\t EPOCHS = ' + str(child[0]))
            history = model.fit(train_inputs, train_targets, validation_split=0.1, epochs = child[0], batch_size = child[1])
            new_accuracy = get_accuracy(history) 
            print ("\n\t CHILD ACCURACY = " + str(new_accuracy) + '\n')
            print ("\n\t PARENT ACCURACY = " + str(parent_accuracy) + '\n')
            if (new_accuracy < parent_accuracy): # if accuracy of child is better than the parent selected from the previous iteration 
                
                q.put((new_accuracy, child)) # inserts a tuple within a tuple
                print ('\n \t \t >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ' + 
                        'APPENDED CHILD TO THE QUEUE | QUEUE SIZE = ' +  
                        str(q.qsize()) + 
                        ' <<<<<<<<<<<<<<<<<<<<<<<<<<< \n')

                if new_accuracy < minimum_accuracy: # if accuracy of the child is better than the best so far in the overall search space 
                    minimum_accuracy = new_accuracy
                    # save the model:
                    save_model(model, 'models/a_star_simple_model_10.h5')
                    # save the plots: 
                    save_plot(history, child[0], child[1], pdf) 

                    print (' \n \t \t \t ********** BEST MODEL SAVED |' + 
                            ' EPOCHS = ' + str(child[0]) + ' |' + 
                            ' BATCH_SIZE = ' + str(child[1]) + ' |' + 
                            ' ACCURACY = ' + str(new_accuracy) + ' ******** \n\n\n' )
                            
print ('\n NODES EXPLORED: ')
for node in nodes_explored:
    print(node)


print ('\n\n\n #########################  TRAINING COMPLETED  ############################### \n \n ')


###################################################################################################################