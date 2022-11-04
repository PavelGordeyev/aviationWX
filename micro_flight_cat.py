from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests
import json

app = Flask(__name__)
api = Api(app)

class FlightCategory(Resource):

	def __init__(self):
		self.url = 'http://127.0.0.1:5000/conditions?airportCode='

	def get(self):

		parser = reqparse.RequestParser()
		parser.add_argument('airportCode', required=True, type=str)

		args = parser.parse_args()
		airportCode = args['airportCode'].upper()

		res = requests.get(self.url + airportCode)

		if res.status_code == 404:
			return {'Error': '404 - Not found'}, 404
		else:
			try:
				return {
					'airport_code': airportCode,
					'flight_category': res.json()[airportCode]['flight_category']
				}, 200
			except Exception as e:
				return {
					"Error": e
				}, 404

api.add_resource(FlightCategory, '/flightcat')

if __name__ == '__main__':
	app.run(port=8000,debug=True)