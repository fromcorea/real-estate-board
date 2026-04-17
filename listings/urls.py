from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='list'),
    path('create/', views.PropertyCreateView.as_view(), name='create'),
    path('my/', views.MyListingsView.as_view(), name='my_listings'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('map/', views.MapView.as_view(), name='map'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='delete'),
    path('<int:pk>/bookmark/', views.BookmarkToggleView.as_view(), name='bookmark_toggle'),
    path('<int:pk>/complete/', views.PropertyCompleteView.as_view(), name='complete'),
    path('<int:pk>/report/', views.ReportCreateView.as_view(), name='report'),
    path('notices/', views.NoticeListView.as_view(), name='notice_list'),
    path('notices/<int:pk>/', views.NoticeDetailView.as_view(), name='notice_detail'),
]
