import os
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from download_monitor import monitor_download

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

def download_report(url, download_dir,reported=False,get_done=False,mybrowser=''):
    """
    Realiza o download de um relatório de análise e aguarda o término.
    :param url: URL inicial para acessar a análise.
    :param download_dir: Diretório de downloads onde o arquivo será salvo.
    """
    if type(mybrowser)==str:
        if reported==False:
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) #webdriver.Safari()
            wait = WebDriverWait(browser, timeout=20)
            browser.get(url)

            # Aguarda a exibição do relatório
            reported_element = wait.until(EC.presence_of_element_located((By.XPATH, '//tr[contains(.,"reported")]')))

            # Captura o ID da tarefa
            task_id = reported_element.get_attribute('data-task-id')
            browser.get(f'https://sandbox.pikker.ee/analysis/{task_id}/export')
        elif get_done==False:
            wait = WebDriverWait(browser, timeout=20)
            browser.get(url)
    else:
        browser=mybrowser
        wait = WebDriverWait(browser, timeout=20)
    # Maximiza a janela para visualizar todas as opções
    browser.maximize_window()

    # Ajusta os checkboxes
    checkbox_container = wait.until(EC.presence_of_element_located((
        By.XPATH, '/html/body/div[2]/div[2]/section/div/div/div/div/div/form/div/div/div[2]/div/div[1]/div'
    )))
    checkboxes = checkbox_container.find_elements(By.XPATH, './/input[@type="checkbox"]')
    for checkbox in checkboxes:
        checkbox_id = checkbox.get_attribute('id')
        if checkbox_id != "export_reports" and checkbox.is_selected():
            try:
                browser.execute_script("arguments[0].click();", checkbox)
            except Exception as e:
                print(f"Erro ao desmarcar checkbox {checkbox_id}: {e}")
                
    checkbox_container = wait.until(EC.presence_of_element_located((
        By.XPATH, '/html/body/div[2]/div[2]/section/div/div/div/div/div/form/div/div/div[2]/div/div[2]'
    )))
    checkboxes = checkbox_container.find_elements(By.XPATH, './/input[@type="checkbox"]')
    for checkbox in checkboxes:
        checkbox_id = checkbox.get_attribute('id')
        if checkbox_id != "export_reports" and checkbox.is_selected():
            browser.execute_script("arguments[0].click();", checkbox)

    # Clica no botão de exportar
    button_xpath = '/html/body/div[2]/div[2]/section/div/div/div/div/div/form/div/div/div[2]/div/div[3]/div[2]/button'
    export_button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    browser.execute_script("arguments[0].click();", export_button)

    # Monitora o download
    print("Aguardando o término do download...")
    downloaded_file = monitor_download(download_dir, timeout=120)

    if downloaded_file:
        print(f"Download concluído: {downloaded_file}")
    else:
        print("Download não foi detectado dentro do tempo limite.")

    # Fecha o navegador
    browser.close()
    browser.quit()

def send_file(filePath):
    #Inicialização do navegador
    browser = webdriver.Safari()
    wait = WebDriverWait(browser, timeout=20)

    # Acesse o site
    browser.get('https://sandbox.pikker.ee')

    # Envia o arquivo
    browser.find_element(By.XPATH, '//*[@id="file"]').send_keys(filePath)

    # Aguarda que o número "1" apareça no elemento que indica que o arquivo foi carregado
    wait.until(EC.text_to_be_present_in_element(
        (By.XPATH, '//*[@id="analysis-configuration"]/div/section/nav/ul[2]/li/p/a/span[1]'),
        '1'
    ))

    # Aguarda que o botão esteja visível e pronto para interação
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="start-analysis"]')))

    # Aguarda que o botão seja clicável
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="start-analysis"]')))

    # Clica no botão usando JavaScript para garantir a execução
    button = browser.find_element(By.XPATH, '//*[@id="start-analysis"]')
    browser.execute_script("arguments[0].click();", button)

    print(f'Análise submetida! Acompanhe o status em:{browser.current_url}')

    url=browser.current_url
    browser.close()
    browser.quit()
    # Mensagem de sucesso
    return url