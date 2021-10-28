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
		x = Weather()
		x.getMetar()
		return {'test': 'hello world'}, 200


class Weather():

	def __init__(self):
		self.url = 'https://www.aviationweather.gov/adds/dataserver_current/current/metars.cache.csv'
		self.headerLines = 5
		self.data = {}

	def getMetars(self):
		
		req = requests.get(self.url)
		df = pd.read_csv(io.StringIO(req.text), skiprows=self.headerLines)

		if df.empty:
			return 0

		try:
			self.data = df.drop_duplicates(subset='station_id').set_index('station_id', verify_integrity=True).to_dict('index')
		except ValueError:
			return -1

		return 1

api.add_resource(AirportConditions, '/conditions')

if __name__ == '__main__':
	app.run(debug=True)