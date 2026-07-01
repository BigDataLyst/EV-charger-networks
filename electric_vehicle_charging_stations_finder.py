#First run push command
# & "C:\Users\brett\AppData\Local\Programs\Python\Python313\python.exe" -m pip install requests
import argparse
import json
import os

import requests
from nlr_api_key import my_nlr_dev_key  # Ensure you have your API key stored in this module


def debug_print(message, debug=False):
    if debug:
        print(message)


def get_ev_charging_networks(api_key, country="all", cache_file=None, refresh=False, debug=False):
    """
    Fetches the full list of electric vehicle (EV) charging networks.

    Parameters:
    - api_key (str): Your developer API key.
    - country (str): 'all' (US & Canada), 'US', or 'CA'. Default is 'all'.
    - cache_file (str | None): Optional path to a JSON file for caching the results.
    - refresh (bool): If True, ignore any existing cache and fetch fresh data.
    """
    if cache_file and os.path.exists(cache_file) and not refresh:
        try:
            with open(cache_file, "r", encoding="utf-8") as cache_handle:
                cached_networks = json.load(cache_handle)
                if cached_networks:
                    debug_print(f"Loaded network list from cache: {cache_file}", debug)
                    return cached_networks
        except (json.JSONDecodeError, OSError):
            pass

    url = "https://developer.nlr.gov/api/alt-fuel-stations/v1/electric-networks.json"

    params = {
        "api_key": api_key,
        "country": country,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        networks = response.json()

        if cache_file:
            try:
                with open(cache_file, "w", encoding="utf-8") as cache_handle:
                    json.dump(networks, cache_handle, indent=2)
            except OSError as err:
                debug_print(f"Could not write network cache file: {err}", debug)

        return networks

    except requests.exceptions.HTTPError as http_err:
        debug_print(f"HTTP error occurred: {http_err}", debug)
        if response.status_code == 422:
            debug_print(f"Details: {response.text}", debug)
    except Exception as err:
        debug_print(f"An error occurred: {err}", debug)

    return None

# --- Example Usage ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch EV charging network and station data")
    parser.add_argument("--debug", action="store_true", help="Enable verbose terminal output")
    parser.add_argument("--network", default="IONNA", help="Network name to fetch station locations for")
    parser.add_argument("--skip-prompt", action="store_true", help="Skip the interactive cache prompt")
    args = parser.parse_args()

    MY_API_KEY = my_nlr_dev_key
    network_cache_path = os.path.join(
        os.path.dirname(__file__),
        "ev_networks_cache.json",
    )

    if os.path.exists(network_cache_path) and not args.skip_prompt:
        choice = input(
            "Network cache file found. Choose an option:\n"
            "1) Use cached network list\n"
            "2) Refresh and replace network cache\n"
            "Enter 1 or 2: "
        ).strip()
    else:
        choice = "2" if not args.skip_prompt else "1"

    refresh_network_cache = choice == "2"
    network_list = get_ev_charging_networks(
        api_key=MY_API_KEY,
        country="all",
        cache_file=network_cache_path,
        refresh=refresh_network_cache,
        debug=args.debug,
    )

    if network_list:
        debug_print(f"Successfully retrieved {len(network_list)} networks.\n", args.debug)

        if args.debug:
            for network in network_list:
                name = network.get("name", "N/A")
                key = network.get("key", "N/A")
                url = network.get("url", "N/A")
                print(f"Network Name: {name} | Key: {key} | Website: {url}")


def get_station_locations_by_network(api_key, network_key, country="US", limit=200, cache_file=None, refresh=False, append=False, debug=False):
    """
    Fetches location details for electric charging stations filtered by a specific network.

    Parameters:
    - api_key (str): Your developer API key.
    - network_key (str): The 'key' string from your network_list (e.g., 'Tesla', 'ChargePoint Network').
    - country (str): Country code ('US' or 'CA').
    - limit (int): Maximum number of records to return per API call.
    - cache_file (str | None): Optional path to a JSON file for caching the results.
    - refresh (bool): If True, ignore any existing cache and fetch fresh data.
    - append (bool): If True and a cache exists, append newly fetched rows to the existing cached list.
    """
    existing_stations = []
    if cache_file and os.path.exists(cache_file) and not refresh:
        try:
            with open(cache_file, "r", encoding="utf-8") as cache_handle:
                existing_stations = json.load(cache_handle)
                if existing_stations:
                    return existing_stations
        except (json.JSONDecodeError, OSError):
            pass

    url = "https://developer.nlr.gov/api/alt-fuel-stations/v1.json"

    params = {
        "api_key": api_key,
        "fuel_type": "ELEC",
        "ev_network": network_key,
        "country": country,
        "limit": limit,
        "offset": 0,
    }

    all_stations = []

    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            stations = data.get("fuel_stations", [])
            if not stations:
                break

            all_stations.extend(stations)

            if len(stations) < limit:
                break

            params["offset"] += limit
            debug_print(f"Fetched {len(all_stations)} stations so far...", debug)

        except requests.exceptions.HTTPError as http_err:
            debug_print(f"HTTP error occurred: {http_err}", debug)
            break
        except Exception as err:
            debug_print(f"An error occurred: {err}", debug)
            break

    if cache_file:
        try:
            if append and existing_stations:
                merged_stations = existing_stations + all_stations
                with open(cache_file, "w", encoding="utf-8") as cache_handle:
                    json.dump(merged_stations, cache_handle, indent=2)
            else:
                with open(cache_file, "w", encoding="utf-8") as cache_handle:
                    json.dump(all_stations, cache_handle, indent=2)
        except OSError as err:
            debug_print(f"Could not write cache file: {err}", debug)

    return all_stations if not append else (existing_stations + all_stations)

# --- Example Integration with your network_list ---
if __name__ == "__main__":
    MY_API_KEY = my_nlr_dev_key

    target_network = args.network
    cache_path = os.path.join(
        os.path.dirname(__file__),
        f"{target_network.lower().replace(' ', '_')}_stations.json",
    )

    debug_print(f"Fetching station locations for network: {target_network}...", args.debug)

    if os.path.exists(cache_path) and not args.skip_prompt:
        choice = input(
            "Cache file found. Choose an option:\n"
            "1) Use cached data\n"
            "2) Refresh and replace cached data\n"
            "3) Refresh and append to cached data\n"
            "Enter 1, 2, or 3: "
        ).strip()
    else:
        choice = "1" if args.skip_prompt else "2"

    if choice == "1":
        refresh_cache = False
        append_cache = False
    elif choice == "3":
        refresh_cache = True
        append_cache = True
    else:
        refresh_cache = True
        append_cache = False

    stations_list = get_station_locations_by_network(
        api_key=MY_API_KEY,
        network_key=target_network,
        cache_file=cache_path,
        refresh=refresh_cache,
        append=append_cache,
        debug=args.debug,
    )

    if stations_list:
        debug_print(f"\nFound total of {len(stations_list)} station locations.", args.debug)
        debug_print(
            f"\nFound total of {len([station for station in stations_list if station.get('state') == 'NC'])} station locations in North Carolina.",
            args.debug,
        )

        if args.debug:
            for station in stations_list:
                if station.get("state") == "NC":  # Filter for North Carolina stations
                    name = station.get("station_name", "Unknown Name")
                    city = station.get("city", "N/A")
                    state = station.get("state", "N/A")
                    street = station.get("street_address", "N/A")
                    lat = station.get("latitude")
                    lon = station.get("longitude")

                    print(f"\n- Station: {name}")
                    print(f"  Address: {street}, {city}, {state}")
                    print(f"  Coordinates: ({lat}, {lon})")