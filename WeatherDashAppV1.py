'''
Aavy18
Weather App Class

This project is a desktop weather app
It has the weather for today, high/low, humidity and windspeed, sunrise sunset 
it also has a forecast

The weather information comes from Open Weather Map
'''

import requests
# you can get a weather key from open weather map
from configCopy import weatherKey
import tkinter as tk
import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeatherApp:
    def __init__(self, root, loc):

        self.location = loc
        self.coords = None

        self.themes = {
            "day":      {"bg": "#87CEEB", "fg": "#1a1a2e", "card": "#6ab4d4", "text": "#1a1a2e", "btn": "#4a7ab5"},
            "twilight": {"bg": "#2d1b4e", "fg": "#ffcc88", "card": "#3d2b5e", "text": "#ffcc88", "btn": "#6b4a8a"},
            "night":    {"bg": "#1a1a2e", "fg": "#e0e0ff", "card": "#16213e", "text": "#a0a0cc", "btn": "#4a4a8a"}
        }
        self.currTheme = "night"
        init_t = self.themes[self.currTheme]

        # creates the basic widget shape/size
        self.root = root
        root.title("Weather Dashboard - " + self.location)
        root.geometry("600x810")
        root.resizable(False, False)
        root.configure(bg=init_t["bg"])

        # any other nicknames can go here
        self.nicknames = {
            "new york": "big apple",
            "jaipur": "pink city",
            "paris": "city of light",
            "chicago": "the windy city" 
        }
        # inverts the dict and gets rid of emojis
        self.searchNicknames = {}
        for city, alias in self.nicknames.items():
            search_term = alias.rsplit(' ', 1)[0].lower()
            self.searchNicknames[search_term] = city

        # makes a status bar frame for the update buttons
        self.status_bar = tk.Frame(root, bg=init_t["card"], padx=10, pady=5)
        self.status_bar.pack(fill="x", side="top")

        # makes a status bar for the warnings
        self.warning_bar = tk.Frame(root, bg=init_t["card"], padx=10, pady=5)
        self.warning_bar.pack(fill="x", side="top")


        # makes a frame
        self.frame = tk.Frame(root, padx=10, pady=10, bg=init_t["bg"])
        self.frame.pack(fill="both", expand=True)

        # adds buttons for updating and switching unites
        self.update_btn = tk.Button(self.status_bar, text="Update Weather", command=self.update_data,
                                    bg=init_t["btn"], highlightbackground=init_t["btn"], relief="flat",
                                    font=("Georgia", 11), padx=20, pady=8, cursor="hand2")
        self.update_btn.pack(side="left", pady=5)

        self.switch_F_btn = tk.Button(self.status_bar, text="Switch to °F", command=self.go_to_F,
                                        bg=init_t["btn"], highlightbackground=init_t["btn"], relief="flat",
                                        font=("Georgia", 11), padx=20, pady=8, cursor="hand2")
        self.switch_C_btn = tk.Button(self.status_bar, text="Switch to °C", command=self.go_to_C,
                                        bg=init_t["btn"], highlightbackground=init_t["btn"], relief="flat",
                                        font=("Georgia", 11), padx=20, pady=8, cursor="hand2")
        # only packs the switch to farenheit bc it inits in celsius
        self.switch_F_btn.pack(side="left", pady=5)

        # inits the data dictionaries
        self.base_data = {}
        self.display_data = {}

        self.forecast_data = []      
        self.display_forecast = []
        self.display_hourly = []
        self.hourly_data = []

        # inits dictionary of icons
        self.icons = {
        "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Snow": "❄️",
        "Thunderstorm": "⛈️", "Mist": "🌫️", "Fog": "🌫️", "Haze": "🌫️",
        "Drizzle": "🌦️", "Dust": "🌪️", "Sand": "🌪️", "Ash": "🌋",
        "Squall": "💨", "Tornado": "🌪️", "Smoke": "🌫️"
        }  

        self.search_frame = tk.Frame(self.status_bar, bg=init_t["bg"])
        self.search_frame.pack(side="right")
        
        # creates a field to enter a city
        self.city_entry = tk.Entry(self.search_frame, font=("Georgia", 11),
                            bg="#16213e", fg="white", insertbackground="white",
                            relief="flat", width=20, )
        self.city_entry.bind("<Return>", lambda _: self.set_location())
        self.city_entry.pack(side="left", padx=5, ipady=6)
        
        # creates a button that allows the entered city to be submitted
        self.change_city_btn = tk.Button(self.search_frame, text="Switch Location", command=self.set_location,
                                    bg=init_t["btn"], highlightbackground=init_t["btn"], relief="flat",
                                    font=("Georgia", 11), padx=10, pady=5, cursor="hand2")
        self.change_city_btn.pack(side="left")

        self.time_label = None

        # updates data to get accurate results
        self.update_data()
        self.update_time()

    def get_data_city(self, CITY):
        '''
        Gets the data from open weather map
        Inputs are the city
        Return is the data
        '''
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={weatherKey}&units=metric"
            resp = requests.get(url)
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {"cod": "connection_error"}
    
    def get_data_coords(self, lat, lon):
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weatherKey}&units=metric"
            resp = requests.get(url)
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {"cod": "connection_error"}
        
    def parse_data(self, data):
        '''
        This function makes our data more useful/easier to parse later by getting rid of the first keys
        The param is the data
        The return is the cleaner data
        '''
        #the cleaner data will go here
        cleanData = {}
        #the header is made for user reading, but we do not need it here
        for header in data:
            #if it is a string/number, we want to keep its header as it provideds info. 
            if not isinstance(data[header], (dict, list)):
                cleanData[header] = data[header]
            # if it is another dict, we have enough info
            else:
                #this means the value is a dict or a list
                if isinstance(data[header], list):
                    #adds each dictionary in the list to the main dict
                    for infoDict in data[header]:
                        cleanData |= infoDict
                else:
                    #adds this dict to the main dict
                    cleanData |= data[header]
        return cleanData
    
    def get_forecast_city(self, CITY):
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={weatherKey}&units=metric"
            resp = requests.get(url)
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {"cod": "connection_error"}
        
    def get_forecast_coords(self, lat, lon):
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weatherKey}&units=metric"
            resp = requests.get(url)
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {"cod": "connection_error"}
    
    def parse_forecast(self, forecastData):
        '''
        This function parses the forecast data
        param: forecast data, raw data
        returns a list of dicts about the future data
        '''
        # inits dict of days
        days = {}
        # repeates over every day in the forecast
        for entry in forecastData['list']:
            #saves the important values
            date = entry['dt_txt'].split(' ')[0]
            temp_min = entry["main"]["temp_min"]
            temp_max = entry["main"]["temp_max"]
            weather = entry["weather"][0]["main"]
            
            # sets default values if something is missing
            if date not in days:
                days[date] = {'temps_min': [], 'temps_max': [], 'weather': []}
            
            # appends to the dict
            days[date]['temps_min'].append(temp_min)
            days[date]['temps_max'].append(temp_max)
            days[date]['weather'].append(weather)

        # puts it all into a list
        forecast = []
        for date, info in days.items():
            forecast.append({
                'date': date,
                'temp_min': min(info['temps_min']),
                'temp_max': max(info['temps_max']),
                'weather': max(set(info['weather']), key=info['weather'].count)
            })
        
        return forecast
    
    def parse_hourly(self, forecastData):
        '''
        This function takes forecast data and gets the hourly prediction
        param forecast data: the data recieved from the API
        returns a list of all the hours's data 
        '''
        # inits list that will contain all the hourly data
        hourly = []

        # gets the local date (daily format)
        today = self.get_local_time().strftime('%Y-%m-%d')

        for entry in forecastData['list']:
            # gets the date
            date = entry['dt_txt'].split(' ')[0]
            if date >= today:
                # adds all the data to the list
                hourly.append({
                'time': entry['dt_txt'].split(' ')[1][:5],
                'temp': entry['main']['temp'],
                'weather': entry['weather'][0]['main'],
                'date': date
            })
        # returns the next 24 hrs of data
        return hourly[:24]

    
    def get_display_name(self):
        key = self.display_data['name'].lower()
        return self.nicknames.get(key, self.display_data['name'])

    def display(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.apply_theme()
        unit = self.display_data.get('unit', 'C')
        t = self.themes[self.currTheme]

        tk.Label(self.frame, text=f"Weather in {self.get_display_name()}, {self.display_data['country']}",
                font=("Georgia", 22, "bold"), fg=t["fg"], bg=t["bg"]).pack(pady=10)
        
        if self.coords:
            tk.Label(self.frame, text=f"{self.coords[0]:.4f}, {self.coords[1]:.4f}",
                    font=("Georgia", 11), fg=t["text"], bg=t["bg"]).pack()
        
        self.time_label = tk.Label(self.frame, text=f"{self.get_local_time().strftime('%b %d, %Y')} | {self.get_local_time().strftime('%I:%M:%S %p')}",
                font=("Georgia", 14), fg=t["fg"], bg=t["bg"])
        self.time_label.pack(pady=10)
        
        weatherType = f"{self.display_data['main'].title()}"
        tk.Label(self.frame, text=weatherType + " " + self.icons.get(weatherType, ""),
                font=("Georgia", 14), fg=t["fg"], bg=t["bg"]).pack(pady=5)
        tk.Label(self.frame, text=f"{self.display_data['temp']:.1f}°{unit}",
                font=("Georgia", 52, "bold"), fg=t["fg"], bg=t["bg"]).pack(pady=5)
        tk.Label(self.frame, text=f"Feels like: {self.display_data['feels_like']:.1f}°{unit}",
                font=("Georgia", 12), fg=t["fg"], bg=t["bg"]).pack()

        # get today's min/max from forecast data (assuming it exists)
        if self.forecast_data:
            today_min = self.display_forecast[0]['temp_min']
            today_max = self.display_forecast[0]['temp_max']
        else:
            today_min = self.display_data['temp_min']
            today_max = self.display_data['temp_max']

        hlcard = tk.Frame(self.frame, bg=t["card"], padx=20, pady=15)
        hlcard.pack(fill="x", pady=10, padx=20)
        tk.Label(hlcard, text=f"Minimum Temp: {today_min:.1f}°{unit}",
                fg=t["fg"], bg=t["card"], font=("Georgia", 12)).pack(side="left")
        tk.Label(hlcard, text=f"Maximum Temp: {today_max:.1f}°{unit}",
                fg=t["fg"], bg=t["card"], font=("Georgia", 12)).pack(side="right")

        sun_win_container_card = tk.Frame(self.frame, bg=t["bg"])
        sun_win_container_card.pack(fill="x", padx=20, pady=5)

        windcard = tk.Frame(sun_win_container_card, bg=t["card"], padx=20, pady=15, height=70)
        windcard.pack_propagate(False)
        windcard.pack(side="left", expand=True, fill="both", padx=(0, 10))
        tk.Label(windcard, text=f"Humidity: {self.display_data['humidity']}%",
                fg=t["fg"], bg=t["card"], font=("Georgia", 12)).pack(anchor="w")
        tk.Label(windcard, text=f"Wind: {self.display_data['speed']} m/s",
                fg=t["fg"], bg=t["card"], font=("Georgia", 12)).pack(anchor="w")

        suncard = tk.Frame(sun_win_container_card, bg=t["card"], padx=20, pady=15, height=70)
        suncard.pack_propagate(False)
        suncard.pack(side="right", expand=True, fill="both", padx=(10, 0))
        tk.Label(suncard, text=f"Sunrise: {self.get_sun_time('sunrise').strftime('%I:%M:%S %p')}",
                fg=t["fg"], bg=t["card"], font=("Georgia", 12)).pack(anchor="w")
        tk.Label(suncard, text=f"Sunset: {self.get_sun_time('sunset').strftime('%I:%M:%S %p')}",
                fg=t["fg"], bg=t["card"], font=("Georgia", 12)).pack(anchor="w")

        tk.Label(self.frame, text="5-Day Forecast", font=("Georgia", 14, "bold"),
                fg=t["fg"], bg=t["bg"]).pack(pady=(10, 5))

        forecast_card = tk.Frame(self.frame, bg=t["bg"])
        forecast_card.pack(fill="x", padx=20, pady=(5, 15))

        for day in self.display_forecast[1:]:
            row = tk.Frame(forecast_card, bg=t["card"], padx=10, pady=8)
            row.pack(fill="x")
            icon = self.icons.get(day['weather'], "")
            tk.Label(row, text=datetime.datetime.strptime(day['date'], '%Y-%m-%d').strftime('%b %d'),
                    bg=t["card"], fg=t["fg"], font=("Georgia", 11, "bold")).pack(side="left")
            tk.Label(row, text=day['weather'] + icon,
                    bg=t["card"], fg=t["fg"], font=("Georgia", 11)).pack(side="left", padx=20)
            tk.Label(row, text=f"{day['temp_min']:.1f}° / {day['temp_max']:.1f}°",
                    bg=t["card"], fg=t["text"], font=("Georgia", 11)).pack(side="right")
            if day != self.display_forecast[-1]:
                tk.Frame(forecast_card, bg=t["bg"], height=1).pack(fill="x", padx=5)

        self.bind_recursive(forecast_card, "<Button-1>", lambda e: self.make_forecast_graph())

        # hourly forecast section
        tk.Label(self.frame, text="Hourly Forecast", font=("Georgia", 14, "bold"),
                fg=t["fg"], bg=t["bg"]).pack(pady=(5, 5))

        hourly_container = tk.Frame(self.frame, bg=t["bg"], height=140)
        hourly_container.pack_propagate(False)
        hourly_container.pack(fill="x", padx=20, pady=(5, 15))

        hourly_canvas = tk.Canvas(hourly_container, bg=t["card"], highlightthickness=0)
        scrollbar = tk.Scrollbar(hourly_container, orient="horizontal", command=hourly_canvas.xview)
        hourly_canvas.configure(xscrollcommand=scrollbar.set)

        scrollbar.pack(side="bottom", fill="x")
        hourly_canvas.pack(side="top", fill="both", expand=True)

        # makes cards for the canvas
        hourly_frame = tk.Frame(hourly_canvas, bg=t["card"])
        hourly_canvas.create_window((0, 0), window=hourly_frame, anchor="nw")

        # repeats over every hour and displays it
        for hour in self.display_hourly:
            hourCard = tk.Frame(hourly_frame, bg=t["card"], padx=10, pady=3)
            hourCard.pack(side="left")
            icon = self.icons.get(hour['weather'], "")
            tk.Label(hourCard, text=hour['time'], bg=t["card"], fg=t["fg"], font=("Georgia", 10, "bold")).pack()
            tk.Label(hourCard, text=icon, bg=t["card"], font=("Georgia", 12)).pack()
            tk.Label(hourCard, text=f"{hour['temp']:.1f}°", bg=t["card"], fg=t["text"], font=("Georgia", 10)).pack()

        hourly_frame.update_idletasks()
        hourly_canvas.configure(scrollregion=hourly_canvas.bbox("all"))

    def is_coords(self, text):
        '''
        This function determines if the entered field is coords or a city
        param text: the text field
        returns boolean of if it is a coords
        '''
        # splits into parts
        parts = text.split(',')
        # ensures it is 2 parts n/s, and e/w
        if len(parts) == 2:
            try:
                # turns it into
                float(parts[0].strip())
                float(parts[1].strip())
                return True
            except ValueError:
                return False
        return False

    def set_location(self):
        # gets the new location from the field
        newLoc = self.city_entry.get().lower()
        if newLoc.strip():
            # sets it to either a nickname, or just what was entered
            self.location = self.searchNicknames.get(newLoc, newLoc)
            self.root.title(f"Weather Dashboard - {self.location}")
            self.update_data()
        self.city_entry.delete(0, tk.END)
    
    def update_data(self):
        # is in celsius
        self.go_to_C()
        # checks if the coords exist
        if self.is_coords(self.location):
            # finds coords
            lat, lon = [x.strip() for x in self.location.split(',')]
            data = self.parse_data(self.get_data_coords(lat, lon))
            raw_forecast = self.get_forecast_coords(lat, lon)
        else:
            data = self.parse_data(self.get_data_city(self.location))
            raw_forecast = self.get_forecast_city(self.location)


        if data.get('cod') == 'connection_error':
            self.show_connection_error()
            return
        if data.get('cod') == '404':
            self.show_city_error()
            return
        # copys that data into the base data, used for calculations
        self.base_data = data.copy()
        # uses the display data on the tkinter widget 
        self.display_data = data.copy()
        self.coords = (data['lat'], data['lon'])
        self.display_data['unit'] = 'C'

        # gets forecast and hourly data
        self.forecast_data = self.parse_forecast(raw_forecast)
        self.hourly_data = self.parse_hourly(raw_forecast)
        self.display_forecast = [day.copy() for day in self.forecast_data]
        self.display_hourly = [h.copy() for h in self.hourly_data]

        self.currTheme = self.get_theme()
        # displays the tkinter widget
        self.display()
 
    def go_to_F(self):
        self.switch_F_btn.pack_forget()
        self.switch_C_btn.pack(pady=5, side="left", before=self.search_frame)
        # checks to find if the data is related to the tempurature
        for info in self.display_data:
            if info in ('temp', 'feels_like', 'temp_min', 'temp_max'):
                # in celsius
                Ctemp = self.display_data[info]
                Ftemp = (Ctemp * 9/5) + 32
                self.display_data[info] = Ftemp
                self.display_data['unit'] = "F"
        for day in self.display_forecast:
            day['temp_min'] = (day['temp_min'] * 9/5) + 32
            day['temp_max'] = (day['temp_max'] * 9/5) + 32
        for hour in self.display_hourly:
            hour['temp'] = (hour['temp'] * 9/5) + 32
        self.display()

    def go_to_C(self):
        # checks to find if the data is related to the tempurature
        try:
            self.switch_C_btn.pack_forget()
            self.switch_F_btn.pack(pady=5, side="left", before=self.search_frame)
            for info in self.display_data:
                if info in ('temp', 'feels_like', 'temp_min', 'temp_max'):
                    #in farenheit
                    Ftemp = self.display_data[info]
                    Ctemp = (Ftemp - 32) * 5/9
                    self.display_data[info] = Ctemp
                    self.display_data['unit'] = "C"
            # does it for the forecast data
            for day in self.display_forecast:
                day['temp_min'] = (day['temp_min'] - 32) * 5/9
                day['temp_max'] = (day['temp_max'] - 32) * 5/9
            self.display_forecast = [day.copy() for day in self.forecast_data]
            self.display_hourly = [h.copy() for h in self.hourly_data]
            self.display()
        # if there is no data, we return nothing
        except KeyError:
            return
        
    def show_city_error(self):
        '''
        This function will run when an inputted city does not exist
        It deletes everything and shows an error message
        '''
        # destroys everything
        for widget in self.frame.winfo_children():
            widget.destroy()
        t = self.themes[self.currTheme]
        tk.Label(self.frame, text="City not found!",
                font=("Georgia", 18, "bold"), fg="#ff6b6b", bg=t["bg"]).pack(pady=20)
        tk.Label(self.frame, text="Please check the city name\nand try again.",
                font=("Georgia", 12), fg=t["text"], bg=t["bg"]).pack()

    def show_connection_error(self):
        '''
        This function will run when there is a connection error
        '''
        for widget in self.frame.winfo_children():
            widget.destroy()
        t = self.themes[self.currTheme]
        tk.Label(self.frame, text="Connection Error!",
                font=("Georgia", 18, "bold"), fg="#ff6b6b", bg=t["bg"]).pack(pady=20)
        tk.Label(self.frame, text="Please reconnect to the internet and try again.",
                font=("Georgia", 12), fg=t["text"], bg=t["bg"]).pack()

    def get_local_time(self):
        '''
        This function gets the local time of the city
        param self
        returns the time in a string with Hour:Minute:Second format
        '''
        # first, we have to find time zone, which is given by API
        offset = self.display_data["timezone"]
        
        # gets UTC(GMT) time 
        utcTime = datetime.datetime.now(datetime.timezone.utc)
        
        # calculates the offset and returns just hour:min:sec
        return utcTime + datetime.timedelta(seconds=offset)

    
    def update_time(self):
        try:
            if self.display_data and self.time_label:
                new_theme = self.get_theme()
                if new_theme != self.currTheme:
                    self.currTheme = new_theme
                    self.display()
                else:
                    self.time_label.config(
        text=f"{self.get_local_time().strftime('%b %d, %Y')} | {self.get_local_time().strftime('%I:%M:%S %p')}")
        except tk.TclError:
            pass
        self.root.after(1000, self.update_time)

    # sunrises and sunsets
    def get_sun_time(self, key):
        '''
        gets sunrise or sunset
        param key: if we want sunrise
        returns the local time of the sunrise/sunset
        '''
        offset = self.display_data["timezone"]
        sunTime = datetime.datetime.fromtimestamp(self.display_data[key], tz=datetime.timezone.utc)
        return sunTime + datetime.timedelta(seconds=offset)
    
    def get_theme(self):
        '''
        gives what time of day it is based on sunrise/sunset
        '''
        # gets curr time, sunrise, sunset
        now = self.get_local_time()
        sunrise = self.get_sun_time("sunrise")
        sunset = self.get_sun_time("sunset")
        # gets the delta time of 1 hour
        one_hour = datetime.timedelta(hours=1)

        # checks if it is in day time
        if sunrise <= now <= sunset:
            # checks if it is within an hour of sunrise/sunset(twilight)
            if now <= sunrise + one_hour or now >= sunset - one_hour:
                return "twilight"
            return "day"
        return "night"

    def apply_theme(self):
        t = self.themes[self.currTheme]
        self.root.configure(bg=t["bg"])
        self.frame.configure(bg=t["bg"])
        self.status_bar.configure(bg=t["bg"])
        self.search_frame.configure(bg=t["bg"])
        self.city_entry.configure(bg=t["card"])
        for btn in [self.update_btn, self.switch_F_btn, self.switch_C_btn, self.change_city_btn]:
            btn.configure(bg=t["btn"], highlightbackground=t["btn"])

    def make_forecast_graph(self):
        '''
        This function will make a graph based on the forecast 
        It can either be an hourly graph or a weekly graph
        '''
        # creates new window for the graph
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Forecast Graph")

        # uses the current theme
        graph_window.configure(bg=self.themes[self.currTheme]["bg"])

        # creates matplotlib window
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        t = self.themes[self.currTheme]


        # extracts data from display_forecast
        dates = [datetime.datetime.strptime(item['date'], '%Y-%m-%d').strftime('%b %d') for item in self.display_forecast]        
        highs = [item["temp_max"] for item in self.display_forecast]
        lows = [item["temp_min"] for item in self.display_forecast]
        avgs = [(l+h)/2 for l,h in zip(lows, highs)]

        ax.plot(dates, highs, color="#ff6b6b", marker='o', label='High')
        ax.plot(dates, lows, color="#4a90d9", marker='o', label='Low')
        ax.plot(dates, avgs, color="#f6c337", marker='o', label='Avg', linestyle='--')

        # style to match theme
        ax.set_title("5-Day Forecast", color=t["fg"])
        ax.legend(fontsize=8)
        ax.tick_params(colors=t["fg"])
        fig.patch.set_facecolor(t["card"])
        ax.set_facecolor(t["card"])
        for spine in ax.spines.values():
            spine.set_edgecolor(t["fg"])

        # embed into new window
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def make_hour_graph(self):
        '''
        This function makes a graph about the hourly forecasts'''

    def bind_recursive(self, widget, event, callback):
        widget.bind(event, callback)
        widget.config(cursor="hand2")
        for child in widget.winfo_children():
            self.bind_recursive(child, event, callback)