from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests
import pandas as pd
import io
import json

app = Flask(__name__)
api = Api(app)

class AirportConditions(Resource):

	def get(self):
		
		wx = Weather()

		parser = reqparse.RequestParser()
		parser.add_argument('airportCode', required=True, type=str)

		args = parser.parse_args()

		isLoaded, data = wx.getMetar(args['airportCode'])

		if isLoaded:
			return {
				f"{args['airportCode']}": data
			}, 200
		else:
			return data, 404	


class Weather():

	def __init__(self):
		self.url = 'https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv'
		self.headerLines = 5
		self.data = None
		self.jsonURL = './weather_data.json'


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

	def getMetar(self, airportCode):

		if self.loadMetars() == 1:
			try:
				return 1, self.data[airportCode]
			except KeyError:
				return 0, {'Error': 'Invalid airport code'}

		else:
			return 0, {'Error': 'Error parsing METARS...'}

	def loadToFile(self):

		with open(self.jsonURL, 'w') as f:
			json.dump(self.data, f)

	def loadFromFile(self):

		try:
			with open(self.jsonURL, 'r') as f:
				self.data = json.load(f)
		
		except FileNotFoundError:
			return

api.add_resource(AirportConditions, '/conditions')

if __name__ == '__main__':
	app.run(debug=True)