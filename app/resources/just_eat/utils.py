from geopy.geocoders import Nominatim
from flask import abort


def get_country_code_from_lat_lon(lat, lon):

    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(lat + "," + lon)
        country_code = location.raw['address'].get('country_code')
        if country_code == 'gb':
            country_code = 'uk'

        return country_code
    except Exception:
        print("geopy is down..")


def get_tenant_from_country_code(country_code):
    if country_code == 'uk':
        tenant = country_code
    elif country_code == 'au' or country_code == 'nz':
        tenant = 'aus'
    else:
        tenant = 'i18n'
    return tenant
