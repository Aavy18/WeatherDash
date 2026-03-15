from WeatherDashAppV1 import WeatherApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root, "New York City")
    root.mainloop()
