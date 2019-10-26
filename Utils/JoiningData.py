# coding=utf-8
"""
Saturdays AI 
    - Team 2 
        - Predicting the school desertion

This script will be used to join all the data from the datasets.
"""
import os
import pandas as pd
import numpy as np

def _CorrectingColumnNames(df): # by convention, the _ means this is a private function
    """
        There are some columns that have the name
        duplicated, this is caused because they are
        taking just the three first letters of the 
        Subject to determine the name of the column.
        
        So, to avoid further issues, we need to remove
        the names duplicated.
        
        We will be doing this addind a consecutive number
        when the names are duplicated.
    """
    NumColumns = len(df.columns)
    ColumnsNameCorrected = []
    Subject = []
    for i in range(NumColumns):
        if df.columns[i] == 'Faltas':
            SubjectName = df.columns[i-1]
            if SubjectName in Subject:
                counter = 0
                while (str(SubjectName) + str(counter)) in Subject:
                       counter += 1
                SubjectName = str(SubjectName) + str(counter)
            Subject.append(SubjectName)
            ColumnsNameCorrected.pop() # The previous added was the Name of theSubject, discarding it
            ColumnsNameCorrected.append(SubjectName) # Adding the corrected name
            ColumnsNameCorrected.append('Faltas_' + str(SubjectName))
        else:
            ColumnsNameCorrected.append(str(df.columns[i]))
    df.columns = ColumnsNameCorrected
    return(df, Subject)

def CleaningRawDataFrame(df):
    """
        This function will be removing all the columns and
        rows not required.
        
        Also, it's calling a function to remove the issue with the
        columns names duplications.
    """
    df.dropna(axis = 1, how = 'all', inplace = True)
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace = True)
    df.drop(['No. Cons', 'PROMEDIO', 'MATERIAS REP', '% REPROBACIÓN', '% APROBACIÓN'], axis=1, inplace=True)
    
    df, Subject = _CorrectingColumnNames(df)
    
    count = 0
    for i in range(df.shape[0]):
        if np.isnan(float(df.iloc[i][0])):
            count = i
            break
    df2 = df.iloc[0:count]
    if 'TUT' in Subject:
        df2.drop(['TUT', 'Faltas_TUT'], axis=1, inplace=True)
        Subject.remove('TUT')
    for s in Subject:
        if 'TAL' in s:
            df2[s] = df[s].apply(lambda x: 0 if x=='NP' else 7 if x == 'AC' else 5)
    df2['Repetidor'] = df2['Nombre'].apply(lambda x: 'Si' if '(R)' in x else 'No')
    df2.drop(['Nombre'], axis=1, inplace=True)
    return df2, Subject

def ReformatingDataFrame(df, Subject):
    """
        Reformating the database, changing columns to rows to
        be able to join, easily, all the database that are splitted
        by period, group and partial.
    """
    Missings = ["Faltas_" + str(c) for c in Subject]
    ColsToStack = Subject + Missings
    id_vars = set(df.columns) - set(ColsToStack)
    df_stack = pd.melt(df, id_vars=id_vars, value_vars=ColsToStack)
    df_stack['Tipo'] = df_stack['variable'].apply(lambda x: 'Faltas' if 'Faltas_' in x else 'Calificacion')
    df_stack['Materia'] = df_stack['variable'].apply(lambda x: x.replace("Faltas_", ""))
    df_stack.drop('variable', axis = 1, inplace=True)
    groupCols = list(set(df_stack.columns) - set(['Tipo', 'value']))
    df_unstack = pd.pivot_table(df_stack, index=groupCols, columns=['Tipo'], values=['value'], aggfunc=lambda x: ' '.join(str(v) for v in x))
    df_unstack.reset_index(inplace = True, col_level=1)
    df_unstack.columns = df_unstack.columns.droplevel()
    return(df_unstack)
    
def JoinAllFiles(PathToFiles, OutputFilename, SaveToCsv = True, Verbose=False):
    """
        This is the main function that will be navigating through the folder
        structure:
            Period/Cycle (Folder)
                Partials (Folder)
                    Semester/Group (file)
        
        Reading the files, adding the columns Cycle, Partial, Semester and Group
        Removing some columns/rows not used
        Reformating the data to move all the Subjects that are in columns to rows
        Joining all the files in just one dataframe
    """
    df = pd.DataFrame()                                                         # It create a new empty dataframe
    
    Cycles = os.listdir(PathToFiles)                                            # Read all the folders corresponding to the Cycle
    for Cycle in Cycles:                                                        # For each cycle folder
        if not os.path.isdir(os.path.join(PathToFiles, Cycle)):                 # if the file is not a directory continue with the following
            continue
        if Verbose: print("Cycle = {}".format(Cycle))                           # Printing the name of the Current Cycle folder
        Partials = os.listdir(os.path.join(PathToFiles, Cycle))                 # Listing all folders corresponding to the Partials
        for Partial in Partials:
            if not os.path.isdir(os.path.join(PathToFiles, Cycle, Partial)):    # if the file is not a directory continue with the following
                continue
            if Verbose: print("    Partial = {}".format(Partial))
            Groups = os.listdir(os.path.join(PathToFiles, Cycle, Partial))      # List all the files inside the Cycle/Partial Folder
            for Group in Groups:
                if os.path.isdir(os.path.join(PathToFiles, Cycle, Partial, Group)):    # if the file is not a directory continue with the following
                    continue
                if Verbose: print("        Group = {}".format(Group))
                file = os.path.join(PathToFiles, Cycle, Partial, Group)         # Getting the fullpath and filename to the file
                df_temp = pd.read_html(file)                                    # Reading the files as HTML, it will produce a list of dataframes
                df_temp = df_temp[1]                                            # In our case, the Dataframe that is important is the [1]
                df_temp, Subject = CleaningRawDataFrame(df_temp)
                df_temp = ReformatingDataFrame(df_temp, Subject)
                df_temp['Cycle'] = Cycle
                df_temp['Partial'] = Partial
                df_temp['Semester'] = Group.split(".")[0][0]
                df_temp['Group'] = Group.split(".")[0][1]
                df = pd.concat([df, df_temp], ignore_index = True)
    if SaveToCsv:            
        df.to_csv(OutputFilename)
    return(df)
    
if __name__ == "__main__":
    PathToFiles = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\FinalDataFrame.csv'
    JoinAllFiles(PathToFiles, OutputFilename, Verbose=True)