from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# ========== Configuration ==========  
app = Flask(__name__)

# Configure logging
if not app.debug:
    # Set up file handler
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    console_handler.setLevel(logging.INFO)

    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info('GPS Tracker startup')
# Use SQLite for development, can be changed to PostgreSQL in production
db_url = os.environ.get('DATABASE_URL', 'sqlite:///tracker.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.logger.info(f"Connecting to database: {db_url}")
try:
    engine = create_engine(db_url)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    app.logger.info("Database engine created successfully")
except Exception as e:
    app.logger.error(f"Error creating database engine: {str(e)}")
    raise

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
try:
    app.logger.info("Creating database tables if they don't exist")
    Base.metadata.create_all(engine)
    app.logger.info("Database tables created successfully")
except Exception as e:
    app.logger.error(f"Error creating database tables: {str(e)}")
    raise

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
    app.logger.info(f"Tracker update received: {request.method} request to /update")
    try:
        data = request.values
        app.logger.info(f"Received data: {data}")

        # Validate required parameters
        for key in ('imei', 'lat', 'lng', 'ts'):
            if not data.get(key):
                app.logger.warning(f"Missing required parameter: {key}")
                return f"Missing {key}", 400

        app.logger.info(f"Processing location update for IMEI: {data['imei']}")
        sess = Session()
        try:
            # Create new location record
            app.logger.info("Creating location record")
            try:
                loc = Location(
                    imei=data['imei'],
                    latitude=float(data['lat']),
                    longitude=float(data['lng']),
                    speed=float(data.get('speed', 0)),
                    ts=datetime.strptime(data['ts'], "%Y-%m-%d %H:%M:%S")
                )
                app.logger.info(f"Location record created: lat={loc.latitude}, lng={loc.longitude}, ts={loc.ts}")
            except ValueError as e:
                app.logger.error(f"Error parsing location data: {str(e)}")
                raise

            # Save to database
            app.logger.info("Saving location to database")
            sess.add(loc)
            sess.commit()
            app.logger.info(f"Location saved successfully with ID: {loc.id}")

            return "OK", 200
        except ValueError as e:
            app.logger.error(f"Value error in update: {str(e)}")
            return f"Error: Invalid data format - {str(e)}", 400
        except Exception as e:
            app.logger.error(f"Database error in update: {str(e)}")
            return f"Error: Database error - {str(e)}", 500
        finally:
            sess.close()
            app.logger.info("Database session closed")
    except Exception as e:
        app.logger.error(f"Unexpected error in update: {str(e)}")
        return f"Error: Server error - {str(e)}", 500

# ========== API for Map ==========  
@app.route('/api/locations')
def list_locations():
    """
    API endpoint to get location data for the map
    Optional parameters:
    - imei: Filter by device IMEI
    - limit: Limit the number of results (default: all)
    """
    app.logger.info("API request received: /api/locations")
    try:
        imei = request.args.get('imei')
        limit = request.args.get('limit')

        app.logger.info(f"Fetching locations with filters - imei: {imei}, limit: {limit}")
        sess = Session()
        try:
            query = sess.query(Location).order_by(Location.ts.desc())

            # Apply filters if provided
            if imei:
                app.logger.info(f"Filtering by IMEI: {imei}")
                query = query.filter(Location.imei == imei)
            if limit and limit.isdigit():
                app.logger.info(f"Limiting results to: {limit}")
                query = query.limit(int(limit))

            # Get results
            app.logger.info("Executing database query")
            points = query.all()
            app.logger.info(f"Query returned {len(points)} results")

            # Format response
            result = [{
                'imei': p.imei,
                'lat': p.latitude,
                'lng': p.longitude,
                'speed': p.speed,
                'ts': p.ts.isoformat()
            } for p in points]

            app.logger.info("Successfully processed /api/locations request")
            return jsonify(result)
        except Exception as e:
            app.logger.error(f"Database error in list_locations: {str(e)}")
            return jsonify({"error": "Database error", "message": str(e)}), 500
        finally:
            sess.close()
            app.logger.info("Database session closed")
    except Exception as e:
        app.logger.error(f"Unexpected error in list_locations: {str(e)}")
        return jsonify({"error": "Server error", "message": str(e)}), 500

# ========== Diagnostic Endpoints ==========
@app.route('/api/health')
def health_check():
    """
    Health check endpoint to verify the application and database are working
    """
    app.logger.info("Health check requested")
    status = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "database": "unknown"
    }

    # Check database connection
    try:
        sess = Session()
        try:
            # Try a simple query
            result = sess.execute("SELECT 1").scalar()
            if result == 1:
                status["database"] = "connected"
                app.logger.info("Database health check: OK")
            else:
                status["database"] = "error"
                app.logger.error("Database health check: Unexpected result")
        except Exception as e:
            status["database"] = "error"
            status["error"] = str(e)
            app.logger.error(f"Database health check failed: {str(e)}")
        finally:
            sess.close()
    except Exception as e:
        status["database"] = "error"
        status["error"] = str(e)
        app.logger.error(f"Database session creation failed: {str(e)}")

    return jsonify(status)

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    # In production, you might want to use a proper WSGI server
    app.run(host='0.0.0.0', port=port, debug=False)
