# coding=utf-8
"""
Saturdays AI 
    - Team 2 
        - Predicting the school desertion

This script will be used to extract just the Names and Students Codes from the raw data
"""

import os
import pandas as pd
import numpy as np

def GettingNamesAndCodes(PathToFiles, OutputFilename, SaveToCsv = True, Verbose=False):
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
                df_temp.dropna(axis = 1, how = 'all', inplace = True)
                df_temp.columns = df_temp.iloc[0]
                df_temp.drop(df_temp.index[0], inplace = True)
                ColumnsToRemove = set(df_temp.columns) - set(['No. Control', 'Nombre'])
                df_temp.drop(ColumnsToRemove, axis=1, inplace=True)
                count = 0
                for i in range(df_temp.shape[0]):
                    if np.isnan(float(df_temp.iloc[i][0])):
                        count = i
                        break
                df2 = df_temp.iloc[0:count].copy()
                df2['Nombre'] = df2['Nombre'].apply(lambda x: str(x).replace('(R)', '').replace('(RP)', ''))
                df = pd.concat([df, df2], ignore_index = True)
    df.drop_duplicates(inplace = True)
    if SaveToCsv:                                                               # if SaveToCsv is True
        if Verbose: print("Saving the dataframe in: {}".format(OutputFilename))
        df.to_csv(OutputFilename, encoding='utf-8-sig')                                               # We save the dataframe in the OutputFileName file
    return(df)   
    
if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    PathToFiles = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets'
    OutputFilename = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\Raw_Datasets\NamesWithoutDuplicates.csv'
    GettingNamesAndCodes(PathToFiles, OutputFilename, Verbose=True)