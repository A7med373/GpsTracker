#!/usr/bin/env python3
"""
Test script to simulate a GF22 GPS tracker sending data to the web service.
This script sends a test location update to the /update endpoint.
"""

import requests
import datetime
import argparse
import random
import time

def send_location_update(url, imei, lat, lng, speed=0, timestamp=None):
    """Send a location update to the tracker service."""
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    params = {
        'imei': imei,
        'lat': lat,
        'lng': lng,
        'speed': speed,
        'ts': timestamp
    }
    
    try:
        response = requests.get(f"{url}/update", params=params)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending update: {e}")
        return False

def simulate_movement(url, imei, start_lat, start_lng, num_points=5, interval=5):
    """Simulate movement by sending multiple location updates."""
    lat, lng = start_lat, start_lng
    
    for i in range(num_points):
        # Add some random movement
        lat += random.uniform(-0.001, 0.001)
        lng += random.uniform(-0.001, 0.001)
        speed = random.uniform(0, 60)  # Random speed between 0-60 km/h
        
        print(f"\nSending point {i+1}/{num_points}:")
        print(f"IMEI: {imei}")
        print(f"Latitude: {lat}")
        print(f"Longitude: {lng}")
        print(f"Speed: {speed} km/h")
        
        success = send_location_update(url, imei, lat, lng, speed)
        
        if not success:
            print("Failed to send update. Stopping simulation.")
            break
            
        if i < num_points - 1:
            print(f"Waiting {interval} seconds before sending next point...")
            time.sleep(interval)
    
    print("\nSimulation completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the GF22 GPS Tracker web service")
    parser.add_argument("--url", default="http://localhost:5000", help="URL of the tracker service")
    parser.add_argument("--imei", default="861261027896790", help="IMEI of the tracker")
    parser.add_argument("--lat", type=float, default=56.95, help="Starting latitude")
    parser.add_argument("--lng", type=float, default=24.11, help="Starting longitude")
    parser.add_argument("--points", type=int, default=5, help="Number of points to simulate")
    parser.add_argument("--interval", type=int, default=5, help="Interval between points in seconds")
    
    args = parser.parse_args()
    
    print("GF22 GPS Tracker Test Script")
    print("===========================")
    print(f"Service URL: {args.url}")
    print(f"Tracker IMEI: {args.imei}")
    print(f"Starting position: {args.lat}, {args.lng}")
    print(f"Simulating {args.points} points with {args.interval}s interval")
    print("===========================\n")
    
    simulate_movement(args.url, args.imei, args.lat, args.lng, args.points, args.interval)