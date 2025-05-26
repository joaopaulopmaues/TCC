import json
from types import SimpleNamespace
import re
import os
import pandas as pd

def match_the_words_and_make_them_equal(lst):
    result=[]
    wholeDataset=os.getenv("BASIS_DS")
    df_parameter=pd.read_csv(wholeDataset,sep=';',low_memory=False)
    aux=set()
    valid_dlls=set()
    valid_calls=set()
    valid_mutexes=set()
    for i in range(len(df_parameter.columns.to_list())):
        if i<500:
            valid_calls=valid_calls.union(set(df_parameter.iloc[:,i].unique().tolist()))
        elif i<510:
            valid_dlls=valid_dlls.union(set(df_parameter.iloc[:,i].unique().tolist()))
        else:
            valid_mutexes=valid_mutexes.union(set(df_parameter.iloc[:,i].unique().tolist()))
    for el in lst[:500]:
        for comp in valid_calls:
            if type(el)==str and el!='':
                if el.lower()==comp.lower():
                    result.append(comp)
                else:
                    result.append(el)
            else:
                result.append('')
                
    for el in lst[500:510]:
        for comp in valid_dlls:
            if type(el)==str and el!='':
                if el.lower()==comp.lower():
                    result.append(comp)
                else:
                    result.append(el)
            else:
                result.append('')
                
    for el in lst[510:]:
        for comp in valid_mutexes:
            if type(el)==str and el!='':
                if el.lower()==comp.lower():
                    result.append(comp)
                else:
                    result.append(el)
            else:
                result.append('')
    i=0
    result1=[0]*520
    for el in result:
        if len(el) == 1:
            result1[i]=''
        else:
            result1[i]=el
    result=result1
    return result

def write_to_csv(lst, filename):
    # Define the headers
    api_call_headers = [f'ApiCall_{i}' for i in range(500)]
    dll_headers = [f'Dll_{i}' for i in range(10)]
    mutex_headers = [f'Mutex_{i}' for i in range(10)]
    headers = api_call_headers + dll_headers + mutex_headers
    
    # Check if file exists
    file_exists = os.path.isfile(filename)
    if not file_exists:
        with open(filename, 'w+', newline='') as f:
            f.write(';'.join(headers) + '\n')
            f.write(';'.join(map(str, lst)) + '\n')
    else:
        with open(filename, 'a', newline='') as f:
            # Write the data row
            f.write(';'.join(map(str, lst)) + '\n')
        
def data_extraction(input,output_csv):
    with open(input, 'r', encoding='utf-8') as jsonfile: #path must be the iteratable variable for reading each "report.json" (already checked)
        report = json.load(jsonfile, object_hook = lambda d: SimpleNamespace(**d)) #in folders and subfolders
        # Initialize empty list
        lst = []
        api_count=0
        dll_mutex_count=0
            # Extract API calls
        try:
            for process in report.behavior.processes:
                for call in process.calls:
                    try:
                        word=call.api
                        word=re.sub('[^A-Za-z0-9]+','',word)
                        lst.append(word)
                        api_count+=1
                        if api_count==500:
                            break
                    except:
                        continue
                if api_count==500:
                    break
        except:
            #print("no api call")
            pass
            # Extract DLLs
        while len(lst)<500:
            lst.append('')
        try:
            for pe_import in report.static.pe_imports:
                word=pe_import.dll
                word=re.sub('[^A-Za-z0-9]+','',word)
                #cleaned_dll = ''.join(char for char in pe_import.dll if char != '.')
                lst.append(word)#cleaned_dll)
                if len(lst)==510:
                    break
        except:
            #print("no dll")
            pass
            # Extract mutexes
        while len(lst)<510:
            lst.append('')
        try:
            for mutex in report.behavior.summary.mutex:
                word=mutex
                word=re.sub('[^A-Za-z0-9]+','',word)
                lst.append(word)
                dll_mutex_count+=1
                if dll_mutex_count==10:
                    break
        except:
            #print("no mutex")
            pass
        #print(lst)
        while len(lst)<520:
            lst.append('')
        try:
            a=match_the_words_and_make_them_equal(lst)
            lst=a
        except:
            pass
        write_to_csv(lst,output_csv)
        return lst
