import argparse
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt


COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]


def load_station_data(cache_file):
    if not os.path.exists(cache_file):
        raise FileNotFoundError(f"Cache file not found: {cache_file}")

    with open(cache_file, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_map_image(cache_files, output_file=None, title=None):
    if isinstance(cache_files, (str, os.PathLike)):
        cache_files = [cache_files]

    fig, ax = plt.subplots(figsize=(10, 8))
    legend_handles = []

    for index, cache_file in enumerate(cache_files):
        stations = load_station_data(cache_file)
        latitudes = []
        longitudes = []
        for station in stations:
            lat = station.get("latitude")
            lon = station.get("longitude")
            if lat is not None and lon is not None:
                try:
                    latitudes.append(float(lat))
                    longitudes.append(float(lon))
                except (TypeError, ValueError):
                    continue

        if not latitudes or not longitudes:
            continue

        color = COLORS[index % len(COLORS)]
        label = Path(cache_file).stem.replace("_stations", "").replace("_", " ").title()
        ax.scatter(longitudes, latitudes, s=20, color=color, alpha=0.7, label=label)
        legend_handles.append(label)

    if not legend_handles:
        raise ValueError("No valid station coordinates found in the supplied cache files")

    ax.set_title(title or "EV Charging Station Locations")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Networks", loc="best")

    all_longitudes = []
    all_latitudes = []
    for cache_file in cache_files:
        stations = load_station_data(cache_file)
        for station in stations:
            lat = station.get("latitude")
            lon = station.get("longitude")
            if lat is not None and lon is not None:
                try:
                    all_latitudes.append(float(lat))
                    all_longitudes.append(float(lon))
                except (TypeError, ValueError):
                    continue

    if all_longitudes and all_latitudes:
        lon_min = min(all_longitudes)
        lon_max = max(all_longitudes)
        lat_min = min(all_latitudes)
        lat_max = max(all_latitudes)

        lon_span = max(lon_max - lon_min, 1e-6)
        lat_span = max(lat_max - lat_min, 1e-6)
        margin_lon = lon_span * 0.08
        margin_lat = lat_span * 0.08

        ax.set_xlim(lon_min - margin_lon, lon_max + margin_lon)
        ax.set_ylim(lat_min - margin_lat, lat_max + margin_lat)

    if output_file is None:
        output_file = Path(cache_files[0]).with_suffix(".png")
    else:
        output_file = Path(output_file)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_file, dpi=200)
    plt.close(fig)
    return str(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot cached EV charging station data to an image")
    parser.add_argument(
        "cache_files",
        nargs="+",
        help="One or more cached station JSON files to plot",
    )
    parser.add_argument("--output", "-o", help="Output PNG file path")
    parser.add_argument("--title", default="EV Charging Station Locations", help="Plot title")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    resolved_cache_files = []
    for cache_file in args.cache_files:
        path = Path(cache_file)
        if not path.is_absolute():
            path = base_dir / path
        resolved_cache_files.append(str(path))

    output_file = args.output
    if output_file and not Path(output_file).is_absolute():
        output_file = str(base_dir / output_file)

    result = build_map_image(resolved_cache_files, output_file=output_file, title=args.title)
    print(f"Saved map image to: {result}")
