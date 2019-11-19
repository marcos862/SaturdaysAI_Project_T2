import pandas as pd

def MergingTheDataSets(path2MainDF, path2LabeledDF, OutputFilename, SaveToCsv = True, Verbose=False):
    df_main = pd.read_csv(path2MainDF)
    df_labels = pd.read_csv(path2LabeledDF)
    df_main.drop(['Unnamed: 0'], axis=1, inplace=True)
    df_labels.drop(['Unnamed: 0'], axis=1, inplace=True)
    
    columnsToDrop = set(df_labels.columns) - set(['Id Unico', 'Abandono', 'Ultimo Ciclo'])
    df_labels.drop(columnsToDrop, axis = 1, inplace=True)
    df_main_l = df_main.merge(df_labels, how='left', on=['Id Unico'])

    if Verbose:
        if df_main.shape[0] != df_main_l.shape[0]:
            print("The merge bewteen df_main and df_labeled was not right, the number of rows before and after are not the same")
        else:
            print("The merge bewteen df_main and df_labeled was successful, the number of rows before and after is the same")
    
    if SaveToCsv:
        if Verbose: print("Saving the dataframe merged with labels in: {}".format(OutputFilename))
        df_main_l.to_csv(OutputFilename, encoding='utf-8-sig')
        
    return df_main_l

if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    path2MainDF = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\DataSets_Created\FullDataSet.csv'
    path2LabeledDF = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\DataSets_Created\StudentsLabeledByCycle.csv'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\DataSets_Created\FullDataSet_with_labels.csv'
    MergingTheDataSets(path2MainDF, path2LabeledDF, OutputFilename, Verbose=True)