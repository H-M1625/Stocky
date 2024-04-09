from .models import Stock, Recipe, RecipeIngredient, Sales, RecipePrice

def get_recipe_ingredient(recipe_id):
    return RecipeIngredient.objects.filter(recipe_id= recipe_id)

def get_ingredient_price(stock_id):
    return Stock.objects.get(id=stock_id).price_per_unit

def get_ingredient_buying_price(stock_id):
    return Stock.objects.get(id=stock_id).buying_price


def get_recipe_id(meal_id):
    return RecipePrice.objects.get(pk = meal_id).recipe_id



def get_meal_id(sales_id):
    return Sales.objects.get(id = sales_id).meal_id

