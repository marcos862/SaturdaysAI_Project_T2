# coding=utf-8
"""
Saturdays AI 
    - Team 2 
        - Predicting the school desertion

This script will be used to join all the data from the datasets.
"""
import os
import pandas as pd

def _CleaningRawDataFrame(df):
    """
        This function will be removing all the columns and
        rows not required.
        
        Also, it's calling a function to remove the issue with the
        columns names duplications.
    """
    if 'TUT' in df.columns:                                                        # If we have a column with the grades from 'TUT' subject
        df.drop(['TUT', 'Faltas_TUT'], axis=1, inplace=True)                   # Removing the 'TUT' and 'Faltas_TUT' as this columns doesnt have useful information

    Subject = set(df.columns) - set(['Id Unico', 'Genero', 'Repetidor', 'Especialidad', 'Turno'])
    #Missings = ["Faltas_" + str(c) for c in Subject]
    Subject = [s for s in Subject if "Faltas_" not in s]
    # There are some subjects that doesnt have a numeric grade, so, we need to
    # change the non numeric grade to numeric grade, we are doing that as follows:
    #   'NP' = 0    # NP means 'No presento' (Exam not taken)
    #   'AC' = 7    # AC means 'Acreditado'  (Exam was passed)
    #   'NA' = 5    # NA means 'No Acreditado' (Exam was not passed)
    for s in Subject:                                                           # Checking all the Subjects in the list
        df[s] = df[s].apply(lambda x: 0 if x=='NP' else 7 if x == 'AC' else 5 if x == 'NA' else -1 if x == '' else x) # Changing all the non-numeric grades to numeric grades
        df['Faltas_' + s] = df['Faltas_' + s].apply(lambda x: -1 if x=='' else x) # Changing all the '' missings to zero
        df[s] = df[s].astype(int)
        df['Faltas_' + s] = df['Faltas_' + s].astype(int)
    # Finally, we know that, if an alumni has the string '(R)' in his/her name
    # that means that she/he is coursing again a class or the semester
    return df, Subject

def ReformatingDataFrame(df, Subject):
    """
        Reformating the database, changing columns to rows to
        be able to join, easily, all the database that are splitted
        by period, group and partial.
    """
    Missings = ["Faltas_" + str(c) for c in Subject]                    # Creating a list with the name of columns that include "Faltas_"
    ColsToStack = Subject + Missings                                    # The columns that will be "stacked" are the Subject and the "Missings"
    id_vars = set(df.columns) - set(ColsToStack)                        # The rest of columns will be used as indexes
    df_stack = pd.melt(df, id_vars=id_vars, value_vars=ColsToStack)     # To stack the table, we use the function "melt"
    # https://towardsdatascience.com/apply-and-lambda-usage-in-pandas-b13a1ea037f7
    df_stack['Tipo'] = df_stack['variable'].apply(lambda x: 'Faltas' if 'Faltas_' in x else 'Calificacion') # Adding a column that will tell us if the row data is a Grade or Missings
    df_stack['Materia'] = df_stack['variable'].apply(lambda x: x.replace("Faltas_", "")) # Adding another column with the name of the subject, for that, we use the "Faltas_"
    df_stack.drop('variable', axis = 1, inplace=True)                   # Removing the column 'variable' because is not needed anymore
    groupCols = list(set(df_stack.columns) - set(['Tipo', 'value']))    # Getting a list of columns that will be used to group the data    
    #https://medium.com/@enricobergamini/creating-non-numeric-pivot-tables-with-python-pandas-7aa9dfd788a7
    df_unstack = pd.pivot_table(df_stack, index=groupCols, columns=['Tipo'], values=['value'], aggfunc=lambda x: ' '.join(str(v) for v in x)) # Doing a Pivot table (unstacking) the data. Converting Rows in columns
    df_unstack.reset_index(inplace = True, col_level=1)                 # Converting the 'multindex' (rows) in columns
    df_unstack.columns = df_unstack.columns.droplevel()                 # Removing one level of the columns multindex
    return(df_unstack)                                                  # Returning the dataframe modified
    
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
                df_temp = pd.read_csv(file, keep_default_na=False)             # Reading the files as HTML, it will produce a list of dataframes
                df_temp, Subject = _CleaningRawDataFrame(df_temp)                # Cleaning the RawDataFrame removing columns not important and removing duplicate name columns
                df_temp = ReformatingDataFrame(df_temp, Subject)                # Modifying the way the dataframe is presented. Changing Subject Grades and Missings columns to rows
                df_temp['Cycle'] = Cycle                                        # Adding a new column with the name of the cycle
                df_temp['Partial'] = Partial                                    # Adding a new column with the name of the Partial
                df_temp['Semester'] = Group.split(".")[0][0]                    # The group is in a format like 1A.xls, so, spliting by "." will return the following array:
                                                                                # Group[0] = '1A', Group[1] = 'xls'
                                                                                # So, thats why we focus just in the Group[0], where the fist char is the Semester ('1')
                df_temp['Group'] = Group.split(".")[0][1]                       # and the second char in Group[0] is the group ('A')
                df = pd.concat([df, df_temp], ignore_index = True)              # Then, we concatenate the current dataframe with the previous one
    if SaveToCsv:                                                               # if SaveToCsv is True
        if Verbose: print("Saving the dataframe in: {}".format(OutputFilename))
        df.to_csv(OutputFilename, encoding='utf-8-sig')                                               # We save the dataframe in the OutputFileName file
    return(df)                                                                  # Finally, we return the dataframe generated
    
if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    PathToFiles = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets_Anonymous'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\DataSets_Created\FullDataSet.csv'
    JoinAllFiles(PathToFiles, OutputFilename, Verbose=True)