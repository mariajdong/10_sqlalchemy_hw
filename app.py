#json & flask dependencies
import requests
import json
import base64
from flask import Flask, jsonify

#SQLalchemy & ORM dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#datetime & numpy imports
import datetime as dt
import numpy as np

#create flask app
app = Flask(__name__)

#create engine to connect to sqlite file
engine = create_engine ("sqlite:///resources/hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()
Base.prepare (engine, reflect = True)

#save references to each table
meas = Base.classes.measurement
statn = Base.classes.station

#create session from python to database
session = Session (bind = engine)

#find most recent date in dataset
last_date = session.query (meas.date).order_by (meas.date.desc()).first()[0]

#convert date to datetime format, calculate one year (365 days) prior to last day, reformat
last_date_fm = dt.datetime.strptime (last_date, '%Y-%m-%d')
first_date_fm = last_date_fm - dt.timedelta (days = 365)
first_date = first_date_fm.strftime ('%Y-%m-%d')

#close session
session.close()

@app.route ('/')
def home():

    #home page text
	return f"""<h1>welcome to the home page!</h1>
    <h3>available routes:</h3>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/&lt;start&gt; <br>
    /api/v1.0/&lt;start&gt;/&lt;end&gt;
    """

@app.route ('/api/v1.0/precipitation')
def prcp():
    """precipitation data for last year"""

    session = Session (bind = engine)

    #query data, filter dates only from last year
    prcp_data = session.query (meas.date, meas.prcp).filter (meas.date >= first_date).all()

    #loop to populate dict
    prcp_dict = {}
    for row in prcp_data:
        prcp_dict[row[0]] = row[1]

    #return jsonified data
    return jsonify (prcp_dict)

    session.close()

@app.route ('/api/v1.0/stations')
def statn_names():
    """list of weather station IDs & names"""

    session = Session (bind = engine)

    #query data, pull list of station names
    statn_data = session.query (statn.station, statn.name).all()

    #return jsonified data
    return jsonify (statn_data)

    session.close()

@app.route ('/api/v1.0/tobs')
def tobs():
    """temperatures from last year pulled by most active weather station"""

    session = Session (bind = engine)

    #query data, pull temps from last year by top station
    recent_temps = session.query (meas.date, meas.tobs).\
                                  filter (meas.date >= first_date).\
                                  filter_by (station = "USC00519281").all()
    
    #jsonify response
    return jsonify (recent_temps)

    session.close()

@app.route ('/api/v1.0/<start>')
def start_temp(start):
    """pulls minimum, maximum, & average temps from specified start date to most recent date"""

    session = Session (bind = engine)

    #query data for min, max, avg temps after start date
    start_temps = session.query (func.min(meas.tobs), func.max(meas.tobs), func.avg(meas.tobs)).\
                                 filter (meas.date >= start).all()

    #jsonify response
    return jsonify (start_temps)

    session.close()

@app.route ('/api/v1.0/<start>/<end>')
def start_end_temps(start, end):
    """pulls minimum, maximum, & average temps from specified start & end dates"""

    session = Session (bind = engine)

    #query data for min, max, avg temps during start/end period
    start_end_temps = session.query (func.min(meas.tobs), func.max(meas.tobs), func.avg(meas.tobs)).\
                                     filter (meas.date >= start).\
                                     filter (meas.date <= end).all()
    
    #jsonify response
    return jsonify (start_end_temps)

    session.close()

#run app
if __name__ == '__main__':
    app.run(debug=True)
