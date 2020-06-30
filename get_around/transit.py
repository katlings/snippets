#!/usr/bin/env python3
import csv
import json
import random
import time

import googlemaps

DEBUG = False
# CSV file of valid addresses in a region; I got mine from https://openaddresses.io/
ADDRESSES = 'addressdata/us/ny/city_of_new_york.csv'
N = 50


def setup_client():
    with open('creds.json') as f:
        creds = json.loads(f.read())
    return googlemaps.Client(creds['api_key'])


def load_addresses():
    with open(ADDRESSES) as csvfile:
        reader = csv.DictReader(csvfile)
        all_addresses = list(reader)
    return all_addresses


def format_addr(address):
    # ignore unit numbers
    return f'{address["NUMBER"]} {address["STREET"]} {address["CITY"]} {address["POSTCODE"]}'


def calculate_mph(directions):
    try:
        distance_meters = directions[0]['legs'][0]['distance']['value']
        if 'arrival_time' in directions:
            start_time = time.time()
            arrival_time = directions[0]['legs'][0]['arrival_time']['value']
            time_seconds = arrival_time - start_time
        else:
            time_seconds = directions[0]['legs'][0]['duration']['value']
        return distance_meters/time_seconds * 2.237
    except (IndexError, KeyError, ZeroDivisionError):
        return None


def main():
    client = setup_client()
    addresses = load_addresses()

    transit_mphes = []
    driving_mphes = []
    bicycling_mphes = []
    for _ in range(N):
        from_addr, to_addr = random.choices(addresses, k=2)
        transit_directions = client.directions(format_addr(from_addr), format_addr(to_addr), mode='transit')
        mph = calculate_mph(transit_directions)
        if mph:
            transit_mphes.append(mph)

            # Only add the driving time if we successfully found transit directions
            driving_directions = client.directions(format_addr(from_addr), format_addr(to_addr), mode='driving')
            mph = calculate_mph(driving_directions)
            if mph:
                driving_mphes.append(mph)

            # Only add the bicycling time if we successfully found transit directions
            bicycling_directions = client.directions(format_addr(from_addr), format_addr(to_addr), mode='bicycling')
            mph = calculate_mph(bicycling_directions)
            if mph:
                bicycling_mphes.append(mph)

    if DEBUG:
        print(transit_mphes)
        print(driving_mphes)
        print(bicycling_mphes)
    print(f'Average speed over {len(transit_mphes)} transit trips was {sum(transit_mphes)/len(transit_mphes)} mph')
    print(f'Average speed over {len(bicycling_mphes)} bicycling trips was {sum(bicycling_mphes)/len(bicycling_mphes)} mph')
    print(f'Average speed over {len(driving_mphes)} driving trips was {sum(driving_mphes)/len(driving_mphes)} mph')


if __name__ == '__main__':
    main()
