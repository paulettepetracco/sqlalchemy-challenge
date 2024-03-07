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

latest_date = session.query(func.max(Measurement.date)).scalar()
latest_date = dt.datetime.strptime(latest_date,'%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
one_year_ago = latest_date - dt.timedelta(days=365)


@app.route("/")
def welcome():
    """List all available api routes"""
    return(
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session=Session(engine)
    
    

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= one_year_ago).filter(Measurement.date <= latest_date)\
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
    
    
    station_names = session.query(Station.station).distinct().all()
    all_names = list(np.ravel(station_names))
    
    session.close()
    
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    
    twelve_month_temps = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= one_year_ago).all()
    
    all_tobs = list(np.ravel(twelve_month_temps))
    
    session.close()
    
    return jsonify(all_tobs)
    
if __name__ == '__main__':
    app.run(debug=True)
