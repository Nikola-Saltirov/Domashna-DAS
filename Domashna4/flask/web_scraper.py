import time
from datetime import timedelta, datetime
import pandas as pd
import threading
from pathlib import Path
import polars as pl
import requests
from bs4 import BeautifulSoup as bs, BeautifulSoup
import os
# Path to the CSV directory
BASE_DIR = os.getenv("CSV_DIR", "./temp_stocks")

semaphore = threading.Semaphore(6)

def filter1(url):
    now = time.time()
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
    csv_path = os.path.join(BASE_DIR, 'names.csv')
    df.write_csv(csv_path)
    filter2()
    now2 = time.time()
    print(f"Function took {(now2 - now) / 60:.2f} minutes to complete.")
    return (now2 - now) / 60

def filter2():
    csv_path = os.path.join(BASE_DIR, 'names.csv')
    df=pl.read_csv(csv_path)
    names=df['Names']
    newNames=[]
    newDates=[]
    for n in names:
        try:
            fileName = f'{n}.csv'
            csv_path = os.path.join(BASE_DIR, 'temp_data', fileName)
            temp=pd.read_csv(csv_path)
            if temp is not None:
                date=temp['Date'].iloc[-1]
                date_obj=datetime.strptime(date, '%d.%m.%Y')
                if date_obj.isoweekday()==5:
                    date_obj += timedelta(days=3)
                    if not date_obj>datetime.now():
                        newNames.append(n)
                        newDates.append(date_obj)
                elif date_obj+timedelta(days=1)<datetime.now():
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
            date_to = datetime.today()
            interval = timedelta(days=365)
            current_date = date
            new_list=[]
            while current_date < date_to:
                end_date=current_date + interval
                if end_date > date_to:
                    end_date = date_to
                payload={
                    "FromDate":current_date.strftime('%d.%m.%Y'),
                    'ToDate':end_date.strftime('%d.%m.%Y')
                }
                resp=requests.post(url, data=payload)
                if resp.status_code!=200:
                    count += 1
                    print(f'FAILED WITH THREAD {id} FOR {count} from {current_date} to {end_date}')
                    dataSecurity = False
                    break
                try:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    elements=soup.find_all('tr')
                    elements=elements[1:]
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
                        # print(stock)
                except:
                    if current_date + interval > date_to:
                        break
                    else:
                        current_date = end_date
                        continue
                current_date = end_date
                if rewrite:
                    fileName = f'{name}.csv'
                    csv_path = os.path.join(BASE_DIR, 'temp_data', fileName)
                    df=pd.read_csv(csv_path)
                    newdf=pd.DataFrame(new_list)
                    df = pd.concat([df, newdf], ignore_index=True)
                    df.to_csv(csv_path, index=False)
                else:
                    df=pl.DataFrame(new_list)
                    fileName = f'{name}.csv'
                    csv_path = os.path.join(BASE_DIR, 'temp_data', fileName)
                    df.write_csv(csv_path)
            count+=1
            fileName = f'{name}.csv'
            csv_path = os.path.join(BASE_DIR, 'temp_data', fileName)
            df = pd.read_csv(csv_path)
            df.drop_duplicates(keep='last', inplace=True)
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            df = df.reset_index()
            df.fillna(0, inplace=True)
            df.rename(columns={'index': 'Date'}, inplace=True)
            df['Date'] = df['Date'].dt.strftime('%d.%m.%Y')
            df.to_csv(csv_path, index=False)
            if dataSecurity is False:
                continue
            print(f"FINISHED with {name} from thread {id}")
            break

if __name__ == '__main__':
    now=time.time()
    url='https://www.mse.mk/mk/stats/symbolhistory/ALK'
    filter1(url)
    now2=time.time()
    folder_path = Path('temp_stocks/temp_data')
    file_count = len([f for f in folder_path.iterdir() if f.is_file()])
    print(f"There are {file_count} files in the folder.")
    print(f"Function took {(now2-now)/60:.2f} minutes to complete.")