from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('post/',views.post,name="post"),
    path('list/',views.list,name="list"),
    path('list/<str:tag_name>',views.list,name="list"),
    path('search/',views.search,name="search"),
    path('details/<int:article_id>',views.details,name="details"),
    path('comments/<int:article_id>',views.comment,name="comment"), # For root comment
    path('profile/<str:username>',views.profile,name="profile"),
    path('profile/delete/<int:article_id>',views.delete,name="delete"),
    path('profile/update/<int:article_id>', views.update, name="update"),
]
