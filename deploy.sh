#!/bin/bash
# Deployment script for GF22 GPS Tracker web service on VPS server
# Server details:
# - IPv4: 109.73.194.53
# - IPv6: 2a03:6f00:a::cb68

set -e  # Exit on error

# Parse command line arguments
DROP_DB=false
for arg in "$@"; do
    case $arg in
        --drop-db)
            DROP_DB=true
            shift
            ;;
    esac
done

echo "Deploying GF22 GPS Tracker web service to VPS..."

# Check if running as root (needed for port 80)
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root to bind to port 80"
    exit 1
fi

# Install required system packages
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip postgresql postgresql-contrib nginx

# Ensure netstat is available for port checking
if ! command -v netstat &> /dev/null; then
    echo "Installing net-tools for netstat command..."
    apt-get install -y net-tools
fi

# Create PostgreSQL database and user
echo "Setting up PostgreSQL database..."

# Check if database exists
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='tracker_db'")

if [ "$DB_EXISTS" = "1" ]; then
    if [ "$DROP_DB" = true ]; then
        echo "Database 'tracker_db' already exists. Dropping it as requested..."
        sudo -u postgres psql -c "DROP DATABASE tracker_db;"
        echo "Creating new database 'tracker_db'..."
        sudo -u postgres psql -c "CREATE DATABASE tracker_db;"
    else
        echo "Database 'tracker_db' already exists. Skipping database creation."
        echo "Use --drop-db option to drop and recreate the database."
    fi
else
    echo "Creating database 'tracker_db'..."
    sudo -u postgres psql -c "CREATE DATABASE tracker_db;"
fi

# Check if user exists
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='tracker_user'")

if [ "$USER_EXISTS" = "1" ]; then
    echo "User 'tracker_user' already exists. Skipping user creation."
else
    echo "Creating user 'tracker_user'..."
    sudo -u postgres psql -c "CREATE USER tracker_user WITH PASSWORD 'your_secure_password';"
fi

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tracker_db TO tracker_user;"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://tracker_user:your_secure_password@localhost/tracker_db"
export PORT=8000

# Create a systemd service file
echo "Creating systemd service..."
cat > /etc/systemd/system/gps-tracker.service << EOF
[Unit]
Description=GF22 GPS Tracker Web Service
After=network.target postgresql.service

[Service]
User=root
WorkingDirectory=$(pwd)
Environment="DATABASE_URL=postgresql://tracker_user:your_secure_password@localhost/tracker_db"
ExecStart=$(which gunicorn) --workers 4 --bind 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "Starting the service..."
systemctl daemon-reload
systemctl enable gps-tracker
systemctl start gps-tracker

# Check if port 80 is in use
echo "Checking if port 80 is already in use..."
if netstat -tuln | grep -q ":80 "; then
    echo "Warning: Port 80 is already in use. Attempting to stop conflicting services..."
    # Try to identify and stop the service using port 80
    if systemctl is-active --quiet apache2; then
        echo "Stopping Apache2 service..."
        systemctl stop apache2
    fi

    # Check again if port is still in use
    if netstat -tuln | grep -q ":80 "; then
        echo "Port 80 is still in use. Please manually stop the service using this port and run the script again."
        echo "You can use 'sudo netstat -tulnp | grep :80' to identify the process."
        exit 1
    fi
fi

# Configure Nginx for IPv6 support
echo "Configuring Nginx for IPv6 support..."
# Remove default Nginx site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "Removing default Nginx site..."
    rm -f /etc/nginx/sites-enabled/default
fi

# Stop Nginx if it's running
if systemctl is-active --quiet nginx; then
    echo "Stopping Nginx service..."
    systemctl stop nginx
fi

cat > /etc/nginx/sites-available/gps-tracker << EOF
server {
    listen 80;
    listen [::]:80;
    server_name 109.73.194.53 2a03:6f00:a::cb68;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable the Nginx site
ln -sf /etc/nginx/sites-available/gps-tracker /etc/nginx/sites-enabled/

# Start Nginx
echo "Starting Nginx service..."
systemctl start nginx || {
    echo "Failed to start Nginx. Checking for errors..."
    nginx -t
    echo "Port 80 usage:"
    netstat -tulnp | grep :80
    exit 1
}

echo "Deployment completed successfully!"
echo "The GPS tracker service is now running on:"
echo "- IPv4: http://109.73.194.53"
echo "- IPv6: http://[2a03:6f00:a::cb68]"
echo ""
echo "To configure your GF22 tracker, send the following SMS commands:"
echo "1. Set master phone number: 000#your_phone_number#"
echo "2. Configure server address: Adminip#109.73.194.53#80#"
echo "3. Enable automatic GPRS transmission: 123#1"
echo "4. Set transmission interval to 60 minutes: Time#60#"
echo ""
echo "Troubleshooting:"
echo "- If you encounter issues, check the service status: systemctl status gps-tracker"
echo "- Check Nginx status: systemctl status nginx"
echo "- View application logs: journalctl -u gps-tracker"
echo "- View Nginx logs: tail -f /var/log/nginx/error.log"
echo "- If port 80 is in use, identify the process: netstat -tulnp | grep :80"
