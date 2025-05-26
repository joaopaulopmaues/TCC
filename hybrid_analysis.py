from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from download_monitor import monitor_download
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import time

class DownloadHandler_ha(FileSystemEventHandler):
    def __init__(self):
        self.file_created = None

    def on_created(self, event):
        if not event.is_directory:
            self.file_created = event.src_path
            print(f"Download detectado: {event.src_path}")

def monitor_start_download(directory, timeout=60):
    """
    Monitora a pasta de downloads e detecta a criação de arquivos.
    :param directory: Caminho da pasta de downloads.
    :param timeout: Tempo limite para aguardar o download.
    :return: Caminho do arquivo criado, se detectado; None caso contrário.
    """
    event_handler = DownloadHandler_ha()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    start_time = time.time()
    try:
        while not event_handler.file_created:
            if time.time() - start_time > timeout:
                print("Tempo limite atingido. Nenhum download detectado.")
                return False #break
            time.sleep(1)  # Reduzido para respostas mais rápidas
    finally:
        observer.stop()
        observer.join()

    return True #event_handler.file_created

def move_sample_files(hashin):
    # Get the download directory from environment variable
    download_dir = os.getenv("DOWNLOAD_DIR")
    
    # Construct the malware destination directory
    malwaredir = os.path.join(download_dir, os.getenv("MALWARE_DST"))
    
    # Ensure the malware directory exists, create if it doesn't
    os.makedirs(malwaredir, exist_ok=True)
    
    # Iterate over files in download_dir
    moved_files = []
    for filename in os.listdir(download_dir):
        if hashin in filename.lower():  # Case-insensitive check
            src_path = os.path.join(download_dir, filename)
            dst_path = os.path.join(malwaredir, filename)
            shutil.move(src_path, dst_path)
            fullpath=os.path.join(malwaredir,filename)
            return fullpath
    return "Download_not_detected"
    


def download_sample(hashin,browser,logged=False):
    wait = WebDriverWait(browser, timeout=20)
    download_dir=os.getenv("DOWNLOAD_DIR")
    if not logged:
        browser.get('https://www.hybrid-analysis.com/login')
        user=os.getenv("HA_USER")
        password=os.getenv("HA_PASS")
        print('Hybrid-analysis\nhashin:\t'+hashin+'.\tuser,password:\t'+str(len(user)+len(password))+'\n')
        #time.sleep(4)
        wait.until(EC.visibility_of_element_located(('xpath','/html/body/div[3]/div/form/div[1]/input'))).send_keys(user)
        wait.until(EC.visibility_of_element_located(('xpath','/html/body/div[3]/div/form/div[2]/div[1]/input'))).send_keys(password)
        wait.until(EC.visibility_of_element_located(('xpath','/html/body/div[3]/div/form/div[3]/button'))).click()
    #primeiro tentar encontrar a amostra. Se deu certo baixa, senão retorna "Not_Found"
    url='https://www.hybrid-analysis.com/download-sample/'+hashin
    print('url:\t'+url+'\n')
    patience=0
    download_started=False
    try:
        while not download_started and patience<3:
            browser.get(url)
            download_started=monitor_start_download(download_dir)
            patience+=1
            time.sleep(3)
        if not download_started:
            return 'Not_Found' #'HA_Error'
    except:
        return 'Not_Found' # 'HA_Error'
    
    if '404' in browser.title:
        return 'Not_Found'
    else:
        time.sleep(20)
        downloaded_file=move_sample_files(hashin)
        print(downloaded_file+'\n')
        return downloaded_file