from django.urls import path, include
from . import views
from . import api


urlpatterns = [
    # Auth
    path('login', views.View_Login.as_view(), name='login'),
    path('logout', views.View_Logout.as_view(), name='logout'),

    # General
    path('', views.View_Index.as_view(), name='index'),
    path('chart/<str:asset>', views.View_Chart.as_view(), name='chart'),
    path('account', views.View_Account.as_view(), name='account'),
    path('assets', views.View_AssetsList.as_view(), name='assets'),

    # API
    path('api/chart/save', api.Api_Chart_Save.as_view(), name='api_chart_save'),
    path('api/chart/request_indicator_ui', api.Api_Chart_Request_Indicator_UI.as_view(), name='api_chart_request_indicator_ui'),

    path('api/users/action', api.Api_Users_Action.as_view(), name='api_users_action'),

    path('api/assets/load_list', api.Api_Assets_LoadList.as_view(), name='api_assets_load_list'),
    path('api/assets/action', api.Api_Assets_Action.as_view(), name='api_assets_action'),

    path('api/internal/wsc/add', api.Api_Internal_WscAdd.as_view(), name='api_internal_wsc_add'),
    path('api/internal/wsc/remove', api.Api_Internal_WscRemove.as_view(), name='api_internal_wsc_remove'),
    path('api/internal/invalidate_asset', api.Api_Internal_InvalidateAsset.as_view(), name='api_internal_invalidate_asset'),

    # Admin
    path('users', views.View_Admin_Users.as_view(), name='users'),
    path('users/<int:user_id>', views.View_Admin_UserAccount.as_view(), name='user_account'),

    # For redirecting to <index> from unwanted pages of all-auth
    path('accounts/signup/', views.View_RedirectToIndex.as_view()),
    path('accounts/login/', views.View_RedirectToIndex.as_view()),
    path('accounts/google/signup/', views.View_RedirectToIndex.as_view()),
    path('accounts/inactive/', views.View_InactiveAccount.as_view()),

    # For Google auth
    path('accounts/', include('allauth.urls')),

    path('clear/', views.View_ClearOrdpos.as_view(), name='clear'),
]