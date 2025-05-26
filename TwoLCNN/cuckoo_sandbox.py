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

def download_report(url, download_dir='', report_dst='',reported=False,get_done=False,mybrowser='',timeout=180):
    """
    Realiza o download de um relatório de análise e aguarda o término.
    :param url: URL inicial para acessar a análise.
    :param download_dir: Diretório de downloads onde o arquivo será salvo.
    """
    if type(mybrowser)==str:
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) #webdriver.Safari()
        wait = WebDriverWait(browser, timeout=60)
        
        if get_done==False:
            browser.get(url)
            
        if reported==False:
            # Aguarda a exibição do relatório
            reported_element = wait.until(EC.presence_of_element_located((By.XPATH, '//tr[contains(.,"reported")]')))

            # Captura o ID da tarefa
            task_id = reported_element.get_attribute('data-task-id')
            browser.get(f'https://sandbox.pikker.ee/analysis/{task_id}/export')
    else:
        browser=mybrowser
        wait = WebDriverWait(browser, timeout=60)
        if get_done==False:
            browser.get(url)
        if reported==False:
            # Aguarda a exibição do relatório
            reported_element = wait.until(EC.presence_of_element_located((By.XPATH, '//tr[contains(.,"reported")]')))

            # Captura o ID da tarefa
            task_id = reported_element.get_attribute('data-task-id')
            browser.get(f'https://sandbox.pikker.ee/analysis/{task_id}/export')

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
    browser.execute_script("arguments[0].scrollIntoView(true);", export_button)
    browser.execute_script("arguments[0].click();", export_button)

    if report_dst=='':
        dst=os.getenv("REPORT_DST")
    else:
        dst=report_dst

    # Monitora o download
    print("Aguardando o término do download...")
    downloaded_file = monitor_download(download_dir,timeout,dst)

    if downloaded_file:
        print(f"Download concluído: {downloaded_file}")
        return downloaded_file
    else:
        print("Download não foi detectado dentro do tempo limite.")

    # Fecha o navegador
    browser.close()
    browser.quit()

def send_file(filePath,mybrowser=''):
    #Inicialização do navegador
    if type(mybrowser)!=str:
        driver=mybrowser
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, timeout=60)
    # Acesse o site
    driver.get('https://sandbox.pikker.ee')

    # Envia o arquivo
    driver.find_element(By.XPATH, '//*[@id="file"]').send_keys(filePath)

    # Aguarda que o número "1" apareça no elemento que indica que o arquivo foi carregado
    try:
        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, '//*[@id="analysis-configuration"]/div/section/nav/ul[2]/li/p/a/span[1]'),
            '1'
        ))
    except:
        pass

    # Aguarda que o botão esteja visível e pronto para interação
    #wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="start-analysis"]')))
    try:
    # Aguarda que o botão seja clicável
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="start-analysis"]')))
        start_button=wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="start-analysis"]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", start_button)
    except:
        return 'Submission_Error'

    # Clica no botão usando JavaScript para garantir a execução
    button = driver.find_element(By.XPATH, '//*[@id="start-analysis"]')
    url=''
    try:
        url=driver.current_url
    except:
        pass
    driver.execute_script("arguments[0].click();", button)
    time.sleep(2)
    
    try:
        url=driver.current_url
    except:
        pass
    
    print(f'Análise submetida! Acompanhe o status em:{url}')

    if not ('post' in url):
        if type(mybrowser)==str:
            driver.close()
            driver.quit()
        return 'Submission_Error'
    else:
        if type(mybrowser)==str:
            driver.close()
            driver.quit()
        # Mensagem de sucesso
        return url

def send_file1(filePath,mybrowser=''):
    #Inicialização do navegador
    if type(mybrowser)!=str:
        browser=mybrowser
    else:
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(browser, timeout=60)
    # Acesse o site
    browser.get('https://sandbox.pikker.ee')

    # Envia o arquivo
    browser.find_element(By.XPATH, '//*[@id="file"]').send_keys(filePath)

    # Aguarda que o número "1" apareça no elemento que indica que o arquivo foi carregado
    try:
        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, '//*[@id="analysis-configuration"]/div/section/nav/ul[2]/li/p/a/span[1]'),
            '1'
        ))
    except:
        pass

    # Aguarda que o botão esteja visível e pronto para interação
    #wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="start-analysis"]')))
    try:
    # Aguarda que o botão seja clicável
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="start-analysis"]')))
        start_button=wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="start-analysis"]')))
        browser.execute_script("arguments[0].scrollIntoView(true);", start_button)
    except:
        return 'Submission_Error'

    # Clica no botão usando JavaScript para garantir a execução
    button = browser.find_element(By.XPATH, '//*[@id="start-analysis"]')
    browser.execute_script("arguments[0].click();", button)
    time.sleep(2)

    print(f'Análise submetida! Acompanhe o status em:{browser.current_url}')

    url=browser.current_url
    if type(mybrowser)==str:
        browser.close()
        browser.quit()
    # Mensagem de sucesso
    return url

def send_file_alternate(filePath, mybrowser=''):
    # Initialize browser
    if not isinstance(mybrowser, str):
        browser = mybrowser
    else:
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Set longer timeout (60 seconds)
    wait = WebDriverWait(browser, timeout=60)
    
    try:
        print("Accessing sandbox website...")
        browser.get('https://sandbox.pikker.ee')
        
        # Wait for file input to be present first
        file_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="file"]'))
        )
        print("Found file input element")
        
        print(f"Uploading file: {filePath}")
        file_input.send_keys(filePath)
        
        # Wait for any upload progress indicator (alternative approach)
        print("Waiting for upload to complete...")
        
        # Try multiple ways to detect successful upload
        try:
            # Option 1: Wait for the "1" to appear
            wait.until(EC.text_to_be_present_in_element(
                (By.XPATH, '//*[@id="analysis-configuration"]/div/section/nav/ul[2]/li/p/a/span[1]'),
                '1'
            ))
        except:
            # Option 2: Wait for the start analysis button to become active
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="start-analysis"]')))
            print("Detected upload completion via button activation")
        
        print("Upload complete, starting analysis...")
        
        # More reliable button click
        start_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="start-analysis"]'))
        )
        
        # Scroll into view and click using JavaScript
        browser.execute_script("arguments[0].scrollIntoView(true);", start_button)
        browser.execute_script("arguments[0].click();", start_button)
        
        # Wait briefly to ensure click is processed
        time.sleep(2)
        
        print(f'Analysis submitted! Track status at: {browser.current_url}')
        url = browser.current_url
        
        return url
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Take screenshot for debugging
        browser.save_screenshot('upload_error.png')
        print("Saved screenshot as 'upload_error.png'")
        raise
        
    finally:
        if isinstance(mybrowser, str):  # Only quit if we created the browser
            browser.close()
            browser.quit()