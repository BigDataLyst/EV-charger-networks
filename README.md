EV Charging Station Finder and Map Plotter
========================================

This project can fetch EV charging station data from the NLR API, cache it to disk, and generate map images from the cached data.

Folder contents
---------------
- electric_vehicle_charging_stations_finder.py
  Fetches station data for a selected network and saves a per-network cache file.
- plot_station_map.py
  Reads one or more cached station JSON files and creates a PNG map image.
- .venv/
  A project-specific virtual environment with the required Python packages.

Requirements
------------
- Python 3.11 or newer
- A valid NLR API key stored in nlr_api_key.py

Setup
-----
1. Open a terminal in this project folder.
2. Activate the virtual environment:
   .\.venv\Scripts\Activate.ps1
3. If needed, install dependencies:
   python -m pip install --upgrade pip requests matplotlib pandas plotly folium kaleido

Run the station fetcher
-----------------------
Use the fetcher to download station data for a network and save it to a cache file.

Example:
  .\.venv\Scripts\python.exe electric_vehicle_charging_stations_finder.py --network Tesla --skip-prompt

Optional flags:
- --debug
  Show verbose progress output.
- --skip-prompt
  Use the default cache behavior without asking interactive questions.

Run the map plotter
-------------------
Use the plotter to create a PNG map from one or more cached station JSON files.

Example for one network:
  .\.venv\Scripts\python.exe plot_station_map.py tesla_stations.json --output tesla_map.png

Example for multiple networks:
  .\.venv\Scripts\python.exe plot_station_map.py tesla_stations.json ionna_stations.json --output combined_map.png --title "Tesla and Ionna Stations"

Cache files
-----------
The fetcher writes cache files named like:
- tesla_stations.json
- ionna_stations.json

These files are reused on later runs unless you choose to refresh them.
