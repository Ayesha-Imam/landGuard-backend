from django.urls import path

from .views.save_ndvi_inDB import saveNDVIView

from .views.get_all_views import GetAllViews
from .views.get_multiple_ndvi_views import NDVIMultiView
from .views.get_ndvi_views import getNDVIView
import sys

app_name = "api"

urlpatterns = [
    path('ndvi/', getNDVIView.as_view(), name='ndvi'),
    path('ndvi/multiple/', NDVIMultiView.as_view(), name= 'ndviMultiple'),
    path('ndvi/getAll/', GetAllViews.as_view(), name = 'getAll'),
    path('ndvi/save/', saveNDVIView.as_view(), name = 'saveNDVI')
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