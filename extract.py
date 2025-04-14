import json
from types import SimpleNamespace
import re
import os

def write_to_csv(lst, filename):
    # Define the headers
    api_call_headers = [f'ApiCall_{i}' for i in range(500)]
    dll_headers = [f'Dll_{i}' for i in range(10)]
    mutex_headers = [f'Mutex_{i}' for i in range(10)]
    headers = api_call_headers + dll_headers + mutex_headers
    
    # Check if file exists
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        # Write headers if file doesn't exist
        if not file_exists:
            f.write(';'.join(headers) + '\n')
        # Write the data row
        f.write(';'.join(map(str, lst)) + '\n')
        
def data_extraction(input_folder,output_csv):
    #input folder is where all the jsons are searched for data extraction by this function.
    for path in os.walk(input_folder):
        if not ('report.json' in path):
            continue
        with open(path, 'r', encoding='utf-8') as jsonfile: #path must be the iteratable variable for reading each "report.json" (already checked)
            report = json.load(jsonfile, object_hook = lambda d: SimpleNamespace(**d)) #in folders and subfolders
            # Initialize empty list
            lst = []
            
            # Extract API calls
            try:
                for process in report.behavior.processes:
                    for call in process.calls:
                        try:
                            lst.append(call.api)
                        except:
                            continue
            except:
                print("no api call")
            
            # Extract DLLs
            try:
                for pe_import in report.static.pe_imports:
                    cleaned_dll = ''.join(char for char in pe_import.dll if char != '.')
                    lst.append(cleaned_dll)
            except:
                print("no dll")
            
            # Extract mutexes
            try:
                for mutex in report.behavior.summary.mutex:
                    lst.append(mutex)
            except:
                print("no mutex")
            
            write_to_csv(lst,output_csv)
