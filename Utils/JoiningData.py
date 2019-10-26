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
    df.dropna(axis = 1, how = 'all', inplace = True)                            # First, we remove the columns that are all 'NaN'
    df.columns = df.iloc[0]                                                     # Taking the first row as the name of the columns
    df.drop(df.index[0], inplace = True)                                        # Removing the first row that we just convert to the columns names
    columnsToRemove = ['No. Cons', 'PROMEDIO', 'MATERIAS REP', '% REPROBACIÓN', '% APROBACIÓN']
    df.drop(columnsToRemove, axis=1, inplace=True)                              # Removing columns that are not useful

    df, Subject = _CorrectingColumnNames(df)                                    # Renaming the columns that have the same name

    # The dataframe, as it is, at the end, contain the full name of the subjects
    # As this information is not useful, at the moment, we want to remove that part of the dataframe
    # we identify this part of the dataframe because there is an empty row between the data from alumnis
    # and the real name of the subjects
    RowNumber = 0                                                               # Starting a counter for the row number
    for i in range(df.shape[0]):                                                # For each row in the dataframe
        if np.isnan(float(df.iloc[i][0])):                                      # Checking if the No Control column in the current row is a 'NaN'
            RowNumber = i                                                       # If that is the case, we reached the end of the data we care
            break                                                               # we break the for.
    # https://www.dataquest.io/blog/settingwithcopywarning/
    df2 = df.iloc[0:RowNumber].copy()                                           # Doing a copy of the original dataframe with just the data we want
    if 'TUT' in Subject:                                                        # If we have a column with the grades from 'TUT' subject
        df2.drop(['TUT', 'Faltas_TUT'], axis=1, inplace=True)                   # Removing the 'TUT' and 'Faltas_TUT' as this columns doesnt have useful information
        Subject.remove('TUT')                                                   # Also, removing the 'TUT' from the list of subjects
    
    # The workshop subjects ('TAL') doesnt have a numeric grade, so, we need to
    # change the non numeric grade to numeric grade, we are doing that as follows:
    #   'NP' = 0    # NP means 'No presento' (Exam not taken)
    #   'AC' = 7    # AC means 'Acreditado'  (Exam was passed)
    #   'NA' = 5    # NA means 'No Acreditado' (Exam was not passed)
    for s in Subject:                                                           # Checking all the Subjects in the list
        if 'TAL' in s:                                                          # if the subject is a workshop ('TAL')
            df2[s] = df[s].apply(lambda x: 0 if x=='NP' else 7 if x == 'AC' else 5) # Changing all the non-numeric grades to numeric grades
    
    # Finally, we know that, if an alumni has the string '(R)' in his/her name
    # that means that she/he is coursing again a class or the semester
    df2['Repetidor'] = df2['Nombre'].apply(lambda x: 'Si' if '(R)' in x else 'No')  # Creating a new column to show if the alumni is coursing again the class/semester
    df2.drop(['Nombre'], axis=1, inplace=True)                                  # Removing the 'Nombre' Column because is not usefull anymore
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
    df_unstack = pd.pivot_table(df_stack, index=groupCols, columns=['Tipo'], values=['value'], aggfunc=lambda x: ' '.join(str(v) for v in x)) #https://medium.com/@enricobergamini/creating-non-numeric-pivot-tables-with-python-pandas-7aa9dfd788a7
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
        for Partial in Partials:                                                # for each cycle/partial
            if not os.path.isdir(os.path.join(PathToFiles, Cycle, Partial)):    # if the file is not a directory continue with the following
                continue
            if Verbose: print("    Partial = {}".format(Partial))               # Print the name of the current Partial folder
            Groups = os.listdir(os.path.join(PathToFiles, Cycle, Partial))      # List all the files inside the Cycle/Partial Folder
            for Group in Groups:                                                # for each cycle/patial/group file
                if os.path.isdir(os.path.join(PathToFiles, Cycle, Partial, Group)):    # if the file is not a directory continue with the following
                    continue
                if Verbose: print("        Group = {}".format(Group))           # Print the name of the current Group File
                file = os.path.join(PathToFiles, Cycle, Partial, Group)         # Getting the fullpath and filename to the file
                df_temp = pd.read_html(file)                                    # Reading the files as HTML, it will produce a list of dataframes
                df_temp = df_temp[1]                                            # In our case, the Dataframe that is important is the [1]
                df_temp, Subject = CleaningRawDataFrame(df_temp)                # Cleaning the RawDataFrame removing columns not important and removing duplicate name columns
                df_temp = ReformatingDataFrame(df_temp, Subject)                # Modifying the way the dataframe is presented. Changing Subject Grades and Missings columns to rows
                df_temp['Cycle'] = Cycle                                        # Adding a new column with the name of the cycle
                df_temp['Partial'] = Partial                                    # Adding a new column with the name of the Partial
                df_temp['Semester'] = Group.split(".")[0][0]                    # The group is in a format like 1A.xls, so, spliting by "." will return the following array:
                                                                                # Group[0] = '1A', Group[1] = 'xls'
                                                                                # So, thats why we focus just in the Group[0], where the fist char is the Semester ('1')
                df_temp['Group'] = Group.split(".")[0][1]                       # and the second char in Group[0] is the group ('A')
                df = pd.concat([df, df_temp], ignore_index = True)              # Then, we concatenate the current dataframe with the previous one
    if SaveToCsv:                                                               # if SaveToCsv is True
        df.to_csv(OutputFilename)                                               # We save the dataframe in the OutputFileName file
    return(df)                                                                  # Finally, we return the dataframe generated
    
if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    PathToFiles = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\FinalDataFrame.csv'
    JoinAllFiles(PathToFiles, OutputFilename, Verbose=True)