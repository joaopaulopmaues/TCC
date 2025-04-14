# Caminho para a pasta de Downloads
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class DownloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.file_created = None

    def on_created(self, event):
        if not event.is_directory:
            self.file_created = event.src_path
            print(f"Download detectado: {event.src_path}")

def monitor_download(directory, timeout=60):
    """
    Monitora a pasta de downloads e detecta a criação de arquivos.
    :param directory: Caminho da pasta de downloads.
    :param timeout: Tempo limite para aguardar o download.
    :return: Caminho do arquivo criado, se detectado; None caso contrário.
    """
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    start_time = time.time()
    try:
        while not event_handler.file_created:
            if time.time() - start_time > timeout:
                print("Tempo limite atingido. Nenhum download detectado.")
                break
            time.sleep(1)  # Reduzido para respostas mais rápidas
    finally:
        observer.stop()
        observer.join()

    return event_handler.file_created