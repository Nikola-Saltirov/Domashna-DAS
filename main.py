import time
from datetime import timedelta, datetime
from threading import Thread
from warnings import catch_warnings

from pandas.core.interchange.dataframe_protocol import DataFrame
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import threading
from pathlib import Path
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.wait import WebDriverWait
from winerror import NOERROR
import polars as pl

import requests
from bs4 import BeautifulSoup as bs, BeautifulSoup
from selenium.webdriver.chrome.options import Options

def filter1(url):
    resp = requests.get(url)
    soup = bs(resp.text, 'html.parser')
    names = soup.find_all('option')
    names = [str(n.text) for n in names]
    names2=[]
    for n in names:
        if any(char.isdigit() for char in n):
            continue
        else:
            names2.append(n)
    print(len(names2))
    df=pl.DataFrame({
    'Names': names2,
    })
    df.write_csv('stocks/names.csv')
    filter2(url)

def filter2(url):
    df=pl.read_csv('stocks/names.csv')
    names=df['Names']
    newNames=[]
    oldNames=[]
    oldDates=[]
    newDates=[]
    for n in names:
        try:
            temp=pd.read_csv(f'./stocks/data/{n}.csv')
            if temp is not None:
                date=temp['Date'].iloc[-1]
                date_obj=datetime.strptime(date, '%d.%m.%Y')
                if date_obj.isoweekday()==5:
                    date_obj += timedelta(days=3)
                    if not date_obj>datetime.now():
                        oldNames.append(n)
                        oldDates.append(date_obj)
                else:
                    oldNames.append(n)
                    oldDates.append(date_obj)
        except:
            newNames.append(n)
            newDates.append(datetime(2014, 1, 1))

    print("FINISHED CATEGORIZING")
    if len(newNames)>4:
        percent=0.25
        arr1=newNames[:int(len(newNames)*percent)]
        arr2=newNames[int(len(newNames)*percent):int(len(newNames)*(percent*2))]
        arr3=newNames[int(len(newNames)*percent*2):int(len(newNames)*(percent*3))]
        arr4=newNames[int(len(newNames)*percent*3):]
        darr1 = newDates[:int(len(newDates) * percent)]
        darr2 = newDates[int(len(newDates) * percent):int(len(newDates) * (percent * 2))]
        darr3 = newDates[int(len(newDates) * percent * 2):int(len(newDates) * (percent * 3))]
        darr4 = newDates[int(len(newDates) * percent * 3):]
        threads=[]
        threads.append(threading.Thread(target=update, args=(darr1,arr1,url,False), name="1"))
        threads.append(threading.Thread(target=update, args=(darr2,arr2,url,False), name="2"))
        threads.append(threading.Thread(target=update, args=(darr3,arr3,url,False), name="3"))
        threads.append(threading.Thread(target=update, args=(darr4,arr4,url,False), name="4"))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print("FINISHED")
    elif len(newNames)>0:
        update(newDates,newNames,url,False)
    filter3(oldNames,oldDates)

def filter3(newNames,newDates):
    print("STARTED FILTER3")
    if len(newNames)>4:
        percent=0.25
        arr1=newNames[:int(len(newNames)*percent)]
        arr2=newNames[int(len(newNames)*percent):int(len(newNames)*(percent*2))]
        arr3=newNames[int(len(newNames)*percent*2):int(len(newNames)*(percent*3))]
        arr4=newNames[int(len(newNames)*percent*3):]
        darr1 = newDates[:int(len(newDates) * percent)]
        darr2 = newDates[int(len(newDates) * percent):int(len(newDates) * (percent * 2))]
        darr3 = newDates[int(len(newDates) * percent * 2):int(len(newDates) * (percent * 3))]
        darr4 = newDates[int(len(newDates) * percent * 3):]
        threads=[]
        threads.append(threading.Thread(target=update, args=(darr1,arr1,url,True), name="1f3"))
        threads.append(threading.Thread(target=update, args=(darr2,arr2,url,True), name="2f3"))
        threads.append(threading.Thread(target=update, args=(darr3,arr3,url,True), name="3f3"))
        threads.append(threading.Thread(target=update, args=(darr4,arr4,url,True), name="4f3"))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    elif len(newNames)>0:
        update(newDates,newNames,url,True)
    print("FINISHED FILTER3")

def update(dates,names,url,rewrite):
    id=threading.current_thread().name
    time_start=time.time()
    count=0
    print(f'STARTED WITH {id}')
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)
    driver.implicitly_wait(10)
    driver.get(url)
    print(f'OPENED WITH {id}')
    date_to = datetime.today()
    for name,date in zip(names,dates):
        interval = timedelta(days=365)
        Input = driver.find_element(By.ID, 'Code')
        Input.send_keys(name)
        current_date = date
        new_list=[]
        while current_date < date_to:
            end_date=current_date + interval
            if end_date > date_to:
                end_date = date_to

            try:
                fromDateInput = driver.find_element(By.ID, 'FromDate')
                toDateInput = driver.find_element(By.ID, 'ToDate')
                btn = driver.find_element(By.CLASS_NAME, 'btn-primary-sm')
                fromDateInput.clear()
                fromDateInput.send_keys(current_date.strftime('%d.%m.%Y'))
                toDateInput.clear()
                toDateInput.send_keys(end_date.strftime('%d.%m.%Y'))
                btn.click()
            except:
                time_end=time.time()
                print(f"INPUTS ARE NOT FOUND FOR THREAD {id} WHILE PROCESSING {count} AFTER {time_end-time_start:.2f}")
                print(f'FAILED WITH THREAD {id} WITH {len(names)-count} ELEMENTS LEFT')
                return
            # TO DO
            try:
                WebDriverWait(driver, 0.5).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'tr')))
                time.sleep(0.5)
            except:
                if current_date + interval > date_to:
                    break
                else:
                    current_date=end_date
                    continue
            try:
                table = driver.find_element(By.CSS_SELECTOR, '#resultsTable > tbody:nth-child(2)')
                soup = BeautifulSoup(table.get_attribute('innerHTML'), 'html.parser')
                elements = soup.find_all('tr')
                for i in range(len(elements)+1):
                    tds = elements[-i].find_all('td')
                    date = tds[0].text
                    last_traded_price = tds[1].text
                    max= tds[2].text
                    min = tds[3].text
                    avg_price = tds[4].text
                    promet = tds[5].text
                    volume = tds[6].text
                    promet_BEST = tds[7].text
                    promet_vo_denari = tds[8].text
                    stock={
                        "Date":date,
                        "last_traded_price":last_traded_price,
                        "max":max,
                        "min":min,
                        "avg_price":avg_price,
                        "promet":promet,
                        "volume":volume,
                        "promet_BEST":promet_BEST,
                        "promet_vo_denari":promet_vo_denari
                    }
                    new_list.append(stock)
            except:
                print(f"No data for {name} from {current_date} to {end_date}")
                if current_date + interval > date_to:
                    break
                else:
                    current_date = end_date
                    continue
            current_date = end_date
        if rewrite:
            df=pd.read_csv(f'./stocks/data/{name}.csv')
            newdf=pd.DataFrame(new_list)
            df = pd.concat([df, newdf], ignore_index=True)
            df.to_csv(f'./stocks/data/{name}.csv', index=False)
        else:
            df=pl.DataFrame(new_list)
            df.write_csv(f'stocks/data/{name}.csv')
        count+=1
        print(f"FINISHED with {name} from thread {id}, COUNT={count}")
    driver.quit()

if __name__ == '__main__':
    now=time.time()
    url='https://www.mse.mk/mk/stats/symbolhistory/ALK'
    filter1(url)
    now2=time.time()
    print(f"Function took {(now2-now)/60:.2f} minutes to complete.")