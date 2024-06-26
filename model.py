# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.
"""

import glob
import cv2
import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from keras.preprocessing.image import ImageDataGenerator

#import dataset by mounting your drive
#store fire and non fire images in lst_fire_img and non fire in lst_non_fire

print('Number of images with fire : {}'.format(len(lst_fire_img)))
print('Number of images without fire : {}'.format(len(lst_non_fire_img)))

lst_images_random = random.sample(lst_fire_img, 10) + random.sample(lst_non_fire_img, 10)
random.shuffle(lst_images_random)

plt.figure(figsize=(20, 20))
i = 0
while i < len(lst_images_random):
    plt.subplot(4, 5, i + 1)
    img = cv2.imread(lst_images_random[i])

    if img is not None and img.size != 0:
        re_img = cv2.resize(img, (112, 112))
        re_img = cv2.cvtColor(re_img, cv2.COLOR_BGR2RGB)
        plt.imshow(re_img)

        if "non_fire" in lst_images_random[i] or "NF" in lst_images_random[i]:
            plt.title('Image without fire')
        else:
            plt.title("Image with fire")
        i += 1
    else:
        lst_images_random.pop(i)
        plt.title('Error loading image')

plt.show()

lst_fire = []
for x in lst_fire_img:
  lst_fire.append([x,1])
lst_nn_fire = []
for x in lst_non_fire_img:
  lst_nn_fire.append([x,0])
lst_complete = lst_fire + lst_nn_fire
random.shuffle(lst_complete)

df = pd.DataFrame(lst_complete,columns = ['files','target'])
df.head(10) , df.shape

plt.figure(figsize = (10,10))
sns.countplot(x = "target",data = df)
plt.show()

invalid=[]
def valid_images(filepath):
  img = cv2.imread(filepath)
  if img is None:
    print(f"Error: Unable to read the image at {filepath}")
    invalid.append(filepath)

# for f,t in df.values:
#     valid_images(f)

for filepath_img in invalid:
  df = df.loc[~(df.loc[:,'files'] == filepath_img),:]
df.shape

def preprocessing_image(filepath):

    img = cv2.imread(filepath)

    if img is None:
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (112, 112))
    return img

def augment_image(img):

    img = np.expand_dims(img, axis=0)

    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest'
    )

    augmented_img = datagen.flow(img, batch_size=1).next()[0]
    augmented_img = np.array(augmented_img)

    augmented_img = augmented_img / 255.0

    return augmented_img

def create_format_dataset(dataframe):
    X = []
    y = []
    for filepath, label in dataframe.values:
        # Load and preprocess the image
        img = preprocessing_image(filepath)

        if img is not None:
            X.append(img)
            y.append(label)
            # Augment the image
            augmented_img = augment_image(img)
            X.append(augmented_img)
            y.append(label)

    return np.array(X), np.array(y)

X, y = create_format_dataset(df)
X.shape,y.shape

# Display a random subset of the dataset (e.g., 10 images)
num_images_to_display = min(10, len(X))
random_indices = random.sample(range(len(X)), num_images_to_display)

# Create a DataFrame with the sampled images
dataset_preview = pd.DataFrame({'Image': [X[i].tolist() for i in random_indices], 'Label': y[random_indices]})

# Display the preview of the dataset
print("Preview of the dataset:")
print(dataset_preview)

import tensorflow as tf
from keras.models import Sequential
from sklearn.model_selection import train_test_split
from keras.layers import Conv2D,MaxPooling2D,Flatten,Dense
from sklearn.metrics import confusion_matrix,classification_report

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = 0.2,stratify = y)

X_train.shape,X_test.shape,y_train.shape,y_test.shape

model = Sequential()

model.add(Conv2D(128, (3,3), activation = 'relu', input_shape = (112, 112, 3)))
model.add(MaxPooling2D((2,2)))

model.add(Conv2D(32, (3,3), activation = 'relu'))
model.add(MaxPooling2D((2,2)))

model.add(Flatten())
model.add(Dense(64, activation = 'relu'))
model.add(Dense(1, activation = 'sigmoid'))

model.summary()

model.compile(loss = 'binary_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

model.fit(X_train, y_train, epochs = 10, batch_size = 64)

model.evaluate(X_test, y_test)

y_pred = model.predict(X_test)

y_pred = y_pred.reshape(-1)
y_pred[y_pred<0.5] = 0
y_pred[y_pred>=0.5] = 1
y_pred = y_pred.astype('int')

y_pred

plt.figure(figsize = (20,10))

sns.heatmap(confusion_matrix(y_test,y_pred),annot = True)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("True")

plt.show()

print(classification_report(y_test,y_pred))

model.save('model.h5')

from keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
import PIL

from keras.models import load_model
cnn=load_model('model.h5')

cnn.summary()

image_for_testing=r'/content/drive/MyDrive/fire_dataset/fire_images/fire.209.png'

import keras.utils as image
from keras.models import load_model
import PIL
test_image=image.load_img(image_for_testing,target_size=(112,112))
test_image=image.img_to_array(test_image)
test_image=test_image/255
test_image=np.expand_dims(test_image,axis=0)
y_pred = cnn.predict(test_image)
print(y_pred)
y_pred = y_pred > 0.52

if(y_pred == 0):
    pred = 'no fire'
else:
    pred = 'fire'


print("Our model says :", pred)

image_show=PIL.Image.open(image_for_testing)
plt.imshow(image_show)