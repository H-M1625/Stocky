"""
URL configuration for Stocky project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from Inventory import views
from register import views as v 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', v.register, name='register'),
    path('', include("django.contrib.auth.urls")),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('admin/', admin.site.urls),
    path( '', views.index, name= "index"),
    #path('stck/', views.stockformview, name="stock_form"),
    path('success/',views.success_view, name="success"),
    path('stock_view/', views.stock_view, name="stock_view" ),
    #path('add_quantity/', views.add_quantity_view, name="add_quantity"),
    #path('create_recipe/', views.create_recipe_view, name='create_recipe'),
    #path('recipe_view/', views.recipe_view, name='recipes_view'),
    path('recipes/<int:pk>/edit/', views.recipe_details, name='recipe_edit'),
    path('recipes/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    
   
    #path('create_meal/', views.create_meal_view, name='create_meal'),
    path('sales/', views.sales, name="sales"),
    path('day_sales/', views.sales_view, name="day_sales"),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('reset_database/', views.reset_database, name='reset_database'),

    #path('meal_view/', views.meal_view, name='meal_view'),
    path('menu/<int:pk>/delete/', views.menu_delete, name='menu_delete'),
    path('menu/<int:pk>/edit/', views.menu_edit, name='menu_edit'),


    path('stock/', views.stock, name='stock'),
    path('recipes/', views.recipes, name='recipes'),
    path('menu/', views.menu, name='menu'),
  
]

    

 