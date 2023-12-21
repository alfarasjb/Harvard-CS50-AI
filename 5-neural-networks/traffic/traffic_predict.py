import tensorflow as tf 
import os
import cv2
import numpy as np
import pandas as pd 

MODEL = 'model.h5'
DISTORTED = 'signs/distorted'
VALIDATION = 'signs/validation'

def load_model(model):
    loaded = tf.keras.models.load_model(model)
    return loaded

def load_images(path=VALIDATION):
    print("Loading Images")
    directory = os.listdir(path)

    images = list()
    labels = list()

    for i in directory: 
        #print(i)
        image_path = os.path.join(path, i)
        image_contents = cv2.imread(image_path)
        image_contents = cv2.resize(image_contents,(30,30))
        image_contents = np.array(image_contents, dtype = 'float')

        image_label = i.split('.')[0]
        
        images.append(image_contents)
        labels.append(image_label)

    return np.array(images), np.array(labels)


def main():
    #model = load_model(MODEL)
    images, labels = load_images()
    model = load_model(MODEL)

    # predict 
    predictions = model.predict(images)
    predictions_list = [int(np.argmax(predictions[i]) )for i in range(predictions.shape[0])]
    output = pd.DataFrame(np.arange(1, len(images) + 1))
    output.columns = ['ImageId']
    output['labels'] = labels.astype('int64')
    output['pred'] = predictions_list
    output['match'] = np.where(output['labels'] == output['pred'], 1, 0)

    correct_prediction = output.loc[output['match'] == 1]['match'].count()
    total = len(images) 
    accuracy = (correct_prediction / total ) * 100

    print(output)
    print(f"Total: {total} images")
    print(f"Correct Predictions: {correct_prediction} images")
    print(f"Prediction Accuracy: {accuracy}%")


if __name__ == "__main__":
    main()

