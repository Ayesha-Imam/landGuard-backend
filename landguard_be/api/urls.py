from django.urls import path

from .views.user_details_view import UserDetailView,UserEditView, UserDeleteView, UserChangePasswordView
from .views.list_users_view import ListAllUsersViews
from .views.google_auth_view import GoogleAuthView
from .views.save_ndvi_inDB import saveNDVIView
from .views.get_all_views import GetAllViews
from .views.get_multiple_ndvi_views import NDVIMultiView
from .views.get_ndvi_views import getNDVIView
from .views.signUp_view import SignupView
from .views.login_view import LoginView
from .views.logout_view import LogoutView
from .views.validateUser import ValidateUserView
import sys
from .views.social_views import FacebookPostView
from .views.post_view import CreateLandPostView, AllLandPostsView, MyLandPostsView
from .views.drives_view import CreateDriveView, AllDrivesView, UserDrivesView


app_name = "api"

urlpatterns = [
    path('ndvi/', getNDVIView.as_view(), name='ndvi'),
    path('ndvi/multiple/', NDVIMultiView.as_view(), name= 'ndviMultiple'),
    path('ndvi/getAll/', GetAllViews.as_view(), name = 'getAll'),
    path('ndvi/save/', saveNDVIView.as_view(), name = 'saveNDVI'),
    path('signup/', SignupView.as_view(), name = 'signup'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('validateUser/', ValidateUserView.as_view(), name='validateUser'),
    path('google-auth/', GoogleAuthView.as_view(), name ='google-auth' ),
    path('facebook/post/', FacebookPostView.as_view(), name="facebook_post"),

    path('users/', ListAllUsersViews.as_view(), name = 'users'),
    path('users/me/', UserDetailView.as_view(), name = 'users'),
    path('users/me/edit/', UserEditView.as_view(), name = 'user-edit'),
    path('users/me/delete/', UserDeleteView.as_view(), name = 'user-delete-account'),
    path('users/me/change-password/', UserChangePasswordView.as_view(), name = 'users-change-password'),

    path("post/create/", CreateLandPostView.as_view(), name = 'create-post'),
    path("post/getAll/", AllLandPostsView.as_view(), name = 'getAll-post'),
    path("post/my-posts", MyLandPostsView.as_view(), name = 'get-my-post'),

    path("drive/create/", CreateDriveView.as_view(), name = 'create-drive'),
    path("drive/getAll/", AllDrivesView.as_view(), name = 'getAll-drive'),
    path("drive/my-drives", UserDrivesView.as_view(), name = 'get-my-drive'),

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