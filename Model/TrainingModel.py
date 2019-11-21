import pandas as _pd
import matplotlib.pyplot as _plt
import seaborn as _sns
import pickle as _pickle

from imblearn.combine import SMOTETomek as _SMOTETomek

from sklearn.metrics import confusion_matrix as _confusion_matrix
from sklearn.metrics import classification_report as _classification_report
from sklearn.model_selection import train_test_split as _train_test_split
from sklearn.ensemble import RandomForestClassifier as _RandomForestClassifier

LABELS = ['No', 'Si']

#definimos funciona para mostrar los resultados
def _mostrar_resultados(y_test, pred_y):
    conf_matrix = _confusion_matrix(y_test, pred_y)
    _plt.figure(figsize=(10, 10))
    _sns.heatmap(conf_matrix, xticklabels=LABELS, yticklabels=LABELS, annot=True, fmt="d");
    _plt.title("Confusion matrix")
    _plt.ylabel('True class')
    _plt.xlabel('Predicted class')
    print (_classification_report(y_test, pred_y))

def TrainingModel(DataSet, OutputPathModel, Verbose=True):
    if type(DataSet) == _pd.core.frame.DataFrame:
        df = DataSet
    else:
        df = _pd.read_csv(DataSet)
        df.index = df['Id Unico']
        df.drop(['Id Unico'], inplace = True, axis = 1)
    
    df['Abandono'] = df['Ab'].apply(lambda x: 0 if x < 0 else 1)
    df.drop(['Ab'], inplace = True, axis = 1)
    
    if Verbose:
        print("Number of Rows: {}\nNumber Of Columns: {}\n".format(df.shape[0],df.shape[1]))
        print("Number of Students that Not Dropped (0) and Dropped (1)")
        print(_pd.value_counts(df['Abandono'], sort = True))
        count_classes = _pd.value_counts(df['Abandono'], sort = True)
        count_classes.plot(kind = 'bar', rot=0)
        _plt.xticks(range(2), LABELS)
        _plt.title("Frequency by observation number")
        _plt.xlabel("Abandono")
        _plt.ylabel("Number of Observations");

    y = df['Abandono']
    X = df.drop('Abandono', axis=1)

    seed = 46
    #dividimos en sets de entrenamiento y test
    X_train, X_test, y_train, y_test = _train_test_split(X, y, train_size=0.8, random_state = seed)
    
    #os_us = _SMOTETomek(sampling_strategy='all', ratio=0.6, )
    os_us = _SMOTETomek(sampling_strategy='auto', ratio=0.6, random_state=seed)
    X_train_res, y_train_res = os_us.fit_sample(X_train, y_train)

    if Verbose:
        print ("\nDistribution before resampling {}".format(Counter(y_train)))
        print ("Distribution after resampling {}".format(Counter(y_train_res)))
    
    
    num_trees = 50
    rfc = _RandomForestClassifier(n_estimators = num_trees, 
                             #class_weight="balanced", 
                             random_state = seed, 
                             max_features = 4)
    rfc.fit(X_train, y_train)
    
    if Verbose:
        pred_y = rfc.predict(X_test)
        print()
        _mostrar_resultados(y_test, pred_y)
        print("Saving the model in the following path: {}".format(OutputPathModel))
    
    _pickle.dump(rfc, open(OutputPathModel, 'wb'))
    
    if Verbose:
        _plt.show()


if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    DataSet = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\DataSets_Created\New_DataSet_OneStudentByRow_std.csv'
    OutputPathModel = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Model\RandomForestClassifier_Model.sav'
    TrainingModel(DataSet, OutputPathModel, Verbose=True)