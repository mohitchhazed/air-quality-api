from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///air_quality.db')
Base = declarative_base()

class AirQuality(Base):
    __tablename__ = 'air_quality'
    id = Column(Integer, primary_key=True)
    city = Column(String)
    aqi = Column(Integer)
    time_updated = Column(DateTime)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Function to get air quality data from API
def fetch_air_quality():
    url = f'https://api.waqi.info/feed/stuttgart/?token={os.environ.get("API_TOKEN")}'
    response = requests.get(url)
    try:
        data = response.json()
    except ValueError as e:
        print(f"Error parsing JSON: {e}")
        return
    
    if 'data' in data:
        return data['data']['aqi'], datetime.utcnow()
    else:
        return None, None

# Endpoint to fetch and store air quality data every 15 minutes
@app.route('/fetch-and-store')
def fetch_and_store():
    aqi, time_updated = fetch_air_quality()
    if aqi is not None and time_updated is not None:
        new_data = AirQuality(city='Stuttgart', aqi=aqi, time_updated=time_updated)
        session.add(new_data)
        session.commit()
        return 'Data fetched and stored successfully'
    else:
        return 'Failed to fetch data'

# Endpoint to get current AQI and last update time
@app.route('/aqi')
def get_aqi():
    latest_data = session.query(AirQuality).order_by(AirQuality.id.desc()).first()
    if latest_data:
        return jsonify({
            'Air Quality Index (AQI)': latest_data.aqi,
            'Last Update Time': latest_data.time_updated.strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return 'No data available'

# Endpoint to return status of the application
@app.route('/status')
def get_status():
    total_records = session.query(AirQuality).count()
    return jsonify({
        'Total Records': total_records,
        'Status': 'Running'
    })

# Endpoint to forcefully update and return current AQI
@app.route('/refresh')
def refresh_aqi():
    aqi, time_updated = fetch_air_quality()
    if aqi is not None and time_updated is not None:
        return jsonify({
            'Air Quality Index (AQI)': aqi,
            'Last Update Time': time_updated.strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return 'Failed to refresh data'

if __name__ == '__main__':
    app.run(debug=True)