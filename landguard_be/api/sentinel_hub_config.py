# sentinel_hub_config.py
from datetime import datetime

EVALSCRIPT = """
//VERSION=3
function setup() {
    return {
        input: [{ bands: ["B04", "B08", "dataMask"] }],
        output: [
                { id: "ndvi", bands: 1 , sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 , sampleType: "UINT8"}
            ]
    };
}
function evaluatePixel(sample) {
    if (sample.dataMask === 1) { // Ensure valid pixels
        let denominator = sample.B08 + sample.B04;
        if(denominator !== 0){
            let ndvi = (sample.B08 - sample.B04) / denominator;
            return { ndvi: [ndvi], dataMask: [sample.dataMask] };
        } else {
            return { ndvi: [NaN], dataMask:[sample.dataMask] };
        }
    } else {
        return { ndvi: [NaN], dataMask: [sample.dataMask] };
    }
}
"""

# def get_stats_request(coordinates, already_wrapped=False):
#     return {
#         "input": {
#             "bounds": {
#                 "geometry": {
#                     "type": "Polygon",
#                     "coordinates": coordinates if already_wrapped else [coordinates]
#                 },
#                 "properties": {
#                     "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
#                 }
#             },
#             "data": [{
#                 "type": "sentinel-2-l2a",
#                 "dataFilter": {
#                     "mosaickingOrder": "mostRecent"
#                 }
#             }]
#         },
#         "aggregation": {
#             "timeRange": {
#                 "from": "2025-03-01T00:00:00Z",
#                 "to": "2025-04-01T00:00:00Z"
#             },
#             "aggregationInterval": {
#                 "of": "P30D"
#             },
#             "evalscript": EVALSCRIPT,
#         }
#     }

def get_stats_request(coordinates, already_wrapped=False, from_date=None, to_date=None, interval_days=30):
    coord = [coordinates] if not already_wrapped else coordinates

    # If from_date or to_date is None, raise an error or set default
    if from_date is None or to_date is None:
        raise ValueError("from_date and to_date must be provided")

    return {
        "input": {
            "bounds": {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coord
                },
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                }
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "mosaickingOrder": "mostRecent"
                }
            }]
        },
        "aggregation": {
            "timeRange": {
                "from": from_date,
                "to": to_date
            },
            "aggregationInterval": {
                "of": f"P{interval_days}D"
            },
            "evalscript": EVALSCRIPT,
        }
    }


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

