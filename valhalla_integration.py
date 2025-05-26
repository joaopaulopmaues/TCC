from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime as dt
from datetime import date
from dateutil.relativedelta import relativedelta
import time

#Browsing each ransomware family

#familynamelist=['black','wannacry']


def list_rules(browser,familyname,inputdate='0000-00-00',quant=5,t=10):#date limit and max quantity
    if inputdate=='0000-00-00':
        today=date.today()
        date=today.strftime('%Y-%m-%d')
        dobj=dt.strptime(date,'%Y-%m-%d').date()
        date=dobj+relativedelta(years=-1)
        date=date.strftime('%Y-%m-%d')
    else:
        date=inputdate
    q=0
    wait = WebDriverWait(browser, timeout=20)
    lim_d = dt.strptime(date,'%Y-%m-%d')
    url='https://valhalla.nextron-systems.com/info/search?keyword='+familyname
    browser.get(url)
    try:
        wait.until(EC.presence_of_element_located(
            ('xpath','/html/body/section/section/div[3]/div[2]/div[2]')))
    except:
        return []
    #Retrieving YARA rules names
    YARA=[]#list
    x=0+2
    while q<quant:
        #print(q,quant)
        back=''+browser.current_url
        s="(//*[contains(@class, 'tcell')])["+str(x)+"]"
        d="(//*[contains(@class, 'tcell')])["+str(x+2)+"]"
        try:
            d=browser.find_element('xpath',d).text
            d=dt.strptime(d,'%Y-%m-%d')
            if d > lim_d:
                #print(d,lim_d)
                aux=browser.find_element('xpath',s).text
            else:
                break
        except Exception as e:
            break
        
        sigmaflag=x-1
        if (browser.find_element('xpath',"(//*[contains(@class, 'tcell')])["+str(sigmaflag)+"]").text!='YARA'):
            x+=8
            continue
        
        url='https://valhalla.nextron-systems.com/info/rule/'+aux
        time.sleep(t)
        browser.get(url)
        try:
            s='/html/body/section/section/div[3]/div[3]/div[2]/div[4]'
            browser.find_element('xpath',s).text
            YARA.append(aux)
            q+=1
        except Exception as e2:
            #url=back
            time.sleep(t)
            browser.back()#browser.get(back)
            x+=8
            continue
        #url=back
        time.sleep(t)
        browser.back()#browser.get(back)
        x+=8
    return YARA

def e2a_list_hashes(browser,YARA,t=20): #YARA is a list of YARA rule names found after running list_rules
    result=[]
    for s in YARA:
        url='https://valhalla.nextron-systems.com/info/rule/'+s
        time.sleep(t)
        browser.get(url)
        i=2
        while (True):
            s='/html/body/section/section/div[3]/div[3]/div['+str(i)+']/div[4]'
            try:
                a=browser.find_element('xpath',s).text
                result.append(a)
                i+=1
            except:
                break
    return result

def easier_to_understand_valhalla(browser,familyname,date='0000-00-00',quant=5,t=10):
    #e2a_valhalla, e2a_list_rules, e2a_list_hashes
    YARA=list_rules(browser, familyname, date, quant,t)
    result=e2a_list_hashes(browser,YARA,2*t)
    return set(result)
        #with open(path,'w',newline='') as f: #path will be a string that contains hasheslist.csv
        #    f.write(a+','+familyname)
        
def list_hashes(browser,YARA,t=20):
    wait = WebDriverWait(browser,timeout=20)
    result=set()
    for s in YARA:
        url='https://valhalla.nextron-systems.com/info/rule/'+s
        time.sleep(t)
        browser.get(url)
        i=2
        while (True):
            s='/html/body/section/section/div[3]/div[3]/div['+str(i)+']/div[4]'
            try:
                wait.until(EC.presence_of_element_located(
                    ('xpath',s)
                ))
                a=browser.find_element('xpath',s).text
                result.update([a])
                i+=1
            except:
                break
    return result

def valhalla(browser,familyname,inputdate='0000-00-00',quant=5,t=10):#date limit and max quantity
    result=set()
    if inputdate=='0000-00-00':
        today=date.today()
        date=today.strftime('%Y-%m-%d')
        dobj=dt.strptime(date,'%Y-%m-%d').date()
        date=dobj+relativedelta(years=-1)
        date=date.strftime('%Y-%m-%d')
    else:
        date=inputdate
    q=0
    wait = WebDriverWait(browser, timeout=20)
    lim_d = dt.strptime(date,'%Y-%m-%d')
    url='https://valhalla.nextron-systems.com/info/search?keyword='+familyname
    browser.get(url)
    try:
        wait.until(EC.presence_of_element_located(
            ('xpath','/html/body/section/section/div[3]/div[2]/div[2]')))
    except:
        return []
    #Retrieving YARA rules names
    #YARA=[]#list
    x=0+2
    while q<quant:
        #print(q,quant)
        back=''+browser.current_url
        s="(//*[contains(@class, 'tcell')])["+str(x)+"]"
        d="(//*[contains(@class, 'tcell')])["+str(x+2)+"]"
        try:
            d=browser.find_element('xpath',d).text
            d=dt.strptime(d,'%Y-%m-%d')
            if d > lim_d:
                #print(d,lim_d)
                rule=browser.find_element('xpath',s).text
            else:
                break
        except Exception as e:
            break
        
        sigmaflag=x-1
        if (browser.find_element('xpath',"(//*[contains(@class, 'tcell')])["+str(sigmaflag)+"]").text!='YARA'):
            x+=8
            continue
        
        #url='https://valhalla.nextron-systems.com/info/rule/'+aux
        #time.sleep(t)
        #browser.get(url)
        try:
            #s='/html/body/section/section/div[3]/div[3]/div[2]/div[4]'
            #browser.find_element('xpath',s).text
            #YARA.append(aux)
            result.update(list_hashes(browser,[rule],t))
            q+=1
        except Exception as e2:
            #url=back
            time.sleep(t)
            browser.back()#browser.get(back)
            x+=8
            continue
        #url=back
        time.sleep(t)
        browser.back()#browser.get(back)
        x+=8
    return result