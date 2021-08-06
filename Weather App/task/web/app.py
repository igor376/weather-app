from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from ApiKey import api_key
import sys
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

cities_info = []


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'{self.name}'


db.create_all()


@app.route("/")
def main_page():
    global cities_info
    if len(cities_info) == 0:
        for city in City.query.all():
            cities_info.append(get_temperature(city))
    return render_template("index.html", cities=cities_info)


@app.route('/', methods=['POST'])
def add_city():
    city_name = request.form["city_name"]
    if City.query.filter_by(name=city_name).first() is None:
        city = get_temperature(city_name)
        db.session.add(City(id=len(City.query.all()) + 1, name=city_name))
        db.session.commit()
        cities_info.append(city)
    return render_template("index.html", cities=cities_info)
    # print(dict_with_weather_info)
    # return render_template("index.html", cities=[get_temperature(city_name)])


def get_temperature(city_name):
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric')
    if r.status_code != 200:
        abort(401)
    j = r.json()
    dict_with_weather_info = {"state": j["weather"][0]["main"], "city": j["name"], "degrees": j["main"]["temp"]}
    return dict_with_weather_info


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
