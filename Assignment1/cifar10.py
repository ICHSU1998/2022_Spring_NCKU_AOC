# -*- coding: utf-8 -*-
"""cifar10.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19B-eqnToUXS9eetc8sz8MBDxi3eu0UT8
"""

import tensorflow as tf
import matplotlib.pyplot as plt

"""# Load dataset
CIFAR10  
https://www.tensorflow.org/api_docs/python/tf/keras/datasets/cifar10/load_data

Load cifar10 dataset

將data分為training set及 test set，其中training set為50000筆，test set為10000筆
"""

(x_train,y_train),(x_test,y_test) = tf.keras.datasets.cifar10.load_data()
assert x_train.shape == (50000, 32, 32, 3)
assert x_test.shape == (10000, 32, 32, 3)
assert y_train.shape == (50000, 1)
assert y_test.shape == (10000, 1)

"""training set有 50000 張大小為 32*32 *3的圖像

test set有 10000 張大小為 32*32 *3的圖像
"""

print(x_train.shape)
print(y_train.shape)
print(x_test.shape)
print(y_test.shape)

"""顯示出training set中第 500 個data的label"""

print(y_train[499])

"""顯示第500筆training set的圖像"""

plt.imshow(x_train[499], cmap='gray')

"""#Data preprocess

將data作正規化
"""

x_train = x_train.astype("float32")
x_test = x_test.astype("float32")
x_train = x_train/255
x_test = x_test/255

"""將原始的label改用One-hot encode的label"""

y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

"""顯示第500筆training set的One-hot encode label"""

print(y_train[499])

"""#Build the model"""

from keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout

"""建立模型:

model.add(Conv2D):
* input_shape:輸入資料型態
* filter:kernel數量
* kernel_size:kernel的尺寸
* activation:激活函數

model.add(MaxPooling2D):
將四個相鄰的pixel取最大值，將最大值當作新的pixel

model.add(Flatten):
將多維轉成一維

model.add(Dense):
* units:fully connected layer的神經元數量
* activation:激活函數

model.add(Dropout):
避免overfitting

"""

model = tf.keras.models.Sequential()
model.add(Conv2D(input_shape=(32,32,3), filters=16, kernel_size=(5, 5), activation='relu'))
model.add(MaxPooling2D(2,2))
model.add(Conv2D(filters=32, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(2,2))

model.add(Flatten())
model.add(Dense(units=64, activation='relu'))
model.add(Dropout(rate=0.25))
model.add(Dense(units=10, activation="softmax"))

model.summary()

"""產生FLOPs的function"""

from tensorflow.python.framework.convert_to_constants import  convert_variables_to_constants_v2_as_graph

def get_flops(model):
    concrete = tf.function(lambda inputs: model(inputs))
    concrete_func = concrete.get_concrete_function(
        [tf.TensorSpec([1, *inputs.shape[1:]]) for inputs in model.inputs])
    frozen_func, graph_def = convert_variables_to_constants_v2_as_graph(concrete_func)
    with tf.Graph().as_default() as graph:
        tf.graph_util.import_graph_def(graph_def, name='')
        run_meta = tf.compat.v1.RunMetadata()
        opts = tf.compat.v1.profiler.ProfileOptionBuilder.float_operation()
        flops = tf.compat.v1.profiler.profile(graph=graph, run_meta=run_meta, cmd="op", options=opts)
        return flops.total_float_ops

"""顯示FLOPs的數量"""

print("The FLOPs is:{}".format(get_flops(model)) ,flush=True)

"""顯示model的各個layer所代表的意義，以及data size的變化"""

tf.keras.utils.plot_model(model, show_shapes=True)

"""#Compile the model
Configure the learning process with compile() API before training the model. It receives three arguments:

*   An optimizer 
*   A loss function 
*   A list of metrics  

https://www.tensorflow.org/api_docs/python/tf/optimizers  
https://www.tensorflow.org/api_docs/python/tf/keras/losses

編譯: 選擇損失函數、優化方法及成效衡量方式
"""

model.compile(
      loss='categorical_crossentropy',
      optimizer='adam',
      metrics=['accuracy'])

"""#Train the model

將training data對模型做訓練，訓練10次，每個iteration以64筆做計算，並以1成training set當成validation set
"""

Train_history = model.fit(
            x=x_train, 
            y=y_train, 
            batch_size=64,
            epochs=10, 
            validation_split=0.1)

"""#Plot the learning curve

第一張為loss的曲線圖，從圖可以看出training data及validation data的loss逐漸降低

第二張為Accuracy的曲線圖，從圖可以看出training data以及validation data的acc逐漸升高
"""

plt.title('Loss')
plt.xlabel('epoch')
plt.plot(Train_history.history['loss'], label='Training')
plt.plot(Train_history.history['val_loss'], label='Validation')
plt.legend()
plt.show()

plt.title('Accuracy')
plt.xlabel('epoch')
plt.plot(Train_history.history['accuracy'], label='Training')
plt.plot(Train_history.history['val_accuracy'], label='Validation')
plt.legend()
plt.show()

"""#Evaluate

將test data做輸入，用來評估model的好壞
"""

Test_result = model.evaluate(x = x_test, y = y_test, batch_size = x_test.shape[0])

print("Loss on testing set: %f" % Test_result[0])
print("Accuracy on testing set: %f" % Test_result[1])