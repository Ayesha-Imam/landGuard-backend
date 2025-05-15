import random
from .utils.generate_image_utils import generate_image_with_message
from .utils.facebook_utils import post_to_facebook
from .utils.db_utils import get_mongo_collection

def scheduled_post_to_facebook():
    try:
        collection = get_mongo_collection(collection_name="locations")

        places = [doc.get("place_name", "Unknown Place") for doc in collection.find({}, {"_id": 0, "place_name": 1})]

        if not places:
            print("No locations found.")
            return

        place_name = random.choice(places)

        caption = "Green Spot Highlight from LandGuard"

        message = (
            f"{place_name} is available for plantation.\n"
        )

        image_path = generate_image_with_message(message)
        result = post_to_facebook(caption, image_path)
        print("Scheduled post result:", result)

    except Exception as e:
        print("Scheduled post failed:", str(e))