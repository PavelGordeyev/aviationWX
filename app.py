from flask import Flask
from flask_restful import Resource, Api, reqparse
from weather import Weather

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

api.add_resource(AirportConditions, '/conditions')

if __name__ == '__main__':
	app.run(debug=True)