import pyperclip
import os
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from cuckoo_sandbox import download_report

#create proxy and greater wait time

def search(hashin,browser):#search hash
    wait = WebDriverWait(browser, timeout=10)
    pyperclip.copy(hashin)
    #searching cuckoo sandbox for files already analysed
    browser.get('https://sandbox.pikker.ee/analysis/search')
    element=browser.find_element(By.XPATH,'//*[@id="form_search"]')
    ActionChains(browser).key_down(Keys.COMMAND,element).send_keys('v').key_up(Keys.COMMAND,element).perform()
    A=wait.until(EC.visibility_of_any_elements_located(('xpath','//*[@id="results"]/div')))
    A=browser.find_element(By.XPATH,'//*[@id="results"]/div')
    if A.get_attribute("class")=='panel panel-primary':
        aux=browser.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/table/tbody').text
        for el in aux.split('#')[1:]:
            task_id=el.split('\n')[0]
            url='https://sandbox.pikker.ee/analysis/'+task_id+'/export'
            browser.get(url)
            try:
                # checking if the task is still in there
                wait.until(EC.presence_of_element_located((
                    By.XPATH, '/html/body/div[2]/div[2]/section/div/div/div/div/div/form/div/div/div[2]/div/div[1]/div'
                )))
                break # if so, the report is downloaded and it's not necessary to try the other tasks
            except:
                pass
        try:
            download_report(url,'/Users/joaopaulopmaues/Downloads/',reported=True,get_done=True,mybrowser=browser)
        except:
            return 'Not_Found'
            #continue to the analysis page
    else:
        return 'Not_Found'
    return task_id #if it succedes, it means it downloaded the report and it can be found in task_id.zip
    