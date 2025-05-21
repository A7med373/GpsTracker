#!/usr/bin/env python3
"""
Script to add sample data to the GF22 GPS Tracker database.
This script adds several sample location points to help users get started.
"""

import requests
import datetime
import argparse
import time
import random

def add_sample_data(url, imei, num_points=5):
    """Add sample location data to the tracker database."""
    print(f"Adding {num_points} sample location points for IMEI: {imei}")
    
    # Base coordinates (roughly center of Europe)
    base_lat = 50.0
    base_lng = 10.0
    
    # Time interval between points (in hours)
    time_interval = 1
    
    # Start time (24 hours ago)
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(hours=num_points * time_interval)
    
    success_count = 0
    
    for i in range(num_points):
        # Calculate time for this point
        point_time = start_time + datetime.timedelta(hours=i * time_interval)
        timestamp = point_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate coordinates with some randomness
        lat = base_lat + random.uniform(-1.0, 1.0)
        lng = base_lng + random.uniform(-1.0, 1.0)
        speed = random.uniform(0, 60)  # Random speed between 0-60 km/h
        
        # Prepare parameters
        params = {
            'imei': imei,
            'lat': lat,
            'lng': lng,
            'speed': speed,
            'ts': timestamp
        }
        
        print(f"\nSending point {i+1}/{num_points}:")
        print(f"IMEI: {imei}")
        print(f"Latitude: {lat}")
        print(f"Longitude: {lng}")
        print(f"Speed: {speed} km/h")
        print(f"Time: {timestamp}")
        
        try:
            # Send request to update endpoint
            response = requests.get(f"{url}/update", params=params)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                success_count += 1
            else:
                print(f"Failed to add point {i+1}. Server returned: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error sending update: {e}")
        
        # Small delay between requests
        if i < num_points - 1:
            time.sleep(0.5)
    
    print(f"\nSample data generation completed.")
    print(f"Successfully added {success_count} out of {num_points} points.")
    
    if success_count > 0:
        print(f"\nYou can now view the data on the map at: {url}")
    else:
        print("\nNo points were added successfully. Please check the server logs for errors.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add sample data to the GF22 GPS Tracker")
    parser.add_argument("--url", default="http://localhost:5000", help="URL of the tracker service")
    parser.add_argument("--imei", default="861261027896790", help="IMEI of the tracker")
    parser.add_argument("--points", type=int, default=5, help="Number of sample points to add")
    
    args = parser.parse_args()
    
    print("GF22 GPS Tracker - Sample Data Generator")
    print("========================================")
    print(f"Service URL: {args.url}")
    print(f"Tracker IMEI: {args.imei}")
    print(f"Number of points: {args.points}")
    print("========================================\n")
    
    add_sample_data(args.url, args.imei, args.points)