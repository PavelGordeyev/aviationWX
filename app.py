from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests
import pandas as pd
import io
import json
import os
import time

app = Flask(__name__)
api = Api(app)

class AirportConditions(Resource):

	def get(self):
		
		wx = Weather()

		parser = reqparse.RequestParser()
		parser.add_argument('airport_code', required=True, type=str)

		args = parser.parse_args()

		is_loaded, data = wx.getMetar(args['airport_code'].upper())

		if is_loaded:
			return {
				f"{args['airport_code']}": data
			}, 200
		else:
			return data, 404	


class Weather():

	def __init__(self):
		self.url = 'https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv'
		self.headerLines = 5
		self.minutes_till_update = 10
		self.data = None
		self.weather_json_url = './weather_data.json'


	def loadMetars(self):

		self.loadFromFile()

		if self.data is None:
			return self.pullMetars()

		return 1

	def pullMetars(self):
		
		req = requests.get(self.url)
		df = pd.read_csv(io.StringIO(req.text), skiprows=self.headerLines)
		df.fillna('', inplace=True)

		if df.empty:
			return 0

		try:
			self.data = df.drop_duplicates(subset='station_id').set_index('station_id', verify_integrity=True).to_dict('index')
			self.loadToFile()
		except ValueError:
			return -1

		return 1

	def getMetar(self, airport_code):

		if self.loadMetars() == 1:
			try:
				return 1, self.data[airport_code]
			except KeyError:
				return 0, {'Error': 'Invalid airport code'}

		else:
			return 0, {'Error': 'Error parsing METARS...'}

	def loadToFile(self):

		with open(self.weather_json_url, 'w') as f:
			json.dump(self.data, f)

	def loadFromFile(self):

		try:
			with open(self.weather_json_url, 'r') as f:
				
				# Check last time the data was modified
				modified = os.path.getmtime(self.weather_json_url)
				print("Data last pulled: ", time.ctime(modified))
				print("Time now: ", time.ctime(time.time()))
				if (time.time() - (self.minutes_till_update * 60)) > modified:
					print("Pulling new metars...")
					self.pullMetars()
					return

				print("Loading previous metars...")
				self.data = json.load(f)
		
		except FileNotFoundError:
			return

api.add_resource(AirportConditions, '/conditions')

if __name__ == '__main__':
	app.run(debug=True)