# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
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
    """)

# precipitation route that returns key:value date:precipitation only for the prior year
@app.route('/api/v1.0/precipitation')
def precipitation():
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rows = s.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_prior).all()
    precip = [{'date': _.date, 'precipitation': _.prcp} for _ in rows]
    return jsonify(precip)

# station route that returns JSONs of precipitation for the last year

# tobs route for most active station 'USC00519281', returns JSON for prior year

# dynamic date routes
    #start route take start date and returns min, max, avg from start date to last date
    
    #start/end route, returns min, max, avg temperatres

s.close()

# run file
if __name__ == '__main__':
    app.run()