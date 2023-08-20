# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
s = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
# to sort the JSON in my order, not alphabetically
app.config['JSON_SORT_KEYS'] = False

#################################################
# Flask Routes
#################################################
# display the available routes on the homepage
@app.route('/')
def homepage():
    return (f"""
        Hello<br/>
        <br/>
        Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>/api/v1.0/start/<start_date> ---Insert start date in YYYY-MM-DD format<br/>
        /api/v1.0/start/<start_date>/end/<end_date> ---Insert start and end dates in YYYY-MM-DD format<br/>
    """)

# precipitation route that returns key:value date:precipitation only for the prior year
@app.route('/api/v1.0/precipitation')
def precipitation():
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rows = s.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_prior).order_by(Measurement.date).all()
    precip = {_.date: _.prcp for _ in rows}
    return jsonify(precip)

# station route that returns JSONs of precipitation for the last year
@app.route('/api/v1.0/stations')
def all_stations():
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rows = s.query(Measurement.date, Measurement.prcp, Measurement.station).filter(Measurement.date >= year_prior).order_by(Measurement.date).all()
    stations = [{'station': _.station, 'date': _.date, 'precipitation': _.prcp} for _ in rows]
    return jsonify(stations)

# tobs route for most active station 'USC00519281', returns JSON for prior year
@app.route('/api/v1.0/tobs')
def most_active_station():
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rows = s.query(Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_prior).all()
    mas = [{'station': _.station, 'date': _.date, 'temp_obs': _.tobs, 'precipitation': _.prcp} for _ in rows]
    return jsonify(mas)

# dynamic date routes
#start route take start date and returns min, max, avg from start date to last date
@app.route('/api/v1.0/start/<start_date>')
def start_time(start_date):
    start = dt.datetime.strptime(start_date, '%Y-%m-%d')
    answer = s.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start)
    min, max, avg = answer[0]
    results = {'start_date': start, 'min_temp': min, 'max_temp': max, 'avg_temp': avg}
    return jsonify(results) 

#start/end route, returns min, max, avg temperatres
@app.route('/api/v1.0/start/<start_date>/end/<end_date>')
def start_and_end_time(start_date, end_date):
    start = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end = dt.datetime.strptime(end_date, '%Y-%m-%d')
    answer = s.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end)
    min, max, avg = answer[0]
    results = {'start_date': start, 'end_date': end, 'min_temp': min, 'max_temp': max, 'avg_temp': avg}
    return jsonify(results) 

s.close()

# run file
if __name__ == '__main__':
    app.run()