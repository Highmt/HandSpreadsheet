import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from res.SSEnum import HandEnum

CMFile = 'testCM_KNN'
labels = HandEnum.NAME_LIST.value
cmData = pd.read_csv('{}.csv'.format(CMFile), header=None)
sum = cmData[0:1].sum(axis=1)[0]
cmData.index = labels
cmData.columns = labels
fig, ax = plt.subplots(figsize=(9, 7))
g = sns.heatmap(cmData / sum, annot=True, annot_kws={"size": 18}, cmap="Blues", fmt='.2g', ax=ax)  #  正規化したものを表示
g.set_xticklabels(g.get_xticklabels(), rotation=340, fontsize=15)
g.set_yticklabels(g.get_yticklabels(), rotation=70, fontsize=15)
plt.savefig('{}.pdf'.format(CMFile))
plt.show()
