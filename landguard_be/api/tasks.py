# myapp/tasks.py
from .utils.generate_image_utils import generate_image_with_message
from .utils.facebook_utils import post_to_facebook

def scheduled_post_to_facebook():
    message = "This is an automated weekly update from LandGuard 🌱"
    try:
        image_path = generate_image_with_message(message)
        result = post_to_facebook(message, image_path)
        print("Scheduled post result:", result)
    except Exception as e:
        print("Scheduled post failed:", str(e))
