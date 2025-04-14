from download_monitor import monitor_download
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#import time


def download_sample(hashin,browser):
    user=os.getenv("HA_USER")
    password=os.getenv("HA_PASS")
    download_dir=os.getenv("DOWNLOAD_DIR")
    wait = WebDriverWait(browser, timeout=20)
    browser.get('https://www.hybrid-analysis.com/login')
    #time.sleep(4)
    wait.until(EC.visibility_of_element_located(('xpath','/html/body/div[3]/div/form/div[1]/input'))).send_keys(user)
    wait.until(EC.visibility_of_element_located(('xpath','/html/body/div[3]/div/form/div[2]/div[1]/input'))).send_keys(password)
    wait.until(EC.visibility_of_element_located(('xpath','/html/body/div[3]/div/form/div[3]/button'))).click()
    #primeiro tentar encontrar a amostra. Se deu certo baixa, senão retorna "Not_Found"
    url='https://www.hybrid-analysis.com/download-sample/'+hashin
    try:
        browser.get(url)
    except:
        return 'HA_Error'
    
    if '404' in browser.title:
        return 'Not_Found'
    else:
        print("Aguardando o término do download...")
        downloaded_file = monitor_download(download_dir, timeout=120)
        if downloaded_file:
            print(f"Download concluído: {downloaded_file}")
            return hashin+'.sample'
        else:
            return "Download_not_detected"