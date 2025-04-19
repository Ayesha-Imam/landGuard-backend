from django.urls import path

from .views.get_all_views import GetAllViews
from .views.get_multiple_ndvi_views import NDVIMultiView
from .views.get_ndvi_views import NDVIView
NDVIMultiView
import sys

app_name = "api"

urlpatterns = [
    path('ndvi/', NDVIView.as_view(), name='ndvi'),
    path('ndvi/multiple/', NDVIMultiView.as_view(), name= 'ndviMultiple'),
    path('ndvi/getAll/', GetAllViews.as_view(), name = 'getAll')
    
]

# Debug: Print all URLs inside api/urls.py
print("API URLs:", file=sys.stderr)
for urlpattern in urlpatterns:
    print(urlpattern, file=sys.stderr)

# from django.urls import path
# from .views import hello_world

# urlpatterns = [
#     path('hello/', hello_world, name='hello_world'),
# ]