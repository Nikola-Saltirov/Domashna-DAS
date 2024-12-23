import datetime

from flask import Flask, send_file, jsonify, request, make_response
import polars as pl
from web_scraper import filter1
from moving_averages import MovingAverageCrossStrategy
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

@app.route('/generate-image', methods=['GET'])
def getImage():

    metric = request.args.get('text', 'default_metric')
    chart_type = request.args.get('color', 'line')

    print(metric, chart_type)

    tiker='ALK'
    interval='30'
    prikaz = 'SMA'
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

    img_io=MovingAverageCrossStrategy(tiker=tiker, start_date=last, end_date=today, moving_avg=prikaz, short_window=short_window, long_window=long_window)

    response = make_response(img_io.read())
    response.headers['Content-Type'] = 'image/png'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
