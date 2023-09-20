from typing import List
from fastapi import FastAPI, Query
import os
import pandas as pd
import json

app = FastAPI()

# Endpoint for getting files
@app.get("/getFiles")
def get_files():
    """
    Returns a list of files in the working directory
    ---
    Vrací seznam souborů v pracovním adresáři
    """
    working_directory = os.getcwd()
    files = os.listdir(working_directory)
    csv_files = [file for file in files if file.endswith('.csv')]
    xls_files = [file for file in files if file.endswith(('.xls', '.xlsx'))]
    all_files = csv_files + xls_files
    
    response = {
        "csv_files": csv_files,
        "xls_files": xls_files,
        "all_files": all_files  
    }
    
    return response

# Endpoint for getting sheets with a file name
@app.get("/getSheets/{file_name}")  
def get_sheets(file_name: str ):
    """
    Retrieves the names of all sheets in the specified Excel file.
    Načte názvy všech listů v daném Excel souboru.
    
    Args:
        file_name (str): Optional parameter specifying the name of the Excel file. If not provided, it will default to None.
                         | Volitelný parametr specifikující název Excel souboru. Pokud není poskytnut, bude výchozí hodnota None.

    Returns:
        has_sheets: A boolean value indicating whether the file has sheets. | Logická hodnota indikující, zda soubor má listy.  
        sheets: A list of sheet names in the Excel file. | Seznam názvů listů v Excel souboru.
    """
    if file_name is None:
        response = {
            "has_sheets": False,
            "sheets": "No file name provided"
        }
        return response
    
    working_directory = os.getcwd()
    file_path = os.path.join(working_directory, file_name)

    if not os.path.exists(file_path):
        response = {
            "has_sheets": False,
            "sheets": "File does not exist"
        }
        return response
    
    file_extension = os.path.splitext(file_name)[1]
    
    if file_extension == '.csv':
        response = {
            "has_sheets": False,
            "sheets": "CSV files do not have sheets"
        }
    else:
        ex = pd.ExcelFile(file_path)
        sheets = ex.sheet_names
        response = {
            "has_sheets": True,
            "sheets": sheets
        }
    
    return response       

# Endpoint for getting sheets without a file name
@app.get("/getSheets")  
def get_sheets():
    """
    Function for handling requests to the /getSheets endpoint without a file name.
    Funkce pro zpracování požadavků na koncový bod /getSheets bez názvu souboru.
    """
    response = {
        "has_sheets": False,
        "sheets": "No file name provided"
    }
    return response


# Endpoint for getting information and size of a file
@app.get("/getCSVInfo/{file_name}")
def get_file_info(file_name: str ):
    """
    Retrieves information about a CSV file.
    Načte informace o souboru ve formátu CSV.

    Args:
        file_name (str): Optional parameter specifying the name of the CSV file.
                         | Volitelný parametr specifikující název souboru ve formátu CSV.

    Returns:
        dict: Information about the CSV file.
              | Informace o souboru ve formátu CSV.
    """
    working_directory = os.getcwd()
    file_path = os.path.join(working_directory, file_name)

    if not os.path.exists(file_path):
        response = {
            "file_name": None,
            "message": "File does not exist"
        }
        return response
    
    file_extension = os.path.splitext(file_name)[1]
    if file_extension == '.csv':
        data = pd.read_csv(file_path)
        info = data.describe()
        response = {
            "file_name": file_name,
            "message": "File is a CSV",
            "info": info,
            "size_in_mb": os.path.getsize(file_path) / 1000000,
            "shape": data.shape
        }
    if file_extension == '.xls' or file_extension == '.xlsx':
        response = {
            "file_name": file_name,
            "message": "Please use getExcelInfo and specify a sheet name"
        }
            
    return response


@app.get("/getExcelInfo/{file_name}/{sheet_name}")
def get_file_info(file_name: str , sheet_name: str ):
    """
    Retrieves information about an Excel file.
    Načte informace o souboru ve formátu Excel.

    Args:
        file_name (str): Optional parameter specifying the name of the Excel file.
                         | Volitelný parametr specifikující název souboru ve formátu Excel.
        sheet_name (str): Optional parameter specifying the name of the sheet in the Excel file.
                          | Volitelný parametr specifikující název listu v souboru ve formátu Excel.

    Returns:
        dict: Information about the Excel file.
              | Informace o souboru ve formátu Excel.
    """
    working_directory = os.getcwd()
    file_path = os.path.join(working_directory, file_name)

    if not os.path.exists(file_path):
        response = {
            "file_name": None,
            "message": "File does not exist"
        }
        return response
    
    file_extension = os.path.splitext(file_name)[1]
    if file_extension == '.csv':
        response = {
            "file_name": file_name,
            "message": "Please use getCSVInfo"
        }           

    if file_extension == '.xls' or file_extension == '.xlsx':
        ex = pd.ExcelFile(file_path)
        if sheet_name not in ex.sheet_names:            
            response = {
                "file_name": file_name,
                "message": "Sheet does not exist"
            }
            return response 
        sheet_data = ex.parse(sheet_name)
        info = sheet_data.describe().to_json()
        response = {
            "file_name": file_name,
            "message": f"File is an Excel file, sheet {sheet_name}",
            "size_in_mb": os.path.getsize(file_path) / 1000000,
            "sheet": sheet_name,
            "shape": sheet_data.shape,
            "info": info
        }
    return response

@app.get("/getColumnInfo/{file_name}/{sheet_name}")
def get_column_info(file_name: str, sheet_name: str = None):
    """
    Retrieves column information divided by data types for a file (CSV, XLS, XLSX).

    Args:
        file_name (str): The name of the file.
        sheet_name (str, optional): The name of the sheet (only for XLS and XLSX files).

    Returns:
        dict: Column information divided by data types.
    """
    working_directory = os.getcwd()
    file_path = os.path.join(working_directory, file_name)

    if not os.path.exists(file_path):
        response = {
            "file_name": None,
            "message": "File does not exist"
        }
        return response
    
    file_extension = os.path.splitext(file_name)[1]
    if file_extension == '.csv':
        data = pd.read_csv(file_path)
    elif file_extension == '.xls' or file_extension == '.xlsx':
        ex = pd.ExcelFile(file_path)
        if sheet_name not in ex.sheet_names:
            response = {
                "file_name": file_name,
                "message": "Sheet does not exist"
            }
            return response 
        data = ex.parse(sheet_name)
    else:
        response = {
            "file_name": file_name,
            "message": "Unsupported file format"
        }
        return response 

    column_info = {
        "float_columns": list(data.select_dtypes(include=['float']).columns),
        "int_columns": list(data.select_dtypes(include=['int']).columns),
        "bool_columns": list(data.select_dtypes(include=['bool']).columns),
        "datetime_columns": list(data.select_dtypes(include=['datetime']).columns),
        "object_columns": list(data.select_dtypes(include=['object']).columns),
        "all_columns": list(data.columns)
    }
    
    response = {
        "file_name": file_name,
        "message": "Column information by data types",
        "column_info": column_info,
        "size_in_mb": os.path.getsize(file_path) / 1000000,
        "shape": data.shape
    }
    
    return response

@app.get("/getDataRange/{file_name}/{offset}/{num_lines}/{sheet_name}")
def get_column_info(file_name: str, offset: int = 0, num_lines: int = 5, sheet_name: str = None):
    """
    Retrieves a range of data from a file (CSV, XLS, XLSX) based on the specified offset and number of lines.

    Args:
        file_name (str): The name of the file.
        offset (int, optional): The starting offset of the data range.
        num_lines (int, optional): The number of lines to retrieve. If set to -1, lines are sellected from the bottom.
        sheet_name (str, optional): The name of the sheet (only for XLS and XLSX files).

    Returns:
        dict: Data range from the file.
    """
    working_directory = os.getcwd()
    file_path = os.path.join(working_directory, file_name)

    if not os.path.exists(file_path):
        response = {
            "file_name": None,
            "message": "File does not exist"
        }
        return response
    
    file_extension = os.path.splitext(file_name)[1]
    if file_extension == '.csv':
        data = pd.read_csv(file_path)
    elif file_extension == '.xls' or file_extension == '.xlsx':
        ex = pd.ExcelFile(file_path)
        if sheet_name not in ex.sheet_names:
            response = {
                "file_name": file_name,
                "message": "Sheet does not exist"
            }
            return response 
        data = ex.parse(sheet_name)
    else:
        response = {
            "file_name": file_name,
            "message": "Unsupported file format"
        }
        return response 

    if num_lines < 0:
        row_data = data.iloc[num_lines:].to_json(orient="records"),
    else:
        row_data = data.iloc[offset:offset + num_lines].to_json(orient="records"),

    
    response = {
        "file_name": file_name,
        "message": f"{num_lines} rows from {offset} offset",
        "data": row_data
    }
    
    return response

@app.get("/getColumnData/{file_name}/{sheet_name}")
def get_column_data(file_name: str, sheet_name: str, columns: List[int]  = Query(...)):
    """
    Retrieves data from specified columns of a file (CSV, XLS, XLSX).
    Example of calling the API: 'GET /getColumnData/example.xlsx/Sheet1?columns=0,2,7'

    Args:
        file_name (str): The name of the file.
        sheet_name (str): The name of the sheet.
        columns (List[int]): The list of column numbers.

    Returns:
        dict: Data from the specified columns.
    """
    working_directory = os.getcwd()
    file_path = os.path.join(working_directory, file_name)

    if not os.path.exists(file_path):
        response = {
            "file_name": None,
            "message": "File does not exist"
        }
        return response

    file_extension = os.path.splitext(file_name)[1]
    if file_extension == '.csv':
        data = pd.read_csv(file_path)
    elif file_extension == '.xls' or file_extension == '.xlsx':
        ex = pd.ExcelFile(file_path)
        if sheet_name not in ex.sheet_names:
            response = {
                "file_name": file_name,
                "message": "Sheet does not exist"
            }
            return response
        data = ex.parse(sheet_name)
    else:
        response = {
            "file_name": file_name,
            "message": "Unsupported file format"
        }
        return response

    selected_columns = data.iloc[:, columns]
    column_data = selected_columns.to_json(orient='records')

    response = {
        "file_name": file_name,
        "sheet_name": sheet_name,
        "data": column_data
    }

    return response
