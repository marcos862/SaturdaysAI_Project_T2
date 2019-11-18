# coding=utf-8
"""
Saturdays AI 
    - Team 2 
        - Predicting the school desertion

This script will be used to make anonymous the Raw Data
"""
import os
import pandas as pd

def _GetSpecialtyAndShift(df):
    Specialty = df.iloc[2,1].replace("REPORTE DE EVALUACIÓN PARCIAL DE ", "").replace(" PRIMER PARCIAL", "").replace(" SEGUNDO PARCIAL", "").replace(" TERCER PARCIAL", "")
    if df.iloc[3,1].find('MATUTINO'):
        Shift = 'MATUTINO'
    else:
        print(df.iloc[3,1])
        raise
    return Specialty, Shift

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
    ColumnsNameCorrected = []                                       # Starting an empty list for the columns with the names corrected
    Subject = []                                                    # Starting an empty list for the subjects/topics that are being found
    NumColumns = len(df.columns)                                    # Getting the number of columns to use it in the for
    for i in range(NumColumns):                                     # for each column
        if df.columns[i] == 'Faltas':                               # if the column is called "Faltas"
            SubjectName = df.columns[i-1]                           # The previous column is the name of the subject
            if SubjectName in Subject:                              # If this Subject Name is duplicated...
                counter = 0                                         # We initialize a counter to 0, to replace the name of the column adding a number
                while (str(SubjectName) + str(counter)) in Subject: # While the SubjectName + Counter is in the Subject List...
                       counter += 1                                 # we will be increasing the counter
                SubjectName = str(SubjectName) + str(counter)       # So, the new name will be the SubjectName + the value of the counter    
            Subject.append(SubjectName)                             # And, we add the name of the subject to the Subject List
            ColumnsNameCorrected.pop()                              # The previous added was the Name of theSubject, discarding it
            ColumnsNameCorrected.append(SubjectName)                # Adding the corrected name to the list with the right columns names
            ColumnsNameCorrected.append('Faltas_' + str(SubjectName))# Adding also, the new name to the column "Faltas", we are adding the subject name
        else:                                                       # If the column name is not "Faltas"
            ColumnsNameCorrected.append(str(df.columns[i]))         # We added to the list with the right Columns Name
    df.columns = ColumnsNameCorrected                               # Replacing the columns name of the dataframe with the ColumnsNameCorrected list
    return(df)

def _CleaningRawDataFrame(df):
    """
        This function will be removing all the columns and
        rows not required.
        
        Also, it's calling a function to remove the issue with the
        columns names duplications.
    """
    df.columns = df.iloc[0]                                                     # Taking the first row as the name of the columns
    df.drop(df.index[0], inplace = True)                                        # Removing the first row that we just convert to the columns names
    columnsToRemove = ['No. Cons', 'PROMEDIO', 'MATERIAS REP', '% REPROBACIÓN', '% APROBACIÓN', '']
    df.drop(columnsToRemove, axis=1, inplace=True)                              # Removing columns that are not useful (the axis=1 indicate columns, default is rows [axis = 0])

    # The dataframe, as it is, at the end, contain the full name of the subjects
    # As this information is not useful, at the moment, we want to remove that part of the dataframe
    # we identify this part of the dataframe because there is an empty row between the data from alumnis
    # and the real name of the subjects
    RowNumber = 0                                                               # Starting a counter for the row number
    for i in range(df.shape[0]):                                                # For each row in the dataframe
        if df.iloc[i][0] == '':                                                 # Checking if the No Control column in the current row is a 'NaN'
            RowNumber = i                                                       # If that is the case, we reached the end of the data we care
            break                                                               # we break the for.
    # https://www.dataquest.io/blog/settingwithcopywarning/
    df = df.iloc[0:RowNumber].copy()
    df = _CorrectingColumnNames(df)                                    # Renaming the columns that have the same name
    return df 

def Anonymizer(PathToFiles, PathToUniqueIds, Verbose=False):
    df_uid = pd.read_csv(r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\UniqueIdentifiers.csv')
    df_uid.drop(['Unnamed: 0'], inplace = True, axis = 1)

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
                df = pd.read_html(file, keep_default_na=False)
                
                Specialty, Shift = _GetSpecialtyAndShift(df[0])
                
                df_students = df[1].copy()
                df_students = _CleaningRawDataFrame(df_students)        # Cleaning the RawDataFrame removing columns not important and removing duplicate name columns
                df_students['Especialidad'] = Specialty
                df_students['Turno'] = Shift
                
                df_students['No. Control'] = df_students['No. Control'].astype('int64')
                df_student_uuid = df_students.merge(df_uid, how = 'left', on = 'No. Control')
                df_student_uuid['Repetidor'] = df_student_uuid['Nombre'].apply(lambda x: 'Si' if '(R)' in x else 'No')  # Creating a new column to show if the alumni is coursing again the class/semester
                cols_at_start = ['Id Unico', 'Genero', 'Repetidor', 'Especialidad', 'Turno']
                df_student_uuid = df_student_uuid[cols_at_start + [c for c in df_student_uuid if c not in cols_at_start]]
                
                df_student_uuid.index = df_student_uuid['Id Unico']
                df_student_uuid.drop(['No. Control', 'Nombre', 'Id Unico'], inplace = True, axis = 1)
                OutputFile = os.path.join(PathToFiles + "_Anonymous", Cycle, Partial, Group.split(".")[0] + ".csv")
                df_student_uuid.to_csv(OutputFile)




if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    PathToFiles = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets'
    PathToUniqueIds = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\UniqueIdentifiers.csv'
    Anonymizer(PathToFiles, PathToUniqueIds, Verbose=True)