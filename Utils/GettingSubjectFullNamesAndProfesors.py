# coding=utf-8
"""
Saturdays AI 
    - Team 2 
        - Predicting the school desertion

This script will be used to extract the fullname of the subjects and
Profesors names.
"""
import os
import pandas as pd

def _GettingSubjectsSubset(df):
    count = df.shape[0]
    for i in range(df.shape[0]-1, 0, -1):
        if df.iloc[i][0] == "":
            count = i
            break
    df = df.iloc[count+1:].copy()
    df = df.iloc[:,0:3]
    df.reset_index(inplace=True, drop = True)
    df.columns=['Abreviacion', 'Nombre Completo', 'Profesor']
    return(df)

def _FixingDuplicatedSubjectNames(df):
    NumRows = len(df.index)
    RowsNameCorrected = []
    Subject = []
    for i in range(NumRows):
        SubjectName = df.iloc[i,0]
        if SubjectName == 'TUT':
            df.drop([i], axis = 0, inplace = True)
            continue
        if SubjectName in Subject:
            counter = 0
            while (str(SubjectName) + str(counter)) in Subject:
                   counter += 1
            SubjectName = str(SubjectName) + str(counter)
        Subject.append(SubjectName)
        RowsNameCorrected.append(SubjectName)
    df.iloc[:,0] = RowsNameCorrected
    return(df)

def GettingProfesorsNames(PathToFiles, OutputFilename, SaveToCsv = True, Verbose=False):
    df = pd.DataFrame()                                                         # It create a new empty dataframe
    
    Cycles = os.listdir(PathToFiles)                                            # Read all the folders corresponding to the Cycle
    for Cycle in Cycles:                                                        # For each cycle folder
        if not os.path.isdir(os.path.join(PathToFiles, Cycle)):                 # if the file is not a directory continue with the following
            continue
        if Verbose: print("Cycle = {}".format(Cycle))                           # Printing the name of the Current Cycle folder
        Partial = '1'
        if not os.path.isdir(os.path.join(PathToFiles, Cycle, Partial)):    # if the file is not a directory continue with the following
            continue
        if Verbose: print("    Partial = {}".format(Partial))               # Print the name of the current Partial folder
        Groups = os.listdir(os.path.join(PathToFiles, Cycle, Partial))      # List all the files inside the Cycle/Partial Folder
        for Group in Groups:                                                # for each cycle/patial/group file
            if os.path.isdir(os.path.join(PathToFiles, Cycle, Partial, Group)):    # if the file is not a directory continue with the following
                continue
            if Verbose: print("        Group = {}".format(Group))           # Print the name of the current Group File
            file = os.path.join(PathToFiles, Cycle, Partial, Group)         # Getting the fullpath and filename to the file
            df_temp = pd.read_html(file, keep_default_na=False)
            df_temp = df_temp[1]
            
            df_temp = _GettingSubjectsSubset(df_temp)
            df_temp = _FixingDuplicatedSubjectNames(df_temp)
            
            df_temp['Cycle'] = Cycle                                        # Adding a new column with the name of the cycle
            df_temp['Semester'] = Group.split(".")[0][0]                    # The group is in a format like 1A.xls, so, spliting by "." will return the following array:
                                                                            # Group[0] = '1A', Group[1] = 'xls'
                                                                            # So, thats why we focus just in the Group[0], where the fist char is the Semester ('1')
            df_temp['Group'] = Group.split(".")[0][1]                       # and the second char in Group[0] is the group ('A')
            df = pd.concat([df, df_temp], ignore_index = True)              # Then, we concatenate the current dataframe with the previous one
    if SaveToCsv:                                                               # if SaveToCsv is True
        if Verbose: print("Saving the dataframe in: {}".format(OutputFilename))
        df.to_csv(OutputFilename)                                               # We save the dataframe in the OutputFileName file
    return(df)
                
if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    PathToFiles = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\ProfessorsAndSubjects.csv'
    GettingProfesorsNames(PathToFiles, OutputFilename, Verbose=True)