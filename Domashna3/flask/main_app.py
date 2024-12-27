import datetime

from flask import Flask, send_file, jsonify, request, make_response
import polars as pl

from oscilators.DMI import calcDMI
from oscilators.ao import calcAO
from oscilators.cci import calcCCI
from oscilators.cmo import calcCMO
from oscilators.rsi import calcRSI
from oscilators.stochastic_o import calcSO
from web_scraper import filter1
from moving_averages import MovingAverageCrossStrategy
from lstm_model import StocksAveragePricePredictor
from oscilators import *
app = Flask(__name__)

@app.route('/startup', methods=['GET'])
def startupScrape():
    # image_path = "img/forest.png"
    url = 'https://www.mse.mk/mk/stats/symbolhistory/ALK'
    filter1(url)
    resp={
        'message': 'finished'
    }
    # return send_file(image_path, mimetype='image/png')
    return resp
@app.route('/get_names', methods=['GET'])
def getNames():
    df = pl.read_csv('temp_stocks/names.csv')
    names = df['Names'].to_list()
    return jsonify(names)

@app.route('/generate-image-history', methods=['GET'])
def getImageHistory():

    tiker = request.args.get('tiker', 'ALK')
    interval = request.args.get('interval', '7')
    prikaz = request.args.get('prikaz', 'SMA')

    today = datetime.date.today()
    last = today - datetime.timedelta(days=int(interval))

    if interval == '7':
        short_window=2
        long_window=4
    elif interval == '14':
        short_window=3
        long_window=7
    elif interval == '30':
        short_window=5
        long_window=10
    elif interval == '60':
        short_window=10
        long_window=20
    elif interval == '90':
        short_window=15
        long_window=30
    elif interval == '120':
        short_window=20
        long_window=40
    elif interval == '180':
        short_window=30
        long_window=60
    else:
        short_window=2
        long_window=4

    if prikaz == 'DMI':
        img_io=calcDMI(tiker=tiker, interval=interval, start_date=last, end_date=today, short_window=short_window)
    elif prikaz == 'AO':
        today = datetime.date.today()
        last = today - datetime.timedelta(days=int(44+int(interval)))
        img_io=calcAO(tiker=tiker, interval=interval, start_date=last, end_date=today, short_window=short_window)
    elif prikaz == 'CCI':
        img_io=calcCCI(tiker=tiker, interval=interval, start_date=last, end_date=today, short_window=short_window)
    elif prikaz == 'CMO':
        img_io=calcCMO(tiker=tiker, interval=interval, start_date=last, end_date=today, short_window=short_window)
    elif prikaz == 'RSI':
        img_io=calcRSI(tiker=tiker, interval=interval, start_date=last, end_date=today, short_window=short_window)
    elif prikaz == 'SO':
        img_io=calcSO(tiker=tiker, interval=interval, start_date=last, end_date=today, short_window=short_window)
    else:
        img_io=MovingAverageCrossStrategy(tiker=tiker, start_date=last, end_date=today, moving_avg=prikaz, short_window=short_window, long_window=long_window)

    response = make_response(img_io.read())
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route('/generate-image-projections', methods=['GET'])
def getImageProjections():
    tiker = request.args.get('tiker', 'ALK')
    interval = request.args.get('interval', '7')
    predictor = StocksAveragePricePredictor(tiker, 7, int(interval), 'avg_price')
    # predictor = StocksAveragePricePredictor(tiker,  7, 'avg_price')
    img_io = predictor.predict_and_plot()
    response = make_response(img_io.read())
    response.headers['Content-Type'] = 'image/png'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
