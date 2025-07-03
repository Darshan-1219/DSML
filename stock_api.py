from flask import Flask, request, Response, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def retrieve_stock_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end, auto_adjust=False)
    if data.empty:
        return None
    data = data.reset_index()
    data['Date'] = data['Date'].astype(str)
    # Use pandas to_json for robust serialization
    return data.to_json(orient='records', date_format='iso')

@app.route('/api/stock_data', methods=['GET'])
def get_stock_data():
    stock_symbol = request.args.get('symbol', default='AAPL')
    start_date = request.args.get('start_date', default='2024-01-01')
    end_date = request.args.get('end_date', default='2025-07-02')
    if not all([stock_symbol, start_date, end_date]):
        return jsonify({"error": "Missing required fields: symbol, start_date, end_date"}), 400
    try:
        stock_data_json = retrieve_stock_data(stock_symbol, start_date, end_date)
        if stock_data_json is None:
            return jsonify({"error": "No data found for the given symbol and date range."}), 404
        return Response(stock_data_json, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import requests
@app.route('/api/option_chain', methods=['POST', 'GET'])
def get_option_chain():
    symbol = request.args.get('symbol', default='NIFTY')
    expiry_date = pd.to_datetime(pd.Timestamp.today()).strftime('%d-%b-%Y')
    url = f'https://www.nseindia.com/api/option-chain-indices?symbol={symbol}'
    # if expiry_date:
    #     url += f'&expiryDate={expiry_date}'
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        # Remove 'br' from Accept-Encoding
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get('Content-Type', ''))
        print("Content (first 500):", response.text[:500])
        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({"error": "NSE returned non-JSON response", "content": response.text[:500]}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')