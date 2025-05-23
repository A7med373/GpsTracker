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

   The script includes troubleshooting information if you encounter any issues during deployment.

### Troubleshooting 502 Bad Gateway Errors

If you encounter a "502 Bad Gateway" error after deployment, it typically means that Nginx cannot communicate with the Gunicorn application server. Here are steps to diagnose and fix the issue:

1. Check if the Gunicorn service is running:
   ```
   sudo systemctl status gps-tracker
   ```

2. If the service is not running, start it:
   ```
   sudo systemctl start gps-tracker
   ```

3. Check the Gunicorn error logs for application errors:
   ```
   sudo tail -f /var/log/gunicorn-error.log
   ```

4. Test if Gunicorn is accessible directly:
   ```
   curl -v http://127.0.0.1:8000/
   ```

5. Check Nginx error logs:
   ```
   sudo tail -f /var/log/nginx/error.log
   ```

6. Ensure firewall is not blocking communication:
   ```
   sudo ufw status
   ```

7. If using SELinux, check if it's blocking communication:
   ```
   sudo sestatus
   ```

   If SELinux is enabled, allow Nginx to connect to network:
   ```
   sudo setsebool -P httpd_can_network_connect 1
   ```

8. Restart both services:
   ```
   sudo systemctl restart gps-tracker
   sudo systemctl restart nginx
   ```

### Troubleshooting API and Database Issues

If you encounter issues with the API endpoints or database connectivity, the application includes several features to help diagnose and resolve problems:

1. **Health Check Endpoint**: Use the `/api/health` endpoint to check if the application and database are functioning correctly:
   ```
   curl http://your-server/api/health
   ```
   This will return a JSON response with the status of the application and database connection.

2. **Detailed Error Responses**: API endpoints now return detailed error messages with appropriate HTTP status codes:
   - 400 Bad Request: Missing or invalid parameters
   - 500 Internal Server Error: Database or server errors

3. **Comprehensive Logging**: The application now includes comprehensive logging to help diagnose issues:
   - Application startup and configuration
   - Database connection and initialization
   - API requests and responses
   - Database operations
   - Error details with stack traces

4. **Accessing Logs**: You can access the application logs to diagnose issues:
   ```
   # View application logs
   sudo tail -f /path/to/app.log

   # View Gunicorn error logs (in production)
   sudo tail -f /var/log/gunicorn-error.log
   ```

5. **Frontend Error Display**: The web interface now displays more detailed error messages when API requests fail, helping users understand what went wrong.

6. **Database Session Management**: The application now ensures that database sessions are properly closed, even in error cases, to prevent resource leaks.

### Common Issues and Solutions

#### "Error loading tracker data: HTTP error! Status: 500"

If you see this error on the main page:

1. **Check the database connection**:
   - Use the `/api/health` endpoint to verify the database is connected
   - If the database shows as "connected", the issue may be with the query or data processing

2. **Check for data in the database**:
   - If the database is empty, you need to send some location updates first
   - Use the test form at `/test` or the test script to add sample data

3. **Check the application logs**:
   - Look for error messages related to the `/api/locations` endpoint
   - Database query errors or data format issues will be logged

#### "Missing imei" when accessing /update

This error occurs when you access the `/update` endpoint without providing all required parameters:

1. **Use the test form**:
   - Navigate to `/test` in your browser to use a form with all required fields

2. **Include all required parameters**:
   - The `/update` endpoint requires: `imei`, `lat`, `lng`, and `ts`
   - Example: `/update?imei=861261027896790&lat=56.95&lng=24.11&ts=2025-05-21%2014:00:00`

3. **Check parameter format**:
   - The timestamp (`ts`) must be in the format: `YYYY-MM-DD HH:MM:SS`
   - Latitude and longitude must be valid numbers

#### No Data Showing on Map

If the map loads but no tracker data is displayed:

1. **Add sample data first**:
   - Use the test form at `/test` or the test script to add location data
   - The map can only display data that has been sent to the `/update` endpoint
   - Use the included sample data generator script:
     ```
     ./add_sample_data.py --url http://your-server
     ```

2. **Check the browser console**:
   - Open your browser's developer tools (F12) and check the console for errors
   - Network errors or JavaScript issues will be displayed here

3. **Try refreshing the data**:
   - Click the "Refresh Data" button on the map
   - Check the browser console for any errors during the refresh

### Sample Data Generator

The project includes a script to quickly generate sample location data:

```
./add_sample_data.py [options]
```

Options:
- `--url URL`: URL of the tracker service (default: http://localhost:5000)
- `--imei IMEI`: IMEI of the tracker (default: 861261027896790)
- `--points N`: Number of sample points to add (default: 5)

This script will:
1. Generate random location points in Europe
2. Create points at 1-hour intervals starting from 24 hours ago
3. Send each point to the `/update` endpoint
4. Display the server's response for each point

Example:
```
./add_sample_data.py --url http://your-server --points 10
```

After running the script, you can view the data on the map by visiting the main page.

The deployment script will:
- Install required system packages (Python, PostgreSQL, Nginx)
- Set up a PostgreSQL database for the application
- Configure the application to run as a systemd service with Gunicorn on port 8000
- Check for and resolve port 80 conflicts (stopping conflicting services if necessary)
- Set up Nginx as a reverse proxy to forward requests from port 80 to Gunicorn on port 8000
- Configure Nginx to support both IPv4 and IPv6 access

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
- **Response**: 
  - 200 OK with body "OK" on success
  - 400 Bad Request with error message if parameters are missing or invalid
  - 500 Internal Server Error with error message if a database error occurs

#### Testing the Update Endpoint

You can test the `/update` endpoint in several ways:

1. **Using the Test Form**:
   - Navigate to `/test` in your browser
   - Fill in the required fields (IMEI, latitude, longitude, timestamp)
   - Click "Send Location Update"
   - The form will display the server's response

2. **Using the Test Script**:
   ```
   ./test_tracker.py --url http://your-server
   ```
   This will simulate a tracker sending multiple location updates.

3. **Manual URL Construction**:
   ```
   http://your-server/update?imei=861261027896790&lat=56.95&lng=24.11&speed=0&ts=2025-05-21%2014:00:00
   ```
   Note that all parameters must be properly URL-encoded.

If you receive a "Missing imei" (or similar) error, it means you haven't provided all the required parameters in your request.

### Retrieving Location Data

- **Endpoint**: `/api/locations`
- **Method**: GET
- **Parameters**:
  - `imei` (optional): Filter by tracker IMEI
  - `limit` (optional): Limit the number of results
- **Response**: 
  - Success: JSON array of location objects:
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
  - Error: JSON object with error details:
    ```json
    {
      "error": "Database error",
      "message": "Error details..."
    }
    ```

### Health Check

- **Endpoint**: `/api/health`
- **Method**: GET
- **Description**: Checks the health of the application and database connection
- **Response**: JSON object with health status:
  ```json
  {
    "status": "ok",
    "timestamp": "2023-05-21T14:00:00.123456",
    "database": "connected"
  }
  ```
  If there's a database error:
  ```json
  {
    "status": "ok",
    "timestamp": "2023-05-21T14:00:00.123456",
    "database": "error",
    "error": "Error details..."
  }
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
