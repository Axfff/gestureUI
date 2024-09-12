from buildModel import buildModel
from tensorflow.keras.utils import to_categorical
import keras
import numpy
import os


commandDict = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
               'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'tap': 10, 'pre_pinch': 11, 'pinch': 12}


def getTrain():
    tx, ty = 0, 0
    datas = []
    datays = []
    for filename in os.listdir(r'datasets'):
        filePath = r'datasets/'+filename
        if filePath[-3:] != 'txt':
            continue
        datay = commandDict[filename[:-5]]
        with open(filePath, 'r') as f:
            print(f'loading file: {filePath}, type = {datay}')
            # print(len(f.readlines()))
            for ind, line in enumerate(f.readlines()):
                # print(line[:-2])
                try:
                    data = eval(line[:-1])
                except:
                    continue
                if ind == 0:
                    len_data = len(data)
                else:
                    if len_data != len(data):
                        continue
                datas.append(data)
                datays.append([datay])

        # print(datas)
        tx = numpy.array(datas)
        # print(tx)
        ty = numpy.array(datays)

    return tx, ty


def shuffle(x, y):
    # print(y.reshape((y.shape[0], 1, y.shape[1])))
    # train = numpy.concatenate((x, y.reshape((y.shape[0], 1, y.shape[1]))), axis=1)
    # print(train)
    # print(train.shape)
    state = numpy.random.get_state()
    numpy.random.shuffle(x)
    numpy.random.set_state(state)
    numpy.random.shuffle(y)
    return x, y


def separateTrain2Test(xTrain, yTrain, proportion):
    if len(xTrain) != len(yTrain):
        raise ValueError('length of x, y input are not equal')
    lenTest = int(len(xTrain)*proportion)
    lenTrain = len(xTrain) - lenTest

    xTrainNew, yTrainNew = xTrain[:lenTrain], yTrain[:lenTrain]
    xTest, yTest = xTrain[lenTrain:], yTrain[lenTrain:]

    return xTrainNew, yTrainNew, xTest, yTest


x_train, y_train = getTrain()
y_train = to_categorical(y_train)
print(f'{x_train}, \n{y_train}')
print(x_train.shape, y_train.shape)

x_train, y_train = shuffle(x_train, y_train)
print(f'{x_train}, \n{y_train}')
print(x_train.shape, y_train.shape)

x_train, y_train, x_test, y_test = separateTrain2Test(x_train, y_train, 0.1)
print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)


model = buildModel()

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer='adam',
              metrics=[keras.metrics.CategoricalAccuracy(), keras.metrics.Precision(), keras.metrics.Recall()])

model.fit(x_train, y_train, epochs=2048, batch_size=32)

# model.load_weights(r'models/v0.1_1024epochs.h5')
print(model.evaluate(x_test, y_test))

modelPath = r'models/v0.1_2048epochs.h5'
model.save_weights(modelPath)
# 6.56 e-4 vs 1.50 e-6 - 20220728
print('finish')


