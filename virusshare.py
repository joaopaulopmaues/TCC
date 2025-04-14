from download_monitor import monitor_download
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

user=os.getenv("VS_USER")
password=os.getenv("VS_PASS")
download_dir=os.getenv("DOWNLOAD_DIR")

def download_sample(hashin,browser):
    wait = WebDriverWait(browser, timeout=20)
    browser.get('https://virusshare.com/login')
    browser.find_element('xpath','/html/body/center[2]/form/table/tbody/tr[1]/td[2]/input').send_keys(user)
    browser.find_element('xpath','/html/body/center[2]/form/table/tbody/tr[2]/td[2]/input').send_keys(password)
    wait.until(EC.presence_of_element_located(
        ('xpath','/html/body/center[2]/form/table/tbody/tr[4]/td/input')))
    browser.find_element('xpath','/html/body/center[2]/form/table/tbody/tr[4]/td/input').click()
    wait.until(EC.invisibility_of_element_located(('xpath','/html/body/center[2]/form/table/tbody/tr[4]/td/input')))
    
    browser.get('https://virusshare.com/file?'+hashin)
    try:
        A=browser.find_element('xpath','/html/body/center[2]')
        if A.text=='No results.':
            return 'Not_Found'
    except:
        try:
            browser.get('https://virusshare.com/download?'+hashin)
            # Monitora o download
            print("Aguardando o término do download...")
            downloaded_file = monitor_download(download_dir, timeout=120)
            if downloaded_file:
                print(f"Download concluído: {downloaded_file}")
                return 'VirusShare_'+hashin+'.zip'
            else:
                print("Download não foi detectado dentro do tempo limite.")
        except:
            return 'Connection error'
            pass
        pass
    return 'VS_Error'
    
    