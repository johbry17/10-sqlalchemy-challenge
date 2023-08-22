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
M = Base.classes.measurement

# Create our session (link) from Python to the DB
s = Session(bind=engine)

# set global variable to use in queries below
year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
# disable automatic alphabetical sorting of JSON results, for control over order of output
app.config["JSON_SORT_KEYS"] = False


#################################################
# Flask Routes
#################################################
# display the available routes on the homepage
@app.route("/")
def homepage():
    return f"""
        Hello<br/>
        <br/>
        Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>/api/v1.0/start/<start_date> ---Insert start date in YYYY-MM-DD format<br/>
        /api/v1.0/start/<start_date>/end/<end_date> ---Insert start and end dates in YYYY-MM-DD format<br/>
    """


# precipitation route that returns key:value date:precipitation only for the prior year
@app.route("/api/v1.0/precipitation")
def precipitation():
    rows = s.query(M.date, M.prcp).filter(M.date >= year_prior).order_by(M.date).all()
    precip = {_.date: _.prcp for _ in rows}
    return jsonify(precip)


# station route that returns a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    rows = s.query(
        Station.station,
        Station.name,
        Station.latitude,
        Station.longitude,
        Station.elevation,
    )
    results = [
        {
            "station": _.station,
            "name": _.name,
            "latitude": _.latitude,
            "longitude": _.longitude,
            "elevation": _.elevation,
        }
        for _ in rows
    ]
    return jsonify(results)


# tobs route for most active station 'USC00519281', returns JSON for prior year
@app.route("/api/v1.0/tobs")
def most_active_station():
    rows = (
        s.query(M.station, Station.name, M.date, M.prcp, M.tobs)
        .filter(M.station == "USC00519281")
        .filter(M.date >= year_prior)
        .join(Station, M.station == Station.station)
        .all()
    )
    mas = [
        {
            "station": _.station,
            "name": _.name,
            "date": _.date,
            "temp_obs": _.tobs,
            "precipitation": _.prcp,
        }
        for _ in rows
    ]
    return jsonify(mas)


# dynamic date routes
# function to format datetime from a string
def time(date_string):
    return dt.datetime.strptime(date_string, "%Y-%m-%d")


# function to return min, max, average temperatures
def time_stats(query):
    min_temp, max_temp, avg_temp = query[0]
    return {"min_temp": min_temp, "max_temp": max_temp, "avg_temp": avg_temp}


# start route - take start date and returns min, max, avg from start date to last date
@app.route("/api/v1.0/start/<start_date>")
def start_time(start_date):
    start = time(start_date)
    results = time_stats(
        s.query(func.min(M.tobs), func.max(M.tobs), func.avg(M.tobs)).filter(
            M.date >= start
        )
    )
    results["start_date"] = start
    return jsonify(results)


# start/end route - take start and end dates, returns min, max, avg temperatres
@app.route("/api/v1.0/start/<start_date>/end/<end_date>")
def start_and_end_time(start_date, end_date):
    start = time(start_date)
    end = time(end_date)
    results = time_stats(
        s.query(func.min(M.tobs), func.max(M.tobs), func.avg(M.tobs))
        .filter(M.date >= start)
        .filter(M.date <= end)
    )
    results["start_date"] = start
    results["end_date"] = end
    return jsonify(results)


# close session
s.close()

# run file
if __name__ == "__main__":
    app.run()
