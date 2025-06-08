results =  {}

PREDEFINED_CODES = \
    {
        "837": {
            "main": [
                "040",
                "150"
            ],
            "partner": [
                "040",
                "170"
            ]
        },
        "106": {
            "main": [
                "036",
                "042",
                "045",
                "068",
                "140",
                "158",
                "244",
                "248"
            ],
            "partner": [
                "042",
                "069",
                "081",
                "086",
                "172",
                "240",
                "245",
                "249"
            ]
        },
        "161": {
            "main": [
                "101",
                "258"
            ],
            "partner": [
                "102",
                "272"
            ]
        },
        "867": {
            "main": [
                "043",
                "078",
                "126",
                "142"
            ],
            "partner": [
                "043"
            ]
        },
        "858": {
            "main": [],
            "partner": [
                "089"
            ]
        },
        "127": {
            "main": [
                "132",
                "232"
            ],
            "partner": [
                "232"
            ]
        }
    }

def init_results():
    global results
    results = {code: 0 for form in PREDEFINED_CODES.values()
               for category in form.values()
               for code in category}
