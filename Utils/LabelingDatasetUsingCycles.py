import pandas as pd
import numpy as np

def LabelingDatasetUsingCycles(path2csv, OutputFilename, SaveToCsv = True, Verbose=False):
    df = pd.read_csv(path2csv)
    df.drop(['Unnamed: 0'], axis=1, inplace=True)
    df.drop(['Materia', 'Repetidor', 'Calificacion', 'Faltas', 'Partial'], axis=1, inplace = True)
    df_pivot = pd.pivot_table(df, index=['No. Control'], columns=['Cycle'], values=['Semester'], aggfunc=np.max).copy()
    df_pivot.reset_index(col_level=1, inplace= True)
    df_pivot.columns = df_pivot.columns.droplevel()
    df_pivot['Abandono'] = ''
    df_pivot['Ultimo Ciclo'] = ''
    NoRows = df_pivot.shape[0]
    NoColumns = df_pivot.shape[1]
    if Verbose: print("No Rows: " + str(NoRows) + ", No Columns: " + str(NoColumns))
    
    for i in range(NoRows):
        Abandono = 'Si'
        if(not np.isnan(df_pivot.iloc[i][-3])):
            #print("Row = " + str(i) + ", Column = 5")
            Abandono = 'No'
            LastSemester = df_pivot.columns[-3]
        else:
            for j in range(NoColumns-3, 0, -1): # Removing 'No. Control' and 'Abandono' columns and checking from last to first cycle
                #print("Row = " + str(i) + ", Column = " + str(j))
                if not np.isnan(df_pivot.iloc[i][j]):
                    LastSemester = df_pivot.columns[j]
                    if df_pivot.iloc[i][j] == 6:
                        Abandono = 'No'
                    break
        #print("   Abandono? " + Abandono)
        df_pivot.iloc[i, -2] = Abandono # This is the 'Abandono' Column
        df_pivot.iloc[i, -1] = LastSemester # This is the 'Abandono' Column
        

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
    path2csv = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\FullDataSet.csv'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\StudentsLabeledByCycle.csv'
    LabelingDatasetUsingCycles(path2csv, OutputFilename, Verbose=True)