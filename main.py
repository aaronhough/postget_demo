import os, requests, json
from typing import Tuple

'''
Code for creating sample app on postget.dev
it's recommended that your api key is stored securely in an env var
    called POSTGET_KEY

If you haven't already done so, check out the source article at
    https://postget.dev/docs?view=example
'''

# static vars
url = "https://app.postget.dev/api/v1/owner"
key_url = "https://app.postget.dev/api/v1/keys"
key = os.getenv('POSTGET_KEY')

if not key:
    key = input('postget api key (https://app.postget.dev/apikeys?view=secret):')

headers = {"Authorization": f"Basic {key}"}
app_id = "animal_crossings"

def helper(endpoint: str, json: dict, headers: dict) -> Tuple[int, dict]:
    # helper function

    r = requests.post(endpoint, json = json, headers = headers)
    return r.status_code, r.json() if r.status_code == 200 else {}

def building_the_app() -> Tuple[int, dict]:
    # create the parent app object

    animal_crossings_app = {
        "name": "Animal Crossings",
        "description": "The most cutting edge platform for tracking and celebrating animal sightings",
        "limit": 10000,
        "docId": app_id
    }
        
    return helper(f"{url}/apps", animal_crossings_app, headers)

def building_the_first_route() -> Tuple[int, dict]:
    # the first route for locations

    locations_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "name": {
                "type": "string",
                "minLength": 5,
                "maxLength": 50
            },
            "description": {
                "type": "string",
                "minLength": 5,
                "maxLength": 200
            }
        },
        "required": [
            "name",
            "description"
        ]
    }

    locations_route = {
        "name": "Locations",
        "description": "This route hosts a collection of locations where animal sightings \
            may have taken place...",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "schema": locations_schema,
        "docId": "locations"
    }

    return helper(f"{url}/apps/{app_id}/routes", locations_route, headers)

def building_the_second_route() -> Tuple[int, dict]:
    # the second route for sightings

    sightings_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "location": {
                "type": "string",
                "minLength": 5,
                "maxLength": 50
            },
            "animal_type": {
                "type": "string",
                "enum": ["beaver", "seagull", "possum"]
            },
            "datetime": {
                "type": "object",
                "properties": {
                    "<iso>": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            }
        },
        "required": [
            "location",
            "animal_type",
            "datetime"
        ]
    }

    sightings_route = {
        "name": "Sightings",
        "description": "This route hosts a collection of animal sightings. \
            A sighting represents a location, animal type, and time",
        "methods": [
            "GET",
            "POST",
            "PUT",
            "DELETE"
        ],
        "schema": sightings_schema,
        "docId": "sightings"
    }

    return helper(f"{url}/apps/{app_id}/routes", sightings_route, headers)

def adding_first_user() -> Tuple[int, dict]:
    # creating our first superUser account
    
    sally = {
        "name": "Sally",
        "superUser": True,
        "permissions": {
            "read": [
                "locations",
                "sightings"
            ],
            "write": [
                "locations",
                "sightings"
            ]
        },
        "docId": "sally"
    }
        
    return helper(f"{url}/apps/{app_id}/clients", sally, headers)

def adding_second_user() -> Tuple[int, dict]:
    # creating our second user... no superUser status

    jake = {
        "name": "Jake",
        "superUser": False,
        "permissions": {
            "read": [
                "locations",
                "sightings"
            ],
            "write": [
                "locations",
                "sightings"
            ]
        },
        "docId": "jake"
    }
        
    return helper(f"{url}/apps/{app_id}/clients", jake, headers)

def adding_read_only_account() -> Tuple[int, dict]:
    # creating a read only account

    possums_inc = {
        "name": "Possums Incorporated",
        "superUser": False,
        "permissions": {
            "read": [
                "sightings"
            ],
            "write": []
        },
        "docId": "possums_inc"
    }

    return helper(f"{url}/apps/{app_id}/clients", possums_inc, headers)

def get_user_keys(client_dict: dict = {'sally': None, 'jake': None, 'possums_inc': None}) -> dict:
    # read the client keys and return in a dict

    for client_id in client_dict.keys():

        r = requests.get(f"{key_url}/{client_id}?appId={app_id}", headers = headers)

        if r.status_code == 200:
            client_dict[client_id] = r.json()["response"]["apiKey"]
    
    return client_dict

def run_all(verbose:bool = True, fetch_keys:bool = False) -> None:
    # build everything
    
    builder_functions = {
        'building_the_app':building_the_app,
        'building_the_first_route': building_the_first_route, 
        'building_the_second_route': building_the_second_route, 
        'adding_first_user': adding_first_user, 
        'adding_second_user': adding_second_user, 
        'adding_read_only_account': adding_read_only_account
    }

    print(f'executing {app_id} build...')

    for name, fn in builder_functions.items():
        
        print(f'\nrunning {name}...')
        resp_code, payload = fn()
        print(f'result: {resp_code}')

        if verbose:
            print(json.dumps(payload, indent=4))
    
    if fetch_keys:

        print('\nfetching client keys...')
        key_dict = get_user_keys()

        for user_id, key in key_dict.items():
            print(f'{user_id} : {key}')
    
    print('\ncomplete...')

if __name__ == '__main__':

    # run build pipeline
    run_all()