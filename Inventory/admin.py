from django.contrib import admin
from .models import Stock, Recipe, RecipeIngredient, RecipePrice, Sales


admin.site.register(Stock)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(RecipePrice)
admin.site.register(Sales)
