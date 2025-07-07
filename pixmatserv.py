import time
import sys
import os
import requests
import json
import datetime

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

brightness = 10
font_height = 10 # TO-DO
weather_update_frequency = 600 # In Seconds
tick_speed = 0.03 # In Seconds
blink_freq = 0.5 # In Seconds
scroll_ticks = 2
time_ranges = [
	(datetime.time(18, 0), datetime.time(22, 0)),
	(datetime.time(6, 0), datetime.time(8, 0))
]


def Do_Weather():
	get_station_url = "https://api.weather.gov/points/28.5655801,-81.3293729" # Last bit is latitude longitude
	result = requests.get(get_station_url).json()
	get_weather_url = result["properties"]["forecastHourly"]
	result = requests.get(get_weather_url).json()
	temperature = result["properties"]["periods"][0]["temperature"]
	forecast = result["properties"]["periods"][0]["shortForecast"]
	return str(temperature) + "°F " + forecast

if __name__ == "__main__":

	options = RGBMatrixOptions()
	options.rows = 64
	options.cols = 64
	options.chain_length = 1
	options.parallel = 1
	options.hardware_mapping = 'regular'
	options.brightness = brightness

	matrix = RGBMatrix(options = options)
	offscreen_canvas = matrix.CreateFrameCanvas()
	font = graphics.Font()
	font.LoadFont("./5x8.bdf")
	textColor = graphics.Color(3,252,252)
	pos = offscreen_canvas.width

	blink = False
	time_since_blink = 0
	time_since_last_weather_update = weather_update_frequency
	weather_string = ""
	scroll_countdown_pos = 0
	weather_pos = 0
	scroll_tick_counter = 0
	scroll = False

	while True:
		offscreen_canvas.Clear()

		# Check if running time
		now = datetime.datetime.now().time()

		draw = False
		for start, end in time_ranges:
			if start <= now and now <= end:
				draw = True

		if not draw:
			offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
			continue

		# Handle Scroll Logic
		if scroll_tick_counter >= scroll_ticks:
			scroll_tick_counter = 0
			scroll = True
		else:
			scroll = False


		# Date / Time
		if blink:
			time_string = datetime.datetime.now().strftime("%I %M %p")
		else:
			time_string = datetime.datetime.now().strftime("%I:%M %p")

		if time_since_blink >= blink_freq:
			blink = not blink
			time_since_blink = 0

		time_since_blink += tick_speed

		date_string = datetime.datetime.now().strftime("%m/%d/%y")
		len = graphics.DrawText(offscreen_canvas, font, 3, 10, textColor, time_string)
		graphics.DrawText(offscreen_canvas, font, 3, 20, textColor, date_string)

		# Handle Weather
		if (time_since_last_weather_update >= weather_update_frequency):
			weather_string = Do_Weather()
			time_since_last_weather_update = 0

		len = graphics.DrawText(offscreen_canvas, font, weather_pos, 36, textColor, weather_string)

		if scroll:
			weather_pos -= 1

		if (weather_pos + len < 0):
			weather_pos = offscreen_canvas.width

		time_since_last_weather_update += tick_speed

		# Days till wedding
		today = datetime.date.today()
		big_day = datetime.date(2025, 10, 11)
		diff = big_day - today
		print_string = str(diff.days) + " Days Till Wedding!!"
		len = graphics.DrawText(offscreen_canvas, font, scroll_countdown_pos, 52, textColor, print_string)

		if scroll:
			scroll_countdown_pos -= 1

		if (scroll_countdown_pos + len < 0):
			scroll_countdown_pos = offscreen_canvas.width

		scroll_tick_counter = scroll_tick_counter + 1
		time.sleep(tick_speed)
		offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
