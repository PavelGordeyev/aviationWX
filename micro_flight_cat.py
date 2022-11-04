from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests
import json

app = Flask(__name__)
api = Api(app)

class FlightCategory(Resource):

	def __init__(self):
		self.url = 'http://127.0.0.1:5000/conditions?airport_code='

	def get(self):

		parser = reqparse.RequestParser()
		parser.add_argument('airport_code', required=True, type=str)

		args = parser.parse_args()
		airport_code = args['airport_code'].upper()

		res = requests.get(self.url + airport_code)

		if res.status_code == 404:
			return res.json(), 404
		else:
			try:
				return {
					'airport_code': airport_code,
					'flight_category': res.json()[airport_code]['flight_category']
				}, 200
			except Exception as e:
				return {
					"Error": e
				}, 404

api.add_resource(FlightCategory, '/flight_category')

if __name__ == '__main__':
	app.run(port=8000,debug=True)