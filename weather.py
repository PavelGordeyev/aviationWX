import requests
import io
import os
import time
import json
import pandas as pd

class Weather:

    def __init__(self):
        self.url = 'https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv'
        self.header_lines = 5
        self.minutes_till_update = 10
        self.data = None
        self.weather_json_url = './weather_data.json'

    def getMetar(self, airport_code):
        if self.loadMetars():
            try:
                return 1, self.data[airport_code]
            except KeyError:
                return 0, {'Error': 'Invalid airport code'}

        else:
            return 0, {'Error': 'Error parsing METARS...'}

    def loadMetars(self):
        # Check last time the data was modified
        time_modified = os.path.getmtime(self.weather_json_url)
        time_to_reload_data = time.time() - (self.minutes_till_update * 60)

        print("Time - latest updated weather data: ", time.ctime(time_modified))
        print("Time - request received: ", time.ctime(time.time()))

        if time_to_reload_data > time_modified:
            print("Pulling new metars...")
            return self.pullMetars()
        else:
            print("Loading previous metars...")
            return self.loadFromFile()


    def pullMetars(self):
        req = requests.get(self.url)
        metar_data_file = pd.read_csv(io.StringIO(req.text), skiprows=self.header_lines)
        metar_data_file.fillna('', inplace=True)

        if metar_data_file.empty:
            return 0

        try:
            self.data = metar_data_file.drop_duplicates(subset='station_id').set_index('station_id', verify_integrity=True).to_dict(
                'index')
        except ValueError:
            return 0, {'Error': 'Metar value error'}

        try:
            self.loadToFile()
            return 1
        except Exception as e:
            return 0, {'Error': e}


    def loadToFile(self):
        try:
            with open(self.weather_json_url, 'w') as f:
                try:
                    json.dump(self.data, f)
                    return 1
                except TypeError:
                    return 0, {'Error': 'Unable to serialize object'}
        except FileNotFoundError:
            return 0, {'Error': 'File not found'}

    def loadFromFile(self):
        try:
            with open(self.weather_json_url, 'r') as f:
                try:
                    self.data = json.load(f)
                    return 1
                except JSONDecodeError:
                    return 0, {'Error': 'JSON decoding error'}

        except FileNotFoundError:
            return 0, {'Error': 'File not found'}