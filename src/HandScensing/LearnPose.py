import csv
import datetime
import pickle
import sys

import numpy as np
import pandas as pd
from sklearn import metrics, svm
from sklearn.metrics import classification_report, confusion_matrix

from sklearn.model_selection import train_test_split, GridSearchCV

import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from res import SSEnum
from res.SSEnum import FeatureEnum
from src.HandScensing.HandListener import HandData
from src.HandScensing.Predictor import convertLearningPS

# np.random.seed(1671)  # for reproducibility
ver = "master"
# network and training
DROPOUT = 0.2
data_pass = '../../res/data/train/{}'.format(ver)
lr_label = ['left', 'right']

# どれかひとつだけTrueにする
KNN_enable = True
SVC_enable = False
NN_enable = False

def convertLearningDF(data: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(columns=FeatureEnum.FEATURE_LIST.value)
    hand = HandData()
    for i, ps in data.iterrows():
        hand.loadPS(ps)
        d = convertLearningPS(hand)
        df = df.append(d, ignore_index=True)
    return df


for i in range(2):
    print("------------- {} start -------------".format(lr_label[i]))
    read_data = pd.read_csv(data_pass + '/' + lr_label[i] + 'Data.csv', sep=',', index_col=0)
    data = convertLearningDF(read_data).drop("Label", axis=1).values
    label = read_data["Label"].values
    train_data, test_data, train_label, test_label = train_test_split(data, label, test_size=0.2, stratify=label)

    # normalize
    print(train_data.shape[0], 'train samples')
    print(test_data.shape[0], 'test samples')

    print("train start")
    print("# Tuning hyper-parameters for accuracy")

    #  KNN------------------------------------------------
    if KNN_enable:
        knn_parameters = {'n_neighbors': [7, 11, 19],
                          'weights': ['uniform', 'distance'],
                          'metric': ['euclidean', 'manhattan']
                          }
        scores = ['precision', 'recall', 'f1']

        clf = GridSearchCV(KNeighborsClassifier(), knn_parameters, cv=5,
                           scoring='accuracy', n_jobs=-1, verbose=10)
        clf.fit(train_data, train_label)
        model = "KNN"
    # ------------------------------------------------------

    #   SVC-------------------------------------------------
    elif SVC_enable:
        svc_parameters = {'kernel': ['rbf'],
                            'gamma': [1e-4],
                             'C': [10]}
        scores = ['precision', 'recall', 'f1']
        #  グリッドサーチと交差検証法
        clf = GridSearchCV(svm.SVC(probability=True), svc_parameters, cv=5,
                           scoring='accuracy', n_jobs=-1, verbose=10)
        clf.fit(train_data, train_label)
        model = "SVC"
    # ------------------------------------------------------

    #   NN-------------------------------------------------
    elif NN_enable:
        nn_parameters = [{
            # 最適化手法
            "solver": ["adam"],
            # 隠れ層の層の数と、各層のニューロンの数
            "hidden_layer_sizes": [(100, 100, 100, 10)],
            'activation': ["logistic", "relu", "tanh"],
        }]
        scores = ['precision', 'recall']
        clf = GridSearchCV(MLPClassifier(early_stopping=True), param_grid=nn_parameters, cv=5,
                           scoring='accuracy', n_jobs=-1, verbose=10)
        clf.fit(train_data, train_label)
        model = "NN"
    # ------------------------------------------------------
    else:
        sys.exit(1)
    print(clf.best_estimator_)
    print(classification_report(test_label, clf.predict(test_data)))
    pickle.dump(clf, open('../../res/learningModel/{}Model_{}_{}.pkl'.format(lr_label[i], model, ver), 'wb'))

    # モデルを読み込む --- (*4)
    pred = clf.predict(test_data)
    print(pred)
    print(clf.predict_proba(test_data))
    touch_true = test_label.tolist()
    labels = SSEnum.HandEnum.NAME_LIST.value

    c_matrix = confusion_matrix(touch_true, pred)
    print(c_matrix)
    cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
    sum = int(test_data.shape[0]) / int(labels.__len__())  # 各ラベルの数
    fig, ax = plt.subplots(figsize=(8, 7))
    plt.tick_params(labelsize=10)
    sns.heatmap(cm_pd / sum * 100, annot=True, cmap="Blues", fmt='.4g', ax=ax)  # パーセントで表示
    plt.savefig('../../res/learningResult/{}cvCM_{}.png'.format(lr_label[i], model))
    with open('../../res/learningResult/{}cvCM_{}.csv'.format(lr_label[i], model), 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(c_matrix)
    print(classification_report(test_label, pred))
    print("正答率 = ", metrics.accuracy_score(test_label, pred))

    print("------------- {} end ------------\n".format(lr_label[i]))
plt.show()
