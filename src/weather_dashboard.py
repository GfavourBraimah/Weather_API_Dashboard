import os
import json
import boto3
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherDashboard:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.s3_client = boto3.client('s3')

    def create_bucket_if_not_exists(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} exists")
        except:
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} created")

    def fetch_weather(self, city):
        """Fetch current weather data from OpenWeather API"""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"
        response = requests.get(url)
        return response.json()

    def fetch_forecast(self, city):
        """Fetch weather forecast data from OpenWeather API"""
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}"
        response = requests.get(url)
        return response.json()

    def save_to_s3(self, data, city):
        """Save weather data to S3"""
        try:
            file_name = f"{city}_weather.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json.dumps(data)
            )
            print(f"Successfully saved data for {city} to S3")
            return True
        except Exception as e:
            print(f"Error saving to S3: {e}")
            return False

    def plot_forecast(self, forecast_data, city):
        """Plot weather forecast data"""
        dates = [datetime.fromtimestamp(item['dt']) for item in forecast_data['list']]
        temps = [item['main']['temp'] for item in forecast_data['list']]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, temps, marker='o')
        plt.title(f"5-Day Weather Forecast for {city}")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°F)")
        plt.grid(True)
        plt.savefig(f"{city}_forecast.png")
        plt.show()

def main():
    dashboard = WeatherDashboard()
    
    # Create bucket if needed
    dashboard.create_bucket_if_not_exists()
    
    cities = ["Philadelphia", "Seattle", "New York", "Berlin", "Auckland"]
    weather_data = []

    for city in cities:
        print(f"\nFetching weather for {city}...")
        data = dashboard.fetch_weather(city)
        if data:
            weather_data.append(data)
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            
            print(f"Temperature: {temp}°F")
            print(f"Feels like: {feels_like}°F")
            print(f"Humidity: {humidity}%")
            print(f"Conditions: {description}")
            
            # Save to S3
            success = dashboard.save_to_s3(data, city)
            if success:
                print(f"Weather data for {city} saved to S3!")
            
            # Fetch and plot forecast
            forecast_data = dashboard.fetch_forecast(city)
            dashboard.plot_forecast(forecast_data, city)
        else:
            print(f"Failed to fetch weather data for {city}")

if __name__ == "__main__":
    main()