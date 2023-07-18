# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    '''List all available api routes.'''
    return (
        f"Available Routes:<br/><br/>"
        f"&emsp;/api/v1.0/precipitation<br/><br/>"
        f"&emsp;/api/v1.0/stations<br/><br/>"
        f"&emsp;/api/v1.0/tobs<br/><br/>"
        f"&emsp;/api/v1.0/start<br/>"
        f"&emsp;&emsp;For a specified start date: replace 'start' with a date in the format YYYY-MM-DD.<br/><br/>"
        f"&emsp;/api/v1.0/start/end<br/>"
        f"&emsp;&emsp;For a specified start date: replace 'start' with a date in the format YYYY-MM-DD.<br/>"
        f"&emsp;&emsp;For a specified end date: replace 'end' with a date in the format YYYY-MM-DD.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    '''returns the jsonified precipitation data for the last year in the database'''

    # create session from python to DB
    session = Session(engine)

    # Perform a query to retrieve most active station
    max_station = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()

    # Perform a query to retrieve max date
    max_date = session.query(func.max(measurement.date)).all()

    # Calculate 1 year from max date
    for row in max_date:
        new_date = dt.datetime.strptime(row[0], '%Y-%m-%d').date() - dt.timedelta(days=365)

    # Perform a query to retrieve the data
    summary_list = []
    tobs_scores = session.query(measurement.date, measurement.tobs).filter(measurement.date >= new_date).filter(measurement.station == max_station[0]).all()

    session.close()

    for i,row in enumerate(tobs_scores):
        date = tobs_scores[i][0]
        temp = tobs_scores[i][1]
        summary_dict = {
            date: temp
        }
        summary_list.append(summary_dict)
    return jsonify(summary_list)  

@app.route("/api/v1.0/stations")
def stations():
    '''returns all of the stations in the database'''

    # create session from python to DB
    session = Session(engine)

    # Perform a query to retrieve all stations in database
    summary_list = []
    stations = session.query(measurement.station).distinct()

    session.close()

    for row in stations:
        station = row[0]
        summary_dict = {
            'station': station
        }
        summary_list.append(summary_dict)
    return jsonify(summary_list)    

@app.route("/api/v1.0/tobs")
def tobs():
    '''returns the most active station for the last year of data'''

    # create session from python to DB
    session = Session(engine)

    # Perform a query to retrieve most active station
    max_station = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()

    # Perform a query to retrieve max date
    max_date = session.query(func.max(measurement.date)).all()

    # Calculate 1 year from max date
    for row in max_date:
        new_date = dt.datetime.strptime(row[0], '%Y-%m-%d').date() - dt.timedelta(days=365)

    # Perform a query to retrieve data
    tobs_scores = session.query(measurement.station, measurement.date, measurement.tobs).filter(measurement.date >= new_date).filter(measurement.station == max_station[0]).all()

    session.close()

    summary_list = []
    for row in tobs_scores:
        station = row[0]
        date = row[1]
        prcp = row[2]
        summary_dict = {
            'station': station,
            'date': date,
            'temperature': prcp
        }
        summary_list.append(summary_dict)
    return jsonify(summary_list)

@app.route("/api/v1.0/<start>")
def date_start(start):
    '''Returns the min, max, and average temperatures calculated from the given start date'''

    # create session from python to DB
    session = Session(engine)

    # Perform a query to retrieve most active station
    max_station = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()

    # Convert str date into date
    new_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # Perform a query to retrieve data
    tobs_scores = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= new_date).filter(measurement.station == max_station[0]).all()

    session.close()

    summary_list = []
    for row in tobs_scores:
        tmin = row[0]
        tmax = row[1]
        tavg = row[2]
        summary_dict = {
            'TMIN': tmin,
            'TAVG': tavg,
            'TMAX': tmax
        }
        summary_list.append(summary_dict)
    return jsonify(summary_list)

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start,end):
    '''Returns the min, max, and average temperatures calculated from the given start date to the given end date'''

    # create session from python to DB
    session = Session(engine)

    # Perform a query to retrieve most active station
    max_station = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()

    # Convert str date into date
    new_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    max_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # Perform a query to retrieve data
    tobs_scores = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= new_date).filter(measurement.date <= max_date).filter(measurement.station == max_station[0]).all()

    session.close()

    summary_list = []
    for row in tobs_scores:
        tmin = row[0]
        tmax = row[1]
        tavg = row[2]
        summary_dict = {
            'TMIN': tmin,
            'TAVG': tavg,
            'TMAX': tmax
        }
        summary_list.append(summary_dict)
    return jsonify(summary_list)

if __name__=="__main__":
    app.run(debug=True)