# -*- coding: utf-8 -*-
"""Functions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jRqGBUuMuNn-veKwjPBBsFDn-ccBM8pa

**Import libraries**
"""

import csv
import cv2
import numpy as np
from keras.layers import Input, Conv2D, MaxPool2D, Flatten, Dense, BatchNormalization, Dropout
from augmentations import augmentations as augs
from keras.applications.vgg16 import VGG16
from keras.initializers import glorot_uniform
from keras.models import Model, Sequential, load_model
from keras.utils import to_categorical
from keras.regularizers import l2
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam, SGD, RMSprop
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
from scipy.spatial.distance import cdist
import math
from sklearn.manifold import TSNE
import tensorflow as tf
from sklearn.decomposition import PCA
from matplotlib.pyplot import figure
from matplotlib.pyplot import plot
from matplotlib.pyplot import xlabel
from matplotlib.pyplot import ylabel
from matplotlib.pyplot import show
from more_itertools import locate
from sklearn import svm
import os
import seaborn as sns
import tf_explain
from tf_explain.core.activations import ExtractActivations

"""Functions for Step 1"""

#yuvnish, vartika


def visualize_classes(dict):
    """
    function: display images that are already present in the dataset
    :param dict: dict['dataset_directory'] = 'C:/users/desktop/uploads/dataset.csv'
                  dict['size'] = size of input image
    :return: class_ids, number of images in each class, one image from each class (all three are list)
    """
    x = []
    y = []
    with open(dict['dataset_directory'], 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            label = int(row[0])
            image = np.array([int(a) for a in row[1:]], dtype='uint8')
            image = image.reshape((dict['size'], dict['size']))
            x.append(image)
            y.append(label)

    class_ids = list(set(y))
    number_of_images = []
    images = []
    for i in class_ids:
        number_of_images.append(y.count(i))
        index = y.index(i)
        images.append(x[index])

    return class_ids, number_of_images, images

# bharat


def display_one_sign(image, title, subplot, red=False, titlesize=16):
    """
    function: add passed image to overall visualizer image
    :param image: list of images
           title: label of the image
           subplot: subplot
           red: font color option
           titlesize: size of the title on subplot
    :return: rows, cols, index of image in the main plot
    """
    plt.subplot(*subplot)
    plt.axis('off')
    plt.imshow(image,  cmap='Greys_r')
    if title != None:
        plt.title(title, fontsize=int(titlesize) if not red else int(titlesize/1.2),
                  color='red' if red else 'black', fontdict={'verticalalignment': 'center'}, pad=int(titlesize/1.5))
    return (subplot[0], subplot[1], subplot[2]+1)

# bharat


def display_batch_of_images(images, datadir, labels=None):
    """
    function: displays batch of images
    :param images: list of images
           labels: list of labels
           datadir: where the plot needs to be saved 
    :return: output path of saved plot
    """
    cols = 11
    images = np.array(images)
    if images.shape[0] % cols == 0:
        rows = images.shape[0]//cols
    else:
        rows = 1+(images.shape[0]//cols)

    if labels is None:
        labels = [None for _ in enumerate(images)]

    FIGSIZE = 26.0
    SPACING = 0.1
    subplot = (rows, cols, 1)
    if rows < cols:
        plt.figure(figsize=(FIGSIZE, FIGSIZE/cols*rows))
    else:
        plt.figure(figsize=(FIGSIZE/rows*cols, FIGSIZE))

    for i, (image, label) in enumerate(zip(images[:rows*cols], labels[:rows*cols])):
        title = label
        correct = True
        dynamic_titlesize = FIGSIZE*SPACING/max(rows, cols)*40+7
        subplot = display_one_sign(image, title, subplot, not correct, titlesize=dynamic_titlesize)

    output_path = os.path.join(datadir, 'plot_of_classes.png')
    plt.savefig(output_path)
    return output_path

#yuvnish, vartika


def visualize_image_distribution(d):
    """
    function: returns plot of data distribution in classes of dataset
    :param d: d['y'] = list of all labels
              d['datadir'] = path to data directory were plot needs to be saved
    :return: returns path of saved plot of distribution
    """
    y = d['y']
    category_names = [n for n in range(len(np.unique(y)))]
    label_num = []
    for i in category_names:
        num = sum(y == i)
        label_num.append(num)
    plt.figure(figsize=(20, 10))
    sns.barplot(category_names, label_num).set_title("Number of training images per category:")
    output_path = os.path.join(d['datadir'], 'image_data_distribution.png')
    plt.savefig(output_path)
    return output_path

#yuvnish, vartika


def upload_class(dict):
    """
    function: loading the class images uploaded by user
    :param dict: dict['existing_class'] = 'Y' or 'N'
                dict['path'] = list of names of images uploaded, e.g. ['images1.jpg', 'images2.jpg']
                dict['class_id'] = class id in which images are to be added
                dict['csv_file_path'] = 'C:/users/desktop/uploads/dataset.csv'
                dict['saved_images_directory'] = 'C:/users/desktop/uploads'
    :return:
    """
    with open(dict['csv_file_path'], 'a') as f:
        writer = csv.writer(f)
        if dict['existing_class'] == 'Y':
            for i in dict['path']:
                img = cv2.imread(os.path.join(dict['save_images_directory'], i))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (32, 32))
                value = np.asarray(img, dtype=np.int)
                value = value.flatten()
                value = np.insert(value, 0, int(dict['class_id']), axis=0)
                writer.writerow(value)
        else:
            input_dict = {'dataset_directory': dict['csv_file_path'], 'size': 32}
            class_ids, _, _ = visualize_classes(input_dict)
            next_class_id = len(class_ids)
            for i in dict['path']:
                img = cv2.imread(os.path.join(dict['save_images_directory'], i))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (32, 32))
                value = np.asarray(img, dtype=np.int)
                value = value.flatten()
                value = np.insert(value, 0, next_class_id, axis=0)
                writer.writerow(value)

    return "Uploaded Successfully"


"""Uploading Single Image"""

#yuvnish, vartika


def load_image(dict):
    """
    function: loads image uploaded by user
    :param dict: dict['path'] = 'C:/users/desktop/uploads/image.jpg'
    :return: image
    """
    image = cv2.imread(dict['path'])
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


"""Functions for Step 2

Augmentation Functions
"""

#yuvnish, vartika


def list_to_dictionary(d):
    """
    function: merge two lists into a dictionary with keys as elements of 1st list and corresponding values as elements
              of 2nd list
    :param d: d['list1'] = 1st list
              d['list2'] = 2nd list
    :return: output_dictionary
    """
    output_dictionary = dict(zip(d['list1'], d['list2']))
    return output_dictionary

# harshita


def augment_batch(d):
    """
    function: augments batch of images
    :param d: d['images'] = list of images
              d['input_aug'] = list of augmentations user specified
    :return: list of augmented images
    """
    images = d['images']
    input_aug = d['input_aug']
    for i in range(images.shape[0]):
        images[i] = augs.applyAugmentation(images[i], input_aug)  # Adarsh's augmentation function
    return images


"""Functions for Step 3

Loading Saved Model
"""

#yuvnish, vartika


def load_model(dict):
    """
    function: loads pre-trained neural network
    :param dict: dict['path'] = 'C:/users/desktop/uploads/model_v1.h5'
    :return: model
    """
    model = load_model(dict['path'])
    return model


"""Loading the Dataset"""

#yuvnish, vartika


def load_dataset(csv_file_path, size_of_image=32):
    """
    function: loads images and labels from csv file (combined data set)
    :param csv_file_path: path where the csv file has been stored - 'C:/User/desktop/uploads/data.csv'
    :param size_of_image: size of input image (default value = 32)
    :return: list of images and labels
    """
    X = []
    Y = []

    with open(csv_file_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row[0] != '' and len(row[0]) != 0:
                label = int(row[0])
                image = np.array([int(a) for a in row[1:]], dtype='uint8')

                # loading in RGB format
                image = image.reshape((32, 32, 3))

                # Yuvnish's model - size = 64
                # Sakshee's model - size = 32
                image = cv2.resize(image, (size_of_image, size_of_image))
                X.append(image)
                Y.append(label)

    # print(len(X))
    # print(len(Y))
    return X, Y


"""Over Sampling the Dataset"""

# bharat


def create_data_over(d):
    """
    function: oversample the dataset
    :param d: d['img_data'] = list of all images
              d['label_data'] = list of all labels
              d['i'] = class_id
              d['diff'] = number of images to be added
              d['input_aug'] = list of augmentations user specifies
    :return: list of oversampled images and labels
    """
    img_data = np.array(d['img_data'])
    label_data = np.array(d['label_data'])
    i = d['i']
    diff = d['diff']
    input_aug = d['input_aug']
    mask = [int(x) == i for x in label_data]
    images1 = img_data[mask]
    del img_data
    label1 = label_data[mask]
    del label_data
    if diff < images1.shape[0]:
        idx = np.random.randint(images1.shape[0], size=diff)
        d_augment_batch = {'images': images1[idx], 'input_aug': input_aug}
        images2 = augment_batch(d_augment_batch)
        label2 = label1[idx]
        images = np.concatenate((images1, images2), axis=0)
        labels = np.concatenate((label1, label2), axis=0)
        return images, labels
    else:
        n = diff//images1.shape[0]
        diff = diff % images1.shape[0]
        idx = np.random.randint(images1.shape[0], size=diff)
        images2 = [images1]*n
        images2.append(images1[idx])
        images3 = np.concatenate(images2, axis=0)
        d_augment_batch = {'images': images3, 'input_aug': input_aug}
        images3 = augment_batch(d_augment_batch)
        label2 = [label1]*n
        label2.append(label1[idx])
        label3 = np.concatenate(label2, axis=0)
        images = np.concatenate((images1, images3), axis=0)
        labels = np.concatenate((label1, label3), axis=0)
        return images, labels


"""Undersample the Dataset"""

# bharat


def create_data_under(d):
    """
    function: undersamples the dataset
    :param d: d['img_data'] = list of all images
              d['label_data'] = list of all labels
              d['i'] = class_id
              d['diff'] = number of images to be added
    :return: list of undersampled images and labels
    """
    img_data = np.array(d['img_data'])
    label_data = np.array(d['label_data'])
    i = d['i']
    diff = d['diff']
    mask = [int(x) == i for x in label_data.tolist()]
    images = img_data[mask]
    del img_data
    labels = label_data[mask]
    del label_data
    idx = np.random.randint(images.shape[0], size=labels.shape[0] - diff)
    images = images[idx]
    labels = labels[idx]
    return images, labels


"""Balancing Main Function"""

# bharat


def balanced_dataset(d):
    """
    function: returns balanced dataset
    :param d: d['class_ids'] = list of class ids specified by user
              d['number_of_images'] = list of number of images users wants in a class
              d['input_aug'] = list of all augmentations specified by user
              d['csv_path'] = path of csv file 
    :return: final list of augmented images and labels
    """
    img_data, label_data = load_dataset(d['csv_path'], size_of_image=32)
    d_list_to_dict = {'list1': d['class_ids'], 'list2': d['number_of_images']}
    var_num = list_to_dictionary(d_list_to_dict)

    unique, counts = np.unique(label_data, return_counts=True)
    num_per_class = dict(zip(unique, counts))

    images_lst = []
    labels_lst = []
    d['img_data'] = img_data
    d['label_data'] = label_data

    for i in d['class_ids']:
        diff = var_num[i] - num_per_class[i]
        if diff == 0:
            mask = [int(x) == i for x in label_data]
            images = img_data[mask]
            labels = label_data[mask]
            images_lst.append(images)
            labels_lst.append(labels)
        elif diff > 0:
            d_create_data_over = {'img_data': d['img_data'], 'label_data': d['label_data'], 'i': i, 'diff': diff,
                                  'input_aug': d['input_aug']}
            images, labels = create_data_over(d_create_data_over)
            images_lst.append(images)
            labels_lst.append(labels)
        elif diff < 0:
            d_create_data_under = {'img_data': d['img_data'], 'label_data': d['label_data'], 'i': i, 'diff': -diff}
            images, labels = create_data_under(d_create_data_under)
            images_lst.append(images)
            labels_lst.append(labels)

    del img_data, label_data

    X_data = np.concatenate(images_lst, axis=0)
    del images_lst
    Y_data = np.concatenate(labels_lst, axis=0)
    del labels_lst

    return X_data, Y_data


"""Smart Segregation Functions"""

# bharat


def difficult_sam(x, y, test_size, ypred):
    """
    function: splits data into train and test set (difficult segregation)
    :param x: list of images
    :param y: list of labels
    :param test_size: proportion of images to be put on test set (e.g. 0.2, range=(0,1))
    :param ypred: predicted labels
    :return: train and test set images and labels
    """
    num = y.shape[0]
    num_test = int(num*test_size)
    num_train = num-num_test
    mask1 = y == ypred
    mask2 = y != ypred
    del ypred
    x1, y1 = x[mask1], y[mask1]
    x2, y2 = x[mask2], y[mask2]
    del mask1, mask2, x, y
    num_train = num_train-y2.shape[0]
    test_size = num_test/(num_test+num_train)
    x_train, x_test, y_train, y_test = train_test_split(x1, y1, test_size=test_size)
    del x1, y1
    x_train, y_train = np.concatenate((x_train, x2), axis=0), np.concatenate((y_train, y2), axis=0)
    del x2, y2
    return x_train, x_test, y_train, y_test

# bharat


def euc_mat(x, model_path, layer_name='dense_1'):
    """
    function: passes every image of data to the model and takes output of a layer and then calculates distance between
              those outputs.
    :param x: list of all images
    :param model_path: path to where trained model is saved - 'C:/Users/desktop/uploads/yuvnish_tsr_model_v5.h5'
    :param layer_name: name of layer of model whose output needs to be obtained from model
    :return: matrix representing distance of image from every other image of data
    """
    model = load_model(model_path)
    intermediate_layer = Model(inputs=model.input, outputs=model.get_layer(layer_name).output)
    feature_vectors = intermediate_layer.predict(x)

    distance_matrix = cdist(feature_vectors, feature_vectors, metric='euclidean')

    del model
    del feature_vectors
    return distance_matrix

# bharat


def kennard_stone(x, y, test_size, model_path):
    """
    function: splits data into train and test set (if method=kennard_stone)
    :param x: list of all images
    :param y: list of all labels
    :param test_size: proportion of images to be put on test set (e.g. 0.2, range=(0,1))
    :param model_path: path of saved model used to calculate the euclidean distance between feature vectors
    :return: train and test set images and labels
    """
    x_train = []
    y_train = []
    x_test = []
    y_test = []

    for i in range(len(np.unique(y))):
        mask = y == i
        print(mask)
        class_num = sum(mask)
        cnum_test = int(class_num * test_size)
        cx = x[mask]
        cy = y[mask]
        eucl_mat = euc_mat(cx, layer_name='dense_1', model_path=model_path)

        select_p = []
        remain_p = [n for n in range(class_num)]
        first_2pts = np.unravel_index(np.argmax(eucl_mat), eucl_mat.shape)
        select_p.append(first_2pts[0])
        select_p.append(first_2pts[1])
        remain_p.remove(first_2pts[0])
        remain_p.remove(first_2pts[1])

        for _ in range(cnum_test - 2):
            select_distance = eucl_mat[select_p, :]
            min_distance = select_distance[:, remain_p]
            min_distance = np.min(min_distance, axis=0)
            max_min_distance = np.max(min_distance)
            points = np.argwhere(select_distance == max_min_distance)[:, 1].tolist()
            for point in points:
                if point in select_p:
                    pass
                else:
                    select_p.append(point)
                    remain_p.remove(point)
                    break

        del eucl_mat, select_distance

        xtrain, ytrain = cx[remain_p], cy[remain_p]
        xtest, ytest = cx[select_p], cy[select_p]

        del cx, cy

        x_train.append(xtrain)
        y_train.append(ytrain)
        x_test.append(xtest)
        y_test.append(ytest)

    del x, y

    xtrain = np.concatenate(x_train, axis=0)
    ytrain = np.concatenate(y_train, axis=0)
    xtest = np.concatenate(x_test, axis=0)
    ytest = np.concatenate(y_test, axis=0)

    del x_train, y_train, x_test, y_test

    return xtrain, xtest, ytrain, ytest


"""Main Function for Segregation"""

# bharat


def split(csv_file_path, model_path, test_size=0.2, name='Normal', y_pred=None):
    """
    functions: splits the data into train and test set
    :param name: type of segregation (default value = 'Normal')
    :param csv_file_path: path of csv file in which images and labels are stored
    :param model_path: path of saved model used in kennard_stone method
                        - 'C:/Users/desktop/uploads/yuvnish_tsr_model_v5.h5'
    :param test_size: proportion of images to be put in test size (e.g 0.2, range=(0, 1)) (default value = 0.2)
    :param y_pred: predicted labels (default value is None, user specified if name=Difficult_samples)
    :return: train and test set images and labels based on method specified by user
    """
    x_data, y_data = load_dataset(csv_file_path=csv_file_path, size_of_image=32)
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    if name == "Normal":
        xtrain, xtest, ytrain, ytest = train_test_split(x_data, y_data, test_size=test_size)
        return xtrain, xtest, ytrain, ytest

    elif name == "Stratified":
        xtrain, xtest, ytrain, ytest = train_test_split(x_data, y_data, test_size=test_size, stratify=y_data)
        return xtrain, xtest, ytrain, ytest

    elif name == "Difficult_samples":
        xtrain, xtest, ytrain, ytest = difficult_sam(x_data, y_data, test_size=test_size, ypred=y_pred)
        return xtrain, xtest, ytrain, ytest

    elif name == "kennard_stone":
        xtrain, xtest, ytrain, ytest = kennard_stone(x_data, y_data, test_size=test_size, model_path=model_path)
        return xtrain, xtest, ytrain, ytest


"""Functions for Preprocessing of Image """


#bharat/ vartika


def adjust_gamma(image, gamma=2.0):
    """
      function: gamma adjustment of single image
      param:     image = input image
                 gamma = value of gamma
      returns: processed image
    """

    # gamma default = 2
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0)**invGamma)*255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

#bharat/ vartika


def CLAHE_colored(image):
    """
      function: applies adaptive histogram equalization on colored image
      param:     image = input image
      returns: processed image
    """

    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    image = cv2.split(image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image[0] = clahe.apply(image[0])
    image = cv2.merge(image)
    image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
    return image

#bharat/ vartika


def preprocessing(X_data, preprocess_list, preprocess_parameters):
    """
      function: preprocesses input images
      param:     X_data = list of all images to be preprocessed
                 preprocess_list = list of kinds of pre processing user wants to apply
                 preprocess_parameters = parameters of the chosen pre processing functions
      returns: list of pre processed images
    """

    #preprocess_list = ['adjust_gamma', 'CLAHE', 'denoise', 'binary_filter', 'edge_filter', 'normalize', 'standardize']
    # default preprocess_list=
    # preprocess_parameters = [{'gamma': 2.0}, '{'coloured': y/n}', {'h': value, 'hcolor': value, templateWindowSize': value, 'searchWindowSize': value} , ....]
    # Note - 1) Use anyone from adjust_gamma or denoise(both results in decrease of quality)
    #        2) If using singlechannel don't use colored preprocessing

    xdata = []
    for image in X_data:
        for i in range(0, len(preprocess_list)):
            preprocess = preprocess_list[i]
            parameters = preprocess_parameters[i]

            if preprocess == 'adjust_gamma':
                gamma = int(parameters['gamma'])
                image = adjust_gamma(image, gamma)

            elif preprocess == 'CLAHE':
                response = parameters['coloured']
                if response == 'y':
                    image = CLAHE_colored(image)                                     # CLAHE for colored
                else:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)                  # converting to single channel
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))       # CLAHE
                    image = clahe.apply(image)                                       # appling CLAHE

            elif preprocess == 'denoise':
                h = int(parameters['h'])  # default= 10
                hcolor = int(parameters['hcolor'])  # default= 10
                templateWindowSize = int(parameters['templateWindowSize'])  # default= 7
                searchWindowSize = int(parameters['searchWindowSize'])  # default= 21
                image = cv2.fastNlMeansDenoisingColored(
                    image, None, h, hcolor, templateWindowSize, searchWindowSize)   # remove noise + smoothing(colored)

            elif preprocess == 'binary_filter':
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)                  # converting to single channel
                image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                              cv2.THRESH_BINARY, 11, 2)            # Binary Filter

            elif preprocess == 'edge_filter':
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)                  # converting to single channel
                image = cv2.Laplacian(image, cv2.CV_64F)                          # laplacian edge filter

            elif preprocess == 'normalize':
                size = image.shape[0]
                normalizedImg = np.zeros((size, size))
                normalizedImg = cv2.normalize(image, normalizedImg, 0, 255, cv2.NORM_MINMAX)
                image = normalizedImg

            elif preprocess == 'standardize':
                image = image.astype('float32')
                # standardization
                mean, std = image.mean(), image.std()
                image = (image-mean)/std

        xdata.append(image)
    return np.array(xdata)


"""Re-training Functions"""

# sakshee/vartika

# sakshee/vartika


def design_CNN(d):
    '''
    function: defines each CNN layer with corresponding parameters
    param: d - d['list1'] = ['Conv2D', 'MaxPool2D', 'Flatten', 'Dense', 'BatchNormalization', 'Dropout']
               d['list2'] = [[16, 3, 1, 'same', 'relu'], [2, 1, 'same'], [], [64, 'relu'], [], [0.2]]
               d['img_size'] = img_size
               d['channels'] = channels
               d['num_classes'] = num_classes
    returns: predictions on test set (predictions[1] = value of accuracy on test set)
    '''

    img_size = d['img_size']
    channels = d['channels']
    num_classes = d['num_classes']
    model = Sequential()
    input_shape = (img_size, img_size, channels)
    model.add(InputLayer(input_shape))

    for i, add in enumerate(d['list1']):
        if add == 'Conv2D':
            filters = d['list2'][i][0]
            kernel_size = tuple(d['list2'][i][1], d['list2'][i][1])
            strides = tuple(d['list2'][i][2], d['list2'][i][2])
            padding = d['list2'][i][3]
            activation = d['list2'][i][4]

            model.add(Conv2D(filters, kernel_size, strides, padding, activation=activation))

        elif add == 'MaxPool2D':
            pool_size = tuple(d['list2'][i][0], d['list2'][i][0])
            strides = tuple(d['list2'][i][1], d['list2'][i][1])
            padding = d['list2'][i][2]

            model.add(MaxPool2D(pool_size, strides, padding))

        elif add == 'Flatten':
            model.add(Flatten())

        elif add == 'Dense':
            units = d['list2'][i][0]
            activation = d['list2'][i][1]

            model.add(Dense(units, activation))

        elif add == 'BatchNormalization':
            model.add(BatchNormalization())

        elif add == 'Dropout':
            rate = d['list2'][i][0]

            model.add(Dropout(rate=rate))

    # this can be given as a guideline that the last layer should be softmax. We don't want to hard code anything.

    # model.add(Flatten())
    # model.add(Dense(512, activation='relu'))
    # model.add(BatchNormalization())
    # model.add(Dropout(rate=0.5))
    # model.add(Dense(num_classes, activation='softmax'))

    return model
# sakshee


def compile_model(d, model):
    '''.
    param: d - d['opt_list1'] = ['SGD', 'RMSprop', 'Adam']
               d['opt_list2'] = [[0.001, 0.9, 0.01], [0.001, 0, 0.9, 1e-07], [0.001, 0.9, 0.99, 1e-07]]
               d['model'] = designed model
    returns: compiled model
    '''

    for i, optimizer in enumerate(d['opt_list1']):
        if optimizer == 'SGD':

            learning_rate = d['opt_list2'][i][0]
            momentum = d['opt_list2'][i][1]
            decay = d['opt_list2'][i][2]

            opt = keras.optimizers.SGD(learning_rate, momentum, decay)

        elif optimizer == 'RMSprop':

            learning_rate = d['opt_list2'][i][0]
            momentum = d['opt_list2'][i][1]
            rho = d['opt_list2'][i][2]
            epsilon = d['opt_list2'][i][3]

            opt = keras.optimizers.RMSprop(learning_rate, rho, momentum, epsilon)

        elif optimizer == 'Adam':

            learning_rate = d['opt_list2'][i][0]
            beta_1 = d['opt_list2'][i][1]
            beta_2 = d['opt_list2'][i][2]
            epsilon = d['opt_list2'][i][3]

            opt = keras.optimizers.Adam(learning_rate, beta_1, beta_2, epsilon)

    model = d['model']
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

    return model

# sakshee/vartika


def pre_trained_softmax(d):
    '''
    param: d - d['list1'] = ['ResNet50', 'VGG16', 'VGG19', 'InceptionV3', 'Xception']
             - d['num_classes'] = num_classes
             - d['img_size'] = img_size
             - d['channels'] = channels

    returns: pre_trained designed model
    '''
    img_size = d['img_size']
    channels = d['channels']
    num_classes = d['num_classes']
    input_shape = (img_size, img_size, channels)

    for i, pre_trained in enumerate(d['list1']):
        if pre_trained == 'ResNet50':
            model = ResNet50(include_top=True, weights='imagenet', input_shape=(img_size, img_size, channels))
            model.pop()
            model.add(Dense(num_classes, activation='softmax'))
            layer_count = len(model.layers)
            for l in range(layer_count-1):
                model.layers[l].trainable = False
        elif pre_trained == 'VGG16':
            model = VGG16(include_top=False, weights='imagenet', input_shape=(img_size, img_size, channels))
            model.pop()
            model.add(Dense(num_classes, activation='softmax'))
            layer_count = len(model.layers)
            for l in range(layer_count-1):
                model.layers[l].trainable = False

        elif pre_trained == 'VGG19':
            model = VGG19(include_top=False, weights='imagenet', input_shape=(img_size, img_size, channels))
            model.pop()
            model.add(Dense(num_classes, activation='softmax'))
            layer_count = len(model.layers)
            for l in range(layer_count-1):
                model.layers[l].trainable = False

        elif pre_trained == 'InceptionV3':
            model = InceptionV3(include_top=False, weights='imagenet', input_shape=(img_size, img_size, channels))
            model.pop()
            model.add(Dense(num_classes, activation='softmax'))
            layer_count = len(model.layers)
            for l in range(layer_count-1):
                model.layers[l].trainable = False

        elif pre_trained == 'Xception':
            model = Xception(include_top=False, weights='imagenet', input_shape=(img_size, img_size, channels))
            model.pop()
            model.add(Dense(num_classes, activation='softmax'))
            layer_count = len(model.layers)
            for l in range(layer_count-1):
                model.layers[l].trainable = False
    return model

# sakshee


def train_model(model, model_path, model_name, batch_size, epochs, X_train, Y_train, X_test, Y_test):
    '''
    param: model = compiled model
           model_name - name of model defined by user
           model_path = path in drive where trained model gets saved
           batch_size = variable integer from 1 to 1024 with step size 1 (default 64)
           epochs = variable integer from 1 to 200 with step size 1 (default 10)
           X_train - list of train images
           Y_train - list of labels of train images
           X_test - list of test images
           Y_test - list of labels of test images
    returns: trained model
    '''

    model.fit(X_train, Y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(X_test, Y_test),
              shuffle=True,)

    # the returned model must be saved. How to do that ? :p
    # model.save(model_path + '/' + model_name + '.hdf5')
    return model

# sakshee/vartika


def evaluate_model(model, X_test, Y_test):
    '''
    param: model = trained model
           X_test - list of test images
           Y_test - list of labels of test images
    returns: evaluations on test set (evaluations[1] = value of accuracy on test set)
    '''
    evaluations = model.evaluate(X_test, Y_test)

    return evaluations

#yuvnish, vartika


def predict_model(model, X):
    '''
    param: model = trained model
           X - list of images (train/test)
    returns: predictions on the train/ test set (as given in input) 
    '''
    Y_pred = model.predict(X)

    return Y_pred

# harshita


def ensemble(models_dict, no_of_models):
    '''
    function: creates ensemble of top classifiers
    param: model_dict - model_dict['model_name'] = accuracy
           no_of_models - number of models to create ensemble with
    returns: mean accuracy after ensembling, number of models used for ensembling
    '''
    sorted_tuples = sorted(models_dict.items(), key=lambda item: item[1])
    sorted_dict = {k: v for k, v in sorted_tuples}
    models = []
    acc = []
    for k, v in sorted_dict.items():
        models.append(k)
        acc.append(v)
    acc_mean = np.mean(acc[0:no_of_models])
    models_used = models[0:no_of_models]
    return acc_mean, models_used


"""Visualozation Functions"""

# yuvnish


def model_summary(model):
    '''
    function: returns summary of model to check which layers are present in the model
    param: model - saved model
    returns: summarry of model
    '''
    return model.summary()

# ankur


def visualise_activations(layer_name, model):
    '''
    function: to visualize output after a specific layer of model
    param: layer_name - name of layer of model whose output is needed
           model - saved model
    returns: output image
    '''
    explainer = ExtractActovations()
    grid = explainer.explain((to_predict, None), model, [layer_name])
    fig, ax = plt.subplots(1, 1, figsize=(32, 32))
    ax[0].imshow(grid, cmap='binary_r')

# yuvnish


def Classification_report(x, y, model):
    '''
    function: returns classification report of model on data passed
    param: x - list of images
           y - list of labels
           model - saved model
    returns: classification report of model on data
    '''
    x = numpy.array(x)
    y = numpy.array(y)
    y = to_categorical(y)
    y_pred = predict_model(model, x)
    y_pred = numpy.argmax(y_pred, axis=1)
    y = numpy.argmax(y, axis=1)
    return classification_report(y, y_pred)

# yuvnish


def accuracy_and_loss_plot(model, datadir):
    '''
    function: plots of accuracy and loss
    param: model - saved model
           datadir - path where plots needs to be saved
    returns: path where lots are saved
    '''
    plt.plot(model.history.history['accuracy'], label='Train_accuracy')
    plt.plot(model.history.history['val_accuracy'], label='Test_accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend(loc="upper left")
    output_path_accuracy = os.path.join(d['datadir'], 'accuracy.png')
    plt.savefig(output_path_accuracy)

    plt.plot(model.history.history['loss'], label='Train_loss')
    plt.plot(model.history.history['val_loss'], label='Test_loss')
    plt.title('Model Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    output_path_loss = os.path.join(d['datadir'], 'loss.png')
    plt.savefig(output_path_loss)
    return output_path_accuracy, output_path_loss

#harshita/ sakshee/ muskan


def plot_cm(Y_test, y_pred, figsize=(16, 16)):
    '''
    function: plots confusion matrix and returns data frame
    param: model - saved model
           datadir - path where plots needs to be saved
    returns: path where lots are saved
    '''
    cm = confusion_matrix(Y_test, y_pred, labels=np.unique(Y_test))
    cm_sum = np.sum(cm, axis=1, keepdims=True)
    cm_perc = cm / cm_sum.astype(float) * 100
    annot = np.empty_like(cm).astype(str)
    nrows, ncols = cm.shape

    for i in range(nrows):
        for j in range(ncols):
            c = cm[i, j]
            p = cm_perc[i, j]

            if i == j:
                s = cm_sum[i]
                annot[i, j] = '%.1f%%\n%d/%d' % (p, c, s)

            elif c == 0:
                annot[i, j] = ''

            else:
                annot[i, j] = '%.1f%%\n%d' % (p, c)

    cm = pd.DataFrame(cm, columns=np.unique(Y_test), index=np.unique(y_pred))

    cm.index.name = 'Actual'
    cm.columns.name = 'Predicted'

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(cm, cmap="YlGnBu", annot=annot, fmt='', ax=ax, annot_kws={"size": 9})
    output_path_confusion_matrix = os.path.join(d['datadir'], 'confusion_matrix.png')
    plt.savefig(output_path_confusion_matrix)
    return cm, output_path_confusion_matrix

# harshita/muskan


def bargraphs(model, x_test, y_test, n_classes, datadir):
    '''
    function: bar chart plot function
    param: model = saved model
           n_classes - number of classes
           datadir - path where plot needs to be saved
           x_test = test set images
           y_test = test set labels
    return:
    '''
    ypred = predict_model(model, x_test)
    df, _ = plot_cm(y_test, ypred, (16, 16))
    classes = list(range(n_classes))
    num_classes = n_classes
    cmap = plt.cm.gist_rainbow
    norm = mpl.colors.Normalize(vmin=0, vmax=len(classes) - 1)
    colors = [cmap(norm(i)) for i in range(len(classes))]
    cmpltnt_rela = cm_drops.plot.bar(stacked=True, color=colors, fontsize=8, figsize=(15, 15))
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=2, fontsize=8)

    plt.tick_params('x', labelrotation=90, size=10)

    plt.tight_layout()
    output_path_bar_chart = os.path.join(d['datadir'], 'bar_chart.png')
    plt.savefig(output_path_bar_chart)
    return output_path_bar_chart
