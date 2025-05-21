# GF22 GPS Tracker Web Service

A web service for receiving, storing, and visualizing location data from GF22 GPS trackers in real-time.

## Features

- Receives location data from GF22 GPS trackers via HTTP GET/POST requests
- Stores location data in a database (SQLite for development, PostgreSQL for production)
- Visualizes tracker locations on an interactive map using Leaflet.js
- Provides a REST API for accessing location data
- Auto-refreshes map data every 5 minutes
- Supports filtering by IMEI and limiting the number of points displayed

## Quick Start

### Prerequisites

- Python 3.6+
- pip (Python package manager)
- A publicly accessible server with port 80 open (for production)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/gf22-tracker.git
   cd gf22-tracker
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application (development mode):
   ```
   python app.py
   ```

   The application will be available at http://localhost:5000

### Production Deployment

For production deployment, it's recommended to:

1. Use PostgreSQL instead of SQLite:
   ```
   export DATABASE_URL=postgresql://username:password@localhost/tracker_db
   ```

2. Use a production WSGI server:
   ```
   gunicorn -w 4 -b 0.0.0.0:80 app:app
   ```

3. Set up HTTPS using a reverse proxy like Nginx with Let's Encrypt

### Deploying to VPS Server

This project includes a deployment script for a specific VPS server with the following IP addresses:
- IPv4: 109.73.194.53
- IPv6: 2a03:6f00:a::cb68

To deploy to this server:

1. Copy the project files to the server:
   ```
   scp -r ./* user@109.73.194.53:/path/to/deployment/
   ```

2. SSH into the server:
   ```
   ssh user@109.73.194.53
   ```

3. Navigate to the deployment directory:
   ```
   cd /path/to/deployment/
   ```

4. Run the deployment script as root:
   ```
   sudo ./deploy.sh
   ```

   If you need to redeploy and want to recreate the database:
   ```
   sudo ./deploy.sh --drop-db
   ```

The deployment script will:
- Install required system packages (Python, PostgreSQL, Nginx)
- Set up a PostgreSQL database for the application
- Configure the application to run as a systemd service
- Set up Nginx to support both IPv4 and IPv6 access

After deployment, the application will be accessible at:
- http://109.73.194.53 (IPv4)
- http://[2a03:6f00:a::cb68] (IPv6)

## Configuring Your GF22 Tracker

To configure your GF22 tracker to send data to this service:

1. Set the master phone number (if not already done):
   ```
   000#your_phone_number#
   ```

2. Configure the server address:

   For the specific VPS server:
   ```
   Adminip#109.73.194.53#80#
   ```

   Or for a different server (replace with your actual domain/IP):
   ```
   Adminip#your.domain.com#80#
   ```

3. Enable automatic GPRS transmission:
   ```
   123#1
   ```

4. Set the transmission interval to 60 minutes:
   ```
   Time#60#
   ```

The tracker will now send location data to your server every hour.

## API Documentation

### Receiving Tracker Data

- **Endpoint**: `/update`
- **Methods**: GET, POST
- **Parameters**:
  - `imei` (required): Tracker IMEI
  - `lat` (required): Latitude
  - `lng` (required): Longitude
  - `speed` (optional): Speed in km/h
  - `ts` (required): Timestamp (format: YYYY-MM-DD HH:MM:SS)
- **Response**: 200 OK with body "OK" or 400 Bad Request with error message

### Retrieving Location Data

- **Endpoint**: `/api/locations`
- **Method**: GET
- **Parameters**:
  - `imei` (optional): Filter by tracker IMEI
  - `limit` (optional): Limit the number of results
- **Response**: JSON array of location objects:
  ```json
  [
    {
      "imei": "123456789012345",
      "lat": 56.95,
      "lng": 24.11,
      "speed": 0.0,
      "ts": "2023-05-21T14:00:00"
    },
    ...
  ]
  ```

## GF22 Tracker SMS Commands Reference

| Function | SMS Command | Example |
|----------|-------------|---------|
| Set master number | 000#<number># | 000#79991234567# |
| Record audio (10s) | 111 | — |
| Auto-record on sound (>60dB) | 222 | — |
| Voice callback on sound | 333 | — |
| Disable all functions | 555 | — |
| SMS alert on vibration | 666 | — |
| Callback on vibration | 777 | — |
| Record 10s and upload | 789 | — |
| Request coordinates (SMS) | 999 | → Location: lat, lng, ... |
| Set GPRS interval (seconds) | MD#<sec># | MD#30# |
| Set GPRS interval (minutes) | Time#<min># | Time#60# |
| Set heartbeat interval | Heartbeat#<sec># | Heartbeat#300# |
| Enable GPRS transmission | 123#1 | — |
| Disable GPRS transmission | 123#0 | — |
| Set server (IP/domain + port) | Adminip#<domain/ip>#<port># | Adminip#tracker.example.com#80# |
| Reset password | Pwrst | — |
| Factory reset | 1122 | — |
| Request IMEI | Imei# | → IMEI:XXXXXXXXXXXXX |
| Restart device | SYSRST# | — |
| Enable/disable LED | LED#on / LED#off | — |

## License

This project is licensed under the MIT License - see the LICENSE file for details.
