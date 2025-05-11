# import requests
# from django.conf import settings
# from decouple import config

# FB_PAGE_ID = config("FB_PAGE_ID")
# FB_PAGE_ACCESS_TOKEN = config("FB_PAGE_ACCESS_TOKEN")

# def post_to_facebook(message):
#     page_id = FB_PAGE_ID
#     access_token = FB_PAGE_ACCESS_TOKEN
    
#     # Define the URL for the Graph API feed
#     url = f"https://graph.facebook.com/v22.0/{page_id}/feed"
    
#     # Define the data to send in the request
#     data = {
#         "message": message,
#         "access_token": access_token
#     }
    
#     headers = {
#         'Authorization': f'Bearer {access_token}', 
#         'Content-Type': 'application/json', 
#     }
    
#     response = requests.post(url, json=data, headers=headers)

#     print("Status Code:", response.status_code)
#     print("Response:", response.json())

#     return response.json()



import requests
from django.conf import settings
from decouple import config

FB_PAGE_ID = config("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = config("FB_PAGE_ACCESS_TOKEN")

def post_to_facebook(message, image_path):
    page_id = FB_PAGE_ID
    access_token = FB_PAGE_ACCESS_TOKEN
    
    # Define the URL for the Graph API photos endpoint
    url = f"https://graph.facebook.com/v22.0/{page_id}/photos"
    
    # Define the data to send in the request
    data = {
        "message": message,
        "access_token": access_token
    }
    
    # Open the image file and prepare for upload
    with open(image_path, 'rb') as image_file:
        files = {
            'file': image_file
        }
        
        # Send the POST request with both the image and message
        response = requests.post(url, data=data, files=files)

    print("Status Code:", response.status_code)
    print("Response:", response.json())

    return response.json()
