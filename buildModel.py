from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv1D
from keras.layers import Flatten


def buildModel():
    model = Sequential()
    model.add(Conv1D(filters=6, kernel_size=3, strides=1, input_shape=(21, 3), padding='valid', activation='relu'))
    model.add(Flatten())
    # model.add(Dense(units=1024, activation='relu'))
    model.add(Dense(units=128, activation='relu'))
    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=13, activation='softmax'))

    return model


