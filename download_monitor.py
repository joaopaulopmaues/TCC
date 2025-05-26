from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import re

download_dir = os.getenv("DOWNLOAD_DIR")

class DownloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.file_created = None
        self.temp_files = set()

    def is_temp_file(self, path):
        """Verifica se é um arquivo temporário do Chrome ou outros navegadores"""
        temp_patterns = [
            r'\.crdownload$', r'\.tmp$', r'\.part$', r'\.download$',
            r'\.com\.google\.Chrome\.[a-zA-Z0-9]+$',
            r'\.opera(?:-[a-zA-Z0-9]+)?$',
            r'\.msdownload$', r'\.partial$'
        ]
        return any(re.search(pattern, path) for pattern in temp_patterns)

    def on_created(self, event):
        if not event.is_directory:
            if self.is_temp_file(event.src_path):
                self.temp_files.add(event.src_path)
                print(f"Arquivo temporário detectado: {event.src_path}")
            elif not self.file_created:  # Ignora múltiplos arquivos não-temporários
                self.file_created = event.src_path
                print(f"Arquivo final detectado: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory and not self.is_temp_file(event.src_path):
            if not self.file_created:  # Só considera o primeiro arquivo válido
                self.file_created = event.src_path
                print(f"Download concluído: {event.src_path}")

def wait_for_download_completion(directory, temp_files, timeout=120):
    """Aguarda até que todos os arquivos temporários desapareçam"""
    print("Aguardando conclusão do download...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Verifica se algum arquivo temporário ainda existe
        remaining_temp_files = [f for f in temp_files if os.path.exists(f)]
        
        if not remaining_temp_files:
            print("Todos os arquivos temporários desapareceram - download concluído")
            return True
        
        time.sleep(2)
    
    print(f"Arquivos temporários remanescentes: {remaining_temp_files}")
    return False

def monitor_download(monitored_dir='', timeout=180, dst=''):
    """
    Versão melhorada que lida melhor com arquivos temporários do Chrome
    """
    download_dir=os.getenv("DOWNLOAD_DIR")
    if monitored_dir=='':
        directory=download_dir
    else:
        directory=monitored_dir
        
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    
    try:
        print(f"Monitorando pasta: {directory}")
        start_time = time.time()
        
        # Aguarda até detectar algum arquivo (temporário ou final)
        while not event_handler.file_created and len(event_handler.temp_files) == 0:
            if time.time() - start_time > timeout:
                print("Nenhuma atividade de download detectada.")
                return None
            time.sleep(1)
        
        # Se detectou arquivos temporários mas não o final, aguarda conclusão
        if not event_handler.file_created and event_handler.temp_files:
            print(f"Detectados {len(event_handler.temp_files)} arquivos temporários")
            if not wait_for_download_completion(directory, event_handler.temp_files, timeout):
                print("Download não concluído dentro do tempo limite")
                return None
            
            # Procura pelo arquivo final (não temporário) na pasta
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if not event_handler.is_temp_file(filepath) and os.path.isfile(filepath):
                    # Considera o arquivo mais recente como o download final
                    if (not event_handler.file_created or 
                        os.path.getmtime(filepath) > os.path.getmtime(event_handler.file_created)):
                        event_handler.file_created = filepath
            
            if not event_handler.file_created:
                print("Nenhum arquivo final encontrado após desaparecimento dos temporários")
                return None

        # Defines destiny folder, it is used usually for downloading malware samples
        # But in case of reports dst parameter is defined
        malware_folder = dst if dst else os.getenv("MALWARE_DST")
        dest_dir = os.path.join(download_dir, malware_folder)
        os.makedirs(dest_dir, exist_ok=True)

        # Move o arquivo
        dest_path = os.path.join(dest_dir, os.path.basename(event_handler.file_created))
        try:
            os.rename(event_handler.file_created, dest_path)
            print(f"Arquivo movido com sucesso para: {dest_path}")
            return dest_path
        except OSError as e:
            print(f"Erro ao mover arquivo: {e}")
            return event_handler.file_created

    finally:
        observer.stop()
        observer.join()