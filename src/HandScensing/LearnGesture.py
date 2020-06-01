import csv
import datetime
import pickle

import numpy as np
import pandas as pd
from sklearn import metrics, svm
from sklearn.externals import joblib
from sklearn.metrics import classification_report, confusion_matrix

from sklearn.model_selection import train_test_split, GridSearchCV
from pycm import ConfusionMatrix

import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

np.random.seed(1671)  # for reproducibility

# network and training
DROPOUT = 0.2

# data: shuffled and split between train and test sets
read_data0 = pd.read_csv('../../res/data/0_FREE.csv', sep=',', index_col=0)
read_data1 = pd.read_csv('../../res/data/1_PINCH_IN.csv', sep=',', index_col=0)
read_data2 = pd.read_csv('../../res/data/2_PINCH_OUT.csv', sep=',', index_col=0)
read_data3 = pd.read_csv('../../res/data/3_REVERSE.csv', sep=',', index_col=0)
read_data4 = pd.read_csv('../../res/data/4_PALM.csv', sep=',', index_col=0)
read_data5 = pd.read_csv('../../res/data/5_GRAB.csv', sep=',', index_col=0)

read_data = pd.concat([read_data0, read_data1, read_data2, read_data3, read_data4, read_data5], ignore_index=True)
data = read_data.drop("label", axis=1).values
label = read_data["label"].values


train_data, test_data, train_label, test_label = train_test_split(data, label, test_size=0.2, stratify=label)

# normalize
print(train_data.shape[0], 'train samples')
print(test_data.shape[0], 'test samples')





print("train start")
print("# Tuning hyper-parameters for accuracy")

#  KNN------------------------------------------------
# knn_parameters = {'n_neighbors': [7, 11, 19],
#                     'weights': ['uniform', 'distance'],
#                     'metric': ['euclidean', 'manhattan']
#                   }
# scores = ['precision', 'recall', 'f1']
#
# clf = GridSearchCV(KNeighborsClassifier(), knn_parameters, cv=5,
#                    scoring='accuracy', n_jobs=-1)
# clf.fit(train_data, train_label)
# model = "KNN"
# ------------------------------------------------------


#   SVC-------------------------------------------------
tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [0.1, 1, 10]},
                    {'kernel': ['linear'], 'C': [0.1, 1, 10]}]
scores = ['precision', 'recall', 'f1']
#  グリッドサーチと交差検証法
clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=5,
                    scoring='accuracy', n_jobs=-1)
clf.fit(train_data, train_label)
model = "SVC"
# ------------------------------------------------------

#   NN-------------------------------------------------
# nn_parameters = [{
#         # 最適化手法
#         "solver": ["lbfgs", "sgd", "adam"],
#         # 隠れ層の層の数と、各層のニューロンの数
#         "hidden_layer_sizes": [(100,), (100, 10), (100, 100, 10), (100, 100, 100, 10)],
# }]
# scores = ['precision', 'recall']
# clf = GridSearchCV(MLPClassifier(early_stopping=True), param_grid=nn_parameters, cv=5,
#                    scoring='accuracy', n_jobs=-1)
# clf.fit(train_data, train_label)
# model = "NN"
# ------------------------------------------------------

print(clf.best_estimator_)
print(classification_report(test_label, clf.predict(test_data)))
pickle.dump(clf, open('../../res/learningModel/GestureDetectModel_{}.pkl'.format(model), 'wb'))

# モデルを読み込む --- (*4)
pred = clf.predict(test_data)
print(pred)
print(clf.predict_proba(test_data))
touch_true = test_label.tolist()
labels = ["FREE", "PINCH_IN", "PINCH_OUT", "REVERSE", "PALM", "GRIP", ]

c_matrix = confusion_matrix(touch_true, pred)
print(c_matrix)
cm_pd = pd.DataFrame(c_matrix, columns=labels, index=labels)
sum = int(test_data.shape[0]) / int(labels.__len__())  # 各ラベルの数
fig, ax = plt.subplots(figsize=(9, 8))
sns.heatmap(cm_pd / sum, annot=True, cmap="Reds", fmt='.4g')  #  正規化したものを表示
plt.savefig('../../res/learningResult/cvCM_{}.png'.format(model))
with open('../../res/learningResult/cvCM_{}.csv'.format(model), 'w') as file:
    writer = csv.writer(file, lineterminator='\n')
    writer.writerows(c_matrix)
print(classification_report(test_label, pred))
print("正答率 = ", metrics.accuracy_score(test_label, pred))
