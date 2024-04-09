from .queries  import get_ingredient_price, get_recipe_ingredient, get_recipe_id, get_meal_id
from .models import Sales, RecipePrice, Stock
from decimal import Decimal

def calculate_recipe_cost(recipe_id):
    recipe_ingredients = get_recipe_ingredient(recipe_id)
    total_cost = Decimal(0.0)
    for ingredient in recipe_ingredients:
        price_per_unit = get_ingredient_price(ingredient.stock_id)
        total_cost += price_per_unit * ingredient.quantity
    return total_cost

def calculate_new_buying_price(sales_id, quantity):
    recipe_id = get_recipe_id(sales_id)
    recipe_ingredient = get_recipe_ingredient(recipe_id)

    for ingredient in recipe_ingredient:
        price_per_unit = get_ingredient_price(ingredient.stock_id)
        new_quantity = quantity * ingredient.quantity
        total= new_quantity * price_per_unit
        stock = Stock.objects.get(pk = ingredient.stock_id)
        stock.buying_price -= total
        stock.save()
      

def calculate_total_cost(meal_id, quantity):
    recipe = RecipePrice.objects.get(pk = meal_id)
    total = recipe.production_price * quantity
    return total


def calculate_total_sales(meal_id, quantity):
    recipe = RecipePrice.objects.get(pk = meal_id)
    total = recipe.sale_price * quantity
    return total


def calculate_total_gain(meal_id, quantity):
    recipe = RecipePrice.objects.get(pk = meal_id)
    total = recipe.gain * quantity
    return total