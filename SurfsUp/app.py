# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
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
def home():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d').date()
    year_ago = recent_date - dt.timedelta(days = 366)
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_ago)
    session.close()

    precip_info  = []
    for date, prcp in precip_data:
        passenger_dict = {}
        passenger_dict["date"] = date
        passenger_dict["prcp"] = prcp
        precip_info.append(passenger_dict)
    return jsonify(precip_info)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station, Station.name).all()
    stations_list = [{"Station ID": station, "Station Name":name} for station, name in stations]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d').date()
    year_ago = recent_date - dt.timedelta(days = 366)
    station_count_first = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()[0]
    temperature_data = session.query(Measurement.tobs, Measurement.date).\
    filter(Measurement.station == station_count_first).\
    filter(Measurement.date > year_ago).all()
    session.close()

    tobs_list = [{"Temperature":temps, "Date":date} for temps, date in temperature_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    sel = [
    func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)
    ]
    total_info = session.query(*sel).\
        filter(Measurement.date >= start).all()
    session.close()

    total_list = [{"Min Temp":TMIN, "Max Temp":TMAX, "Avg Temp":TAVG} for TMIN, TMAX, TAVG in total_info]
    return jsonify(total_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    sel = [
    func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)
    ]
    total_info = session.query(*sel).\
        filter(Measurement.date >= start, Measurement.date <=end).all()
    session.close()

    total_list = [{"Min Temp":TMIN, "Max Temp":TMAX, "Avg Temp":TAVG} for TMIN, TMAX, TAVG in total_info]
    return jsonify(total_list)

if __name__ == '__main__':
    app.run(debug=True)