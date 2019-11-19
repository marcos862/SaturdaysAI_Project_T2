import os
import time
import pandas as pd
import numpy as np
#pd.set_option('display.max_columns', 999)

def _ChangingToNumericColumns(df):
    df['Ab']     = df['Abandono'].apply(lambda x: 0 if x == 'No' else 1)
    df['Repite'] = df['Repite Materia'].apply(lambda x: 0 if x == 'No' else 1)
    df['Hombre'] = df['Sexo'].apply(lambda x: 1 if x == 'M' else 0)
    df['Mujer']  = df['Sexo'].apply(lambda x: 1 if x == 'F' else 0)
    
    df.drop(['Abandono', 'Sexo', 'Repite Materia'], axis = 1, inplace = True)
    return(df)

def PreProcessingData(PathToDataSet, OutputFilename, NormStd = None, SaveToCsv = True, Verbose=False):
    df = pd.read_csv(PathToDataSet)
    df.drop(['Unnamed: 0'], axis = 1, inplace = True)
    
    Students = df['Id Unico'].drop_duplicates().reset_index(drop = True)
    
    if Verbose: 
        print("Total Number of Students: {}\n".format(len(Students)))
        start_time = time.time()

    columns_for_df = ['Id Unico', 'Sexo', 'Semestre', 'Promedio_General', 'Materias Aprobadas Historicas', 'Materias No Aprobadas Historicas', 'Numero de Faltas Semestre En Curso', 'Repite Materia', 'Abandono']
    df_final = pd.DataFrame(columns = columns_for_df)

    for r in range(len(Students)):
        df_student = df[df['Id Unico'] == Students[r]]
        if Verbose: print("PreProcessing Data for Student: {}".format(Students[r]))
        Ult_Ciclo = df_student['Ultimo Ciclo'].drop_duplicates().values[0]
        Semester = df_student[df_student['Cycle'] == Ult_Ciclo]['Semester'].max()
        Gender = df_student['Genero'].drop_duplicates().values[0]
        
        df_Grades = df_student[df_student['Calificacion'] != -1]
        Avg_Grade = df_Grades['Calificacion'].mean()
        Approves = df_Grades[df_Grades['Calificacion'] > 5]['Calificacion'].count()
        NotApproves = df_Grades[df_Grades['Calificacion'] <= 5]['Calificacion'].count()
        
        Missings = df_student[(df_student['Cycle'] == Ult_Ciclo) & (df_student['Faltas'] != -1)]['Faltas'].sum()
        ReCoursing = df_student[(df_student['Cycle'] == Ult_Ciclo)]['Repetidor'].drop_duplicates().values[0]
        Dropped = df_student['Abandono'].drop_duplicates().values[0]
        df_temp = pd.DataFrame([[Students[r], Gender, Semester, Avg_Grade, Approves, NotApproves, Missings, ReCoursing, Dropped]], columns = columns_for_df)
        df_final = df_final.append(df_temp, ignore_index=True)

    if Verbose: 
        print("\nThe dataframe created have:\nCols: {}\nRows: {}\n".format(df_final.shape[1], df_final.shape[0]))
        final_time = time.time()
        print("Time Elapsed to PreProcess Data: {}\n".format(final_time - start_time))
        
    if SaveToCsv:                                                               # if SaveToCsv is True
        OutputFileName = os.path.join(OutputPath, "New_DataSet_OneStudentByRow.csv")
        if Verbose: print("Saving the dataframe with NonNumeric Columns in: {}\n".format(OutputFileName))
        df_final.to_csv(OutputFilename, encoding='utf-8-sig')                                               # We save the dataframe in the OutputFileName file
    
    df_final = _ChangingToNumericColumns(df_final)
    if SaveToCsv:                                                               # if SaveToCsv is True
        OutputFileName = os.path.join(OutputPath, "New_DataSet_OneStudentByRow_Numeric.csv")
        if Verbose: print("Saving the dataframe with Numeric Columns in: {}\n".format(OutputFileName))
        df_final.to_csv(OutputFilename, encoding='utf-8-sig') 
        
    if NormStd == None:
        return(df_final)
    
    df_final.index = df_final['Id Unico']
    df_final.drop(['Id Unico'], axis = 1, inplace = True)
    if NormStd == "Norm":
        df_final_norm = (df_final - df_final.mean()) / (df_final.max() - df_final.min())
        if SaveToCsv:                                                               # if SaveToCsv is True
            OutputFileName = os.path.join(OutputPath, "New_DataSet_OneStudentByRow_norm.csv")
            if Verbose: print("Saving the dataframe Normalized in: {}\n".format(OutputFileName))
            df_final.to_csv(OutputFilename, encoding='utf-8-sig') 
        return(df_final_norm)
    elif NormStd == "Std":
        df_final_std = (df_final - df_final.mean()) / df_final.std()
        if SaveToCsv:                                                               # if SaveToCsv is True
            OutputFileName = os.path.join(OutputPath, "New_DataSet_OneStudentByRow_std.csv")
            if Verbose: print("Saving the dataframe Standarized in: {}\n".format(OutputFileName))
            df_final.to_csv(OutputFilename, encoding='utf-8-sig') 
        return(df_final_std)



if __name__ == "__main__":                                                      # This main is just to setup some variables before running the script if we 
                                                                                # run it with "double click" or with python <script name>.py from cmd
    PathToDataSet = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\DataSets_Created\FullDataSet_with_labels.csv'
    OutputPath = r'C:\SaturdaysAI\SaturdaysAI_Project_T2\DataSets_Created\New_DataSet_OneStudentByRow.csv'
    PreProcessingData(PathToDataSet, OutputPath, NormStd = "Std", Verbose=True)