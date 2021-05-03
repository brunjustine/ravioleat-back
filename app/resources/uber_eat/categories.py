from typing import Dict, List, Any
import requests


def call_category(params: Dict[str, Any]) -> List:
    """
    Return all category restaurants in Uber eat API
    ---
    tags:
        - Flask API
    responses:
        200:
            description: JSON representing all the elements
    """
    url = "https://cn-geo1.uber.com/rt/eats/v1/search/home"
    data = {
                "supportedTypes": ["grid"],
                "targetLocation": {
                    "address": {
                        "eaterFormattedAddress": params['formatted_address']
                    },
                    "latitude": float(params['latitude']),                                                                                        
                    "longitude": float(params['longitude'])
                }
    }
    headers = {'Content-Type': 'application/json'}
    restaurants = requests.post(url, json=data, headers=headers)
    categories = get_categories(restaurants.json())
    return categories


def get_categories(categories: Dict[str, Any]):
    if categories['suggestedSections'] is not None:
        top_categories = next((x for x in categories['suggestedSections'] if x['title'] == "Top categories"), None)
        return list(map(lambda category: category['title'], top_categories['gridItems']))
    else:
        return []


def get_formatted_categories(params: Dict[str, Any]):
    categories = call_category(params)
    if len(categories) > 0:
        categories_regex = "" 
        for category in categories:
            categories_regex += category+"|"
    else:
        categories_regex = "" 
    return categories_regex
