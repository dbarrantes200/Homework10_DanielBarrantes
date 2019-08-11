# import numpy, sqlachemy, flask
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,and_, extract
from flask import Flask, jsonify
import datetime as dt
import pandas as pd


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;End&gt;<br/>"
        
    )
#########################################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary  using date as the key and prcp as the value."""
    # Query all precipitation for the year 
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    sel = [Measurement.date, 
       func.sum(Measurement.prcp)]

    results = session.query(*sel).filter(and_(func.date(Measurement.date) >= year_ago),\
    func.date(Measurement.date) <= 'latest_date').group_by(Measurement.date).order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a precipitation records for the dates in analysis
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)
  
   # Return a JSON list of stations from the dataset.
#########################################################################################
@app.route("/api/v1.0/stations")
def names():
    """Return a list of all station names"""
    # Query all stations
    session = Session(engine)
    results = session.query(Station.station ).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)
#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#    * Query for the dates and temperature observations from the last year.
#           
#           
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)


#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):

 # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date. 
    session = Session(engine)
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.    
    session = Session(engine)
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################    
  
if __name__ == '__main__':
    app.run(debug=True)


