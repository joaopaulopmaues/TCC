from downloader import search_n_download_file
from downloader import update_csv
from cuckoo_sandbox import send_file
from cuckoo_sandbox import download_report
from extract import data_extraction
import os
import csv
import zipfile
import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

#write_to_csv(lst,filename)

def download_submit_delete(hashin,browser,logged=False):
    status=search_n_download_file(hashin,browser,logged=logged)#downloads ransomware and updates hasheslist.csv
    malwsample_dir=os.getenv("MALWARE_DST")
    if not (hashin in status) and not(malwsample_dir in status): # No malware with that hash was found or
        return status #analysis report already downloaded
    else: #status is the file path
        url=send_file(status,mybrowser=browser)
        if url!='Submission_Error':
            update_csv(hashin,url)
        else:
            testc=0
            while testc<6 and url=='Submission_Error':
                url=send_file(status)
                testc+=1
            if url!='Submission_Error':
                update_csv(hashin,url)
            else:
                update_csv(hashin,'Not_Found')
        os.remove(status)
        return url

#check the third column. if the value of the second column is in the third, submit for cuckoo and substitute the value of the third column by the value returned by send_file (url to know the status)

def submission_scanner(filePath='hasheslist.csv',browser=''):
    '''
    scans hasheslist.csv for rows that
    has pending report already submitted to analysis
    
    for example: https://sandbox.pikker.ee/submit/post/5268905.
    '''
    rows = []
    
    # Read the file
    with open(filePath, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)  # Load all rows
    
    for row in rows:
        if len(row)>2:
            if 'submit/post' in row[2]:
                report_path=download_report(row[2],mybrowser=browser)
                update_csv(row[1],report_path)
            elif '/export/' in row[2]:
                report_path=download_report(row[2],reported=True,mybrowser=browser)
                update_csv(row[1],report_path)
            
                

def unzip(filepath, dst=''):
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        if dst == '':
            dstfolder = filepath[:-4]  # Remove '.zip' extension
        else:
            dstfolder = dst
            
        if not os.path.exists(dstfolder):
            os.makedirs(dstfolder)  # Using makedirs instead of mkdir for safety
            
        # Extract all files from the zip
        zip_ref.extractall(dstfolder)
        
    return dstfolder

def update_dataset(mybrowser='',skip_Not_Found=False,nsamples=None,newDatasetPath='/Users/joaopaulopmaues/Downloads/tensorflow-test/TCC/XRan - cópia/newDataset.csv',logged=False): #nsamples is for Proof of Concept
    #this way it only searches for a few samples
    '''
    It calls hash_enumerator, download_submit_delete, submission_scanner
    and extract from the zips the json and its features for inputting the model
    '''
    if type(mybrowser)!=str:
        browser=mybrowser
        wait = WebDriverWait(browser, timeout=20)
    else:
        # Caminho para a pasta de Downloads
        download_folder = os.path.expanduser('/Users/joaopaulopmaues/Downloads/')

        # Configurações do Chrome para downloads automáticos
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', {
            "download.default_directory": download_folder,  # Define a pasta de downloads
            "download.prompt_for_download": False,          # Não mostrar prompt para download
            "download.directory_upgrade": True,             # Atualiza automaticamente o diretório
            "safebrowsing.enabled": True                    # Habilita downloads seguros
        })
        chrome_options.add_argument("--start-maximized")  # Maximiza o navegador
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) #webdriver.Safari()
        wait = WebDriverWait(browser, timeout=20)

    hasheslist='./hasheslist.csv'
    
    #call hash_enumerator for enumerating hashes of files of each family
    
    with open(hasheslist,'r') as f:
        hashes=list(csv.reader(f))
    report_dir=os.getenv("REPORT_DST")
    malwsample_dir=os.getenv("MALWARE_DST")
    for line in hashes[:nsamples]:
        if (skip_Not_Found and len(line)>1 and line[-1]=='Not_Found'):
            continue
        if (len(line)==2 and line[-1]!='Not_Found') or (len(line)==3 and not ('Already_Inserted' in line[-1])):
            if ('/export/' in line[-1] or 'submit/post' in line[-1] or report_dir in line[-1]):
                continue
            status=download_submit_delete(line[1],browser,logged=logged)
            if '.zip' in status and not malwsample_dir in status: #report downloaded
                zipfile=status
                folder=unzip(zipfile)
                behav=data_extraction(folder+'/reports/report.json',newDatasetPath)
                behav=';'.join(map(str, behav))
                os.remove(zipfile)
                update_csv(line[1],"Already_Inserted"+behav)
            elif 'submit' in status or status=='Submission_Error' or status=='Not_Found' or malwsample_dir in status:
                continue
            else:
                print("Aborted. File hash when interruption happened: "+line[1]+". Reason: "+status+".\n")
                return "Failed"
    sandbox_doesnt_finish_analysis=True
    waited_once=False
    while sandbox_doesnt_finish_analysis:
        time.sleep(600)
        try:
            submission_scanner(browser=browser)
            sandbox_doesnt_finish_analysis=False
        except:
            if not waited_once:
                sandbox_doesnt_finish_analysis=True
            else:
                sandbox_doesnt_finish_analysis=False
    with open(hasheslist,'r') as f:
        hashes=list(csv.reader(f))
    for line in hashes:
        if (len(line)==3) and ('.zip' in line[2]):
            zipfile=line[2]
            folder=unzip(zipfile)
            behav=data_extraction(folder+'/reports/report.json',newDatasetPath)
            behav=';'.join(map(str, behav))
            os.remove(zipfile)
            update_csv(line[1],"Already_Inserted"+behav)
    return