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
import polars as pl
import requests
from bs4 import BeautifulSoup as bs, BeautifulSoup
from selenium.webdriver.chrome.options import Options

semaphore = threading.Semaphore(10)

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
    filter2()

def filter2():
    df=pl.read_csv('stocks/names.csv')
    names=df['Names']
    newNames=[]
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
                        newNames.append(n)
                        newDates.append(date_obj)
                else:
                    newNames.append(n)
                    newDates.append(date_obj)
        except:
            newNames.append(n)
            newDates.append(datetime(2014, 1, 1))

    print("FINISHED CATEGORIZING")
    filter3(newNames,newDates)
    print(len(newNames))

def filter3(newNames,newDates):
    print("STARTED FILTER3")
    threads=[]
    for n,d in zip(newNames,newDates):
        rewrite=False
        if d!=datetime(2014, 1, 1):
            rewrite=True
        threads.append(threading.Thread(target=update, args=(d, n, rewrite), name=f"{n}"))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("FINISHED FILTER3")

def update(date, name, rewrite):
    with semaphore:
        count=0
        while True:
            dataSecurity=True
            id=threading.current_thread().name
            url=f'https://www.mse.mk/mk/stats/symbolhistory/{name}'
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(60)
            driver.set_script_timeout(60)
            driver.implicitly_wait(5)
            driver.get(url)
            date_to = datetime.today()
            interval = timedelta(days=365)
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
                    count+=1
                    print(f'FAILED WITH THREAD {id} FOR {count} from {current_date} to {end_date}')
                    dataSecurity=False
                    break
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
                        stock={
                            "Date":tds[0].text,
                            "last_traded_price":tds[1].text,
                            "max":tds[2].text,
                            "min":tds[3].text,
                            "avg_price":tds[4].text,
                            "promet":tds[5].text,
                            "volume":tds[6].text,
                            "promet_BEST":tds[7].text,
                            "promet_vo_denari":tds[8].text
                        }
                        new_list.append(stock)
                except:
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
            driver.quit()
            if dataSecurity is False:
                continue
            print(f"FINISHED with {name} from thread {id}")
            break

if __name__ == '__main__':
    now=time.time()
    url='https://www.mse.mk/mk/stats/symbolhistory/ALK'
    filter1(url)
    now2=time.time()
    folder_path = Path('stocks/data')
    file_count = len([f for f in folder_path.iterdir() if f.is_file()])
    print(f"There are {file_count} files in the folder.")
    print(f"Function took {(now2-now)/60:.2f} minutes to complete.")