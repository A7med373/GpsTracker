from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# ========== Configuration ==========  
app = Flask(__name__)
# Use SQLite for development, can be changed to PostgreSQL in production
db_url = os.environ.get('DATABASE_URL', 'sqlite:///tracker.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# ========== Model ==========  
class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    imei = Column(String(32), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float)
    ts = Column(DateTime, nullable=False)

# Create tables
Base.metadata.create_all(engine)

# ========== Routes ==========
@app.route('/')
def index():
    """Render the main page with the map"""
    return render_template('index.html')

# ========== Tracker Data Reception ==========  
@app.route('/update', methods=['GET', 'POST'])
def update():
    """
    Endpoint to receive data from the GF22 tracker
    Accepts both GET and POST methods
    Required parameters: imei, lat, lng, ts
    Optional parameters: speed
    """
    data = request.values
    
    # Validate required parameters
    for key in ('imei', 'lat', 'lng', 'ts'):
        if not data.get(key):
            return f"Missing {key}", 400
    
    try:
        # Create new location record
        loc = Location(
            imei=data['imei'],
            latitude=float(data['lat']),
            longitude=float(data['lng']),
            speed=float(data.get('speed', 0)),
            ts=datetime.strptime(data['ts'], "%Y-%m-%d %H:%M:%S")
        )
        
        # Save to database
        sess = Session()
        sess.add(loc)
        sess.commit()
        sess.close()
        
        return "OK", 200
    except Exception as e:
        return f"Error: {str(e)}", 400

# ========== API for Map ==========  
@app.route('/api/locations')
def list_locations():
    """
    API endpoint to get location data for the map
    Optional parameters:
    - imei: Filter by device IMEI
    - limit: Limit the number of results (default: all)
    """
    imei = request.args.get('imei')
    limit = request.args.get('limit')
    
    sess = Session()
    query = sess.query(Location).order_by(Location.ts.desc())
    
    # Apply filters if provided
    if imei:
        query = query.filter(Location.imei == imei)
    if limit and limit.isdigit():
        query = query.limit(int(limit))
    
    # Get results
    points = query.all()
    
    # Format response
    result = [{
        'imei': p.imei,
        'lat': p.latitude,
        'lng': p.longitude,
        'speed': p.speed,
        'ts': p.ts.isoformat()
    } for p in points]
    
    sess.close()
    return jsonify(result)

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    # In production, you might want to use a proper WSGI server
    app.run(host='0.0.0.0', port=port, debug=False)