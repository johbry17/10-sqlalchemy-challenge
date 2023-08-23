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
        <a href="/api/v1.0/precipitation">Precipitation</a><br/>
        <a href="/api/v1.0/stations">Stations</a><br/>
        <a href="/api/v1.0/tobs">tobs</a><br/>
        <form action="/api/v1.0/start/" method="get">
            Start Date: <input type="text" id="start_date" name="start_date" placeholder="YYYY-MM-DD" required><br>
            End Date: <input type="text" id="end_date" name="end_date" placeholder="YYYY-MM-DD"><br>
            <input type="submit" value="Submit">
        </form>
        <br/>
        /api/v1.0/start/&lt;start_date&gt;<br/>
        /api/v1.0/start/&lt;start_date&gt;/end/&lt;end_date&gt;<br/>
        ---Insert start and end dates in YYYY-MM-DD format<br/>
    """


# precipitation route that returns key:value date:precipitation only for the prior year
@app.route("/api/v1.0/precipitation")
def precipitation():
    rows = s.query(M.date, M.prcp).filter(M.date >= year_prior).order_by(M.date).all()
    precip = {_.date: _.prcp for _ in rows}
    s.close()
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
    s.close()
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
    s.close()
    return jsonify(mas)


# dynamic date routes
# function to format datetime from a string
def time(date_string):
    return dt.datetime.strptime(date_string, "%Y-%m-%d")


# function to return min, max, average temperatures
def time_stats(query):
    min_temp, max_temp, avg_temp = query[0]
    return {"min_temp": min_temp, "max_temp": max_temp, "avg_temp": avg_temp}

# two routes to return a JSON list of the min, average, and max temp for a specified start, or start-end range
# use default value to combine both routes into one query
@app.route("/api/v1.0/start/<start_date>")
@app.route("/api/v1.0/start/<start_date>/end/<end_date>")
def dates(start_date, end_date='2017-08-23'):
    start = time(start_date)
    end = time(end_date)
    results = time_stats(
        s.query(func.min(M.tobs), func.max(M.tobs), func.avg(M.tobs))
        .filter((M.date >= start_date) & (M.date <= end_date))
    )
    results["start_date"] = start
    results["end_date"] = end
    s.close()
    return jsonify(results)


# close session, in case it wasn't already done
s.close()

# run file
if __name__ == "__main__":
    app.run()
