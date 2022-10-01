import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# 2. Create an app
app = Flask(__name__)

              
# 3. Define static routes
@app.route("/")
def index():
    
    return (
        f"<h4>List of all available api routes.</h4>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/<start></li>"
        f"<li>/api/v1.0/<start>/<end></li>"
        f"</ul>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    station_data = session.query(Station.station).all()
    session.close()
    
    station_list = list(np.ravel(station_data))
   
    return jsonify(station_list)   

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    active_station = session.query(Measurement.station\
                ).group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).first()
    active_max_date = session.query(func.max(Measurement.date),\
                ).filter(Measurement.station == active_station[0]).all()
    d2 = dt.datetime(2017, 8, 18)
    active_one_year_prior = d2 - relativedelta(years=1)  
    active_last_year = session.query(Measurement.tobs)\
                   .filter(Measurement.date >= active_one_year_prior).filter(Measurement.station == active_station[0])\
                   .order_by(Measurement.tobs.desc()).all()           
    session.close()
    
    tobs_list = list(np.ravel(active_last_year))
    
    return jsonify(tobs_list) 

@app.route("/api/v1.0/<start>")
def temperature(start):
    session = Session(engine)
    temp_lowest = session.query(func.min(Measurement.tobs),\
                ).filter(Measurement.date >= start).all()
    temp_highest = session.query(func.max(Measurement.tobs),\
                ).filter(Measurement.date >= start).all()
    temp_average = session.query(func.avg(Measurement.tobs),\
                ).filter(Measurement.date >= start).all()
    session.close()

    temp_lowest_list = list(np.ravel(temp_lowest))
    temp_highest_list = list(np.ravel(temp_highest))
    temp_average_list = list(np.ravel(temp_average))

    return (
        f"TMIN: {temp_lowest_list[0]} </br>"
        f"TMAX: {temp_highest_list[0]} </br>"
        f"TAVG: {round(temp_average_list[0],3)}"
    )

@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    session = Session(engine)
    temp_lowest = session.query(func.min(Measurement.tobs),\
                ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_highest = session.query(func.max(Measurement.tobs),\
                ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_average = session.query(func.avg(Measurement.tobs),\
                ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_lowest_list = list(np.ravel(temp_lowest))
    temp_highest_list = list(np.ravel(temp_highest))
    temp_average_list = list(np.ravel(temp_average))

    return (
        f"TMIN: {temp_lowest_list[0]} </br>"
        f"TMAX: {temp_highest_list[0]} </br>"
        f"TAVG: {round(temp_average_list[0],3)}"
    )

# 4. Define main behaviour
if __name__ == "__main__":
    app.run(debug=True)

