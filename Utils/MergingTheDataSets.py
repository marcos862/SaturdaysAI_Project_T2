import os
import pandas as pd

def MergingTheDataSets(path2MainDF, path2GenderDF, path2LabeledDF, OutputFilename, SaveToCsv = True, Verbose=False):
    df_gender = pd.read_csv(path2GenderDF)
    df_gender.drop(['Nombre', 'Unnamed: 0'], axis = 1, inplace = True)
    df_gender = df_gender.drop_duplicates()
    
    df_main = pd.read_csv(path2MainDF)
    df_labels = pd.read_csv(path2LabeledDF)
    df_main.drop(['Unnamed: 0'], axis=1, inplace=True)
    df_labels.drop(['Unnamed: 0'], axis=1, inplace=True)
    
    columnsToDrop = set(df_labels.columns) - set(['No. Control', 'Abandono'])
    df_labels.drop(columnsToDrop, axis = 1, inplace=True)
    df_main_l = df_main.merge(df_labels, how='left', on=['No. Control'])

    if SaveToCsv:
        tempFilename = OutputFilename.split("\\")
        OutputFolder = OutputFilename.replace(tempFilename[-1], "")
        if Verbose: print("Saving the merge bewteen main and labels in: {}".format(os.path.join(OutputFolder, 'FinalDataFrame_with_labels.csv')))
        df_main_l.to_csv(os.path.join(OutputFolder, 'FinalDataFrame_with_labels.csv'))
    
    if Verbose:
        if df_main.shape[0] != df_main_l.shape[0]:
            print("The merge bewteen df_main and df_labeled was not right, the number of rows before and after are not the same")
        else:
            print("The merge bewteen df_main and df_labeled was successful, the number of rows before and after is the same")
    
    df_main_lg = pd.merge(df_main_l, df_gender, how='left', on=['No. Control'])
    
    if Verbose:
        if df_main_l.shape[0] != df_main_lg.shape[0]:
            print("The merge bewteen df_main_labeled and df_gender was not right, the number of rows before and after are not the same")
        else:
            print("The merge bewteen df_main_labeled and df_gender was successful, the number of rows before and after is the same")
            
    if SaveToCsv:
        if Verbose: print("Saving the dataframe merged with labels and genders in: {}".format(OutputFilename))
        df_main_lg.to_csv(OutputFilename)
        
    return df_main_lg

if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    path2MainDF = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\FinalDataFrame.csv'
    path2GenderDF = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\Gender.csv'
    path2LabeledDF = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\StudentsLabeledByCycle.csv'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\FinalDataFrame_with_labels_and_genders.csv'
    MergingTheDataSets(path2MainDF, path2GenderDF, path2LabeledDF, OutputFilename, Verbose=True)