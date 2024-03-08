# Import the dependencies.
import numpy as np
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
# Query to retrieve the last 12 months of precipitation data
latest_date = session.query(func.max(Measurement.date)).scalar()
latest_date_formatted= dt.datetime.strptime(latest_date,'%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
one_year_ago = latest_date_formatted - dt.timedelta(days=365)

# Routes for Climate App
@app.route("/")
def welcome():
    """List all available api routes"""
    return(
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23<br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session=Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= one_year_ago).filter(Measurement.date <= latest_date_formatted)\
    .order_by(Measurement.date).all()
    
    session.close()
    
    precipitation_by_date = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation_by_date.append(precipitation_dict)
        
    
    return jsonify(precipitation_by_date)    


@app.route("/api/v1.0/stations")
def stations():
    
    session=Session(engine)    
    # Create a query that returns data for all of the stations
    station_names = session.query(Station.station).distinct().all()
    all_names = list(np.ravel(station_names))
    
    session.close()
    
    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    # Query the last 12 months of temperature observation data for the most active station
    twelve_month_temps = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= one_year_ago).all()
    
    all_tobs = list(np.ravel(twelve_month_temps))
    
    session.close()
    
    return jsonify(all_tobs)

@app.route("/api/v1.0/<date>")
def start(date):
    session = Session(engine)
    # Query to calculate the min, max and avg temp from start date
    start_date = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date>=date).all()
        
    start_date_temps = list(np.ravel(start_date))
    
    session.close()
    
    return jsonify(start_date_temps)

@app.route("/api/v1.0/<start>/<end>")
def range(start,end):
    session = Session(engine)
    # Query to calculate the min, max and avg temp from date range
    date_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date>=start).filter(Measurement.date<=end).all()
    
    one_year_temps = list(np.ravel(date_range))
    
    session.close()
    
    return jsonify(one_year_temps)
    
    
if __name__ == '__main__':
    app.run(debug=True)
