import pandas as pd
import numpy as np

def LabelingDatasetUsingCycles(path2csv, OutputFilename, SaveToCsv = True, Verbose=False):
    df = pd.read_csv(path2csv)
    df.drop(['Unnamed: 0'], axis=1, inplace=True)
    df.drop(['Materia', 'Repetidor', 'Calificacion', 'Faltas', 'Partial'], axis=1, inplace = True)
    df_pivot = pd.pivot_table(df, index=['No. Control'], columns=['Cycle'], values=['Faltas'], aggfunc=np.sum).copy()
    df_pivot.reset_index(col_level=1, inplace= True)
    df_pivot.columns = df_pivot.columns.droplevel()
    df_pivot['Abandono'] = ''
    NoRows = df_pivot.shape[0]
    NoColumns = df_pivot.shape[1]
    if Verbose: print("No Rows: " + str(NoRows) + ", No Columns: " + str(NoColumns))
    
    for i in range(NoRows):
        Abandono = 'Si'
        '''
            Needs to be stablish a limit of missings to label the students as 
            Dropped or Not Dropped
        '''
        df_pivot.iloc[i, -1] = Abandono # This is the 'Abandono' Column

    if Verbose:
        NoDropped = df_pivot[df_pivot['Abandono']=='No'].shape[0]
        Dropped = df_pivot[df_pivot['Abandono']=='Si'].shape[0]
        print("The Number of Alumni that Dropped the studies is: {}".format(Dropped))
        print("The Number of Alumni that No Dropped the studies is: {}".format(NoDropped))
        print("The porcentage of Alumni that dropped the studies is: {}".format(Dropped/(NoDropped+Dropped)))
    
    if SaveToCsv:                                                               # if SaveToCsv is True
        if Verbose: print("Saving the dataframe in: {}".format(OutputFilename))
        df_pivot.to_csv(OutputFilename)

if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    path2csv = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\FinalDataFrame.csv'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\StudentsLabeledByCycle.csv'
    LabelingDatasetUsingCycles(path2csv, OutputFilename, Verbose=True)