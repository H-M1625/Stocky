from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView
from .forms import StockForm, AddQuantityForm, RecipeForm, RecipeIngredientFormset, RecipePriceForm, MealForm, SalesForm, RecipeIngredientForm, SaleFormSet
from .models import Stock, Recipe, RecipePrice, Sales, RecipeIngredient
from .function import calculate_recipe_cost, calculate_new_buying_price, calculate_total_cost, calculate_total_gain, calculate_total_sales
import json
from django.core.serializers.json import DjangoJSONEncoder
from .queries import get_recipe_id, get_recipe_ingredient
from django.db.models import Sum
from django.contrib import messages

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from .exceptions import NotEnoughQuantityException



# Create your views here.

def index(request):
    return render(request, 'Inventory/index.html')

def success_view(request):
    return render(request, 'Inventory/Success.html')


def stock(request):

    create_form = StockForm(request.POST or None)
    update_form = AddQuantityForm(request.POST or None)
    stock = Stock.objects.all()

    if request.method =='POST':
        
        if create_form.is_valid() and not update_form.is_valid():
            create_form.save()
            return redirect('stock')
        
        if update_form.is_valid() and not create_form.is_valid():
            selected_food= update_form.cleaned_data['food']
            additional_quantity = update_form.cleaned_data['quantity']
            price= update_form.cleaned_data['price']


            selected_food.quantity += additional_quantity
            selected_food.buying_price += price
            selected_food.save()
            return redirect('stock')
            
    context = {
        'create_form': create_form,
        'update_form': update_form,
        'stock': stock,
    }

    return render(request, 'Inventory/stock.html', context)




def stock_view(request):

    context = {}
    form = StockForm()
    stock = Stock.objects.all()
    context['stock']= stock

    if request.method == 'POST':
        if 'save' in request.POST:
            pk = request.POST.get('save')
            if not pk:
                form = StockForm(request.POST)
            else:
                food = Stock.objects.get (id=pk)
                form = StockForm(request.POST, instance=food)
            form.save()
            form = StockForm()
        elif 'delete' in request.POST:
            pk = request.POST.get('delete')
            food = Stock.objects.get(id=pk)
            food.delete()
        elif 'edit' in request.POST:
            pk= request.POST.get('edit')
            food = Stock.objects.get(id =pk)
            form = StockForm(instance=food)    

    context['form'] = form
    return render(request, 'Inventory/stock_view.html',context)


def recipes(request):
    
    recipes = Recipe.objects.all()

    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST)
        formset = RecipeIngredientFormset(request.POST)
        

        if recipe_form.is_valid() and formset.is_valid():
        
            recipe = recipe_form.save()
            instances= formset.save(commit=False)
            for instance in instances:
                instance.recipe = recipe
                instance.save()
            return redirect('recipes')
        else:
            
            print(formset.errors)     
    else:
        
        recipe_form = RecipeForm()
        formset = RecipeIngredientFormset()
    return render(request, 'Inventory/recipes.html', {'recipe_form': recipe_form, 'formset': formset,'recipes':recipes, })
    



def recipe_delete(request, pk ): 
    recipes = get_object_or_404(Recipe, pk = pk)

    if request.method == 'POST':
        recipes.delete()
        return redirect ('recipes')
    return render( request, 'Inventory/recipe_delete.html', {'recipes': recipes})


def recipe_details(request, pk ):
    recipes = get_object_or_404(Recipe, pk =pk)
    details = RecipeIngredient.objects.filter(recipe_id = pk )
    form = RecipeIngredientForm()

    context = {}
    context['recipes'] = recipes
    context['details'] = details

    if request.method == 'POST':

        if 'save' in request.POST:
            id = request.POST.get('save')
            if not id:
                form = RecipeIngredientForm(request.POST)
            else:
                ri = get_object_or_404(RecipeIngredient, id = id)
                form = RecipeIngredientForm(request.POST, instance=ri)

            if form.is_valid():
             form.instance.recipe_id = pk 
             form.save()
             form = RecipeIngredientForm()

        elif 'delete' in request.POST:
            id = request.POST.get('delete')
            ingredient = get_object_or_404(RecipeIngredient, id =id)
            ingredient.delete()
            return redirect ('recipe_edit', pk = pk)
    
        elif 'edit' in request.POST:
            id = request.POST.get('edit')
            ingredient = get_object_or_404(RecipeIngredient, id = id)
            form = RecipeIngredientForm(instance=ingredient)
            

    context['form'] = form
    return render(request, 'Inventory/recipe_detail.html', context)



def menu_delete(request, pk ): 
    meal = get_object_or_404(RecipePrice, pk = pk)

    if request.method == 'POST':
        meal.delete()
        return redirect ('menu')
    return render( request, 'Inventory/menu_delete.html', {'meal': meal})


def menu_edit(request, pk):
    meal = get_object_or_404(RecipePrice, pk = pk)

    if request.method == 'POST':
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():

            sale_price= form.cleaned_data['sale_price']
    
            rp_instance = RecipePrice.objects.get(id = pk)
            rp_instance.production_price = calculate_recipe_cost(rp_instance.recipe_id)
            print(rp_instance.production_price)
            rp_instance.sale_price = sale_price
            rp_instance.gain = sale_price - rp_instance.production_price 
            rp_instance.save()


            return redirect('menu')
    else:
        form = MealForm(instance=meal)
        return render(request, 'Inventory/menu_edit.html', context={'form': form, 'meal':meal})  


def menu(request):
    meals = RecipePrice.objects.all()
    recipes = Recipe.objects.all()
    pp= {}
    for recipe in recipes:
        pp[recipe.id] = calculate_recipe_cost(recipe.id)
    for key, value in pp.items():
        pp[key] = round(value,2)   


    if request.method == 'POST':
        form = RecipePriceForm(request.POST)
        
        if form.is_valid():
            recipe = form.cleaned_data['recipe']
            sale_price= form.cleaned_data['sale_price']

    
            rp_instance, created = RecipePrice.objects.get_or_create(recipe=recipe)
            print(recipe.id)
            rp_instance.production_price = calculate_recipe_cost(recipe.id)
            rp_instance.sale_price = sale_price
            rp_instance.gain = sale_price - rp_instance.production_price if rp_instance.production_price != 0 else 0
            rp_instance.save()

        
            
            return redirect('menu')
    else:
        form = RecipePriceForm()
    return render( request, 'Inventory/menu.html', context= {'meals':meals, 'form':form, 'production_prices': json.dumps(pp, cls=DjangoJSONEncoder)} )


def sales(request):

    if request.method == 'POST':
        recipes = RecipePrice.objects.all()

        for recipe in recipes:
            recipe.production_price = calculate_recipe_cost(recipe.recipe_id)
            recipe.gain = recipe.sale_price - recipe.production_price 
            recipe.save()

        formset = SaleFormSet(request.POST)

        if formset.is_valid():
            all_successful = True
            
            for form in formset:

                selected_meal = form.cleaned_data['meal']
                meal_quantity = form.cleaned_data['quantity']

                recipe = get_recipe_id(selected_meal.id)
                ingredients = get_recipe_ingredient(recipe)

                try:
                    
                    for ingredient in ingredients:
                        total_stock_quantity_needed = ingredient.quantity * meal_quantity
                        new_quantity = Stock.objects.get(pk = ingredient.stock_id)
                    
                        if total_stock_quantity_needed > new_quantity.quantity:
                            raise ValueError(f"Insufficient quantity {selected_meal} in stock. Please adjust your order.")
                        
                except ValueError as e:
                    all_successful = False 
                    error_message = str(e)
                    messages.error(request, error_message)   


            if all_successful:

                for form in formset:

                    selected_meal = form.cleaned_data['meal']
                    meal_quantity = form.cleaned_data['quantity']

                    recipe = get_recipe_id(selected_meal.id)
                    ingredients = get_recipe_ingredient(recipe)


                    calculate_new_buying_price(selected_meal.id, meal_quantity)
                    tpp = calculate_total_cost(selected_meal.id, meal_quantity)
                    tsp = calculate_total_sales(selected_meal.id, meal_quantity)
                    tg = calculate_total_gain(selected_meal.id, meal_quantity)
            
                    new_sale_instance = form.save(commit=False)
                    new_sale_instance.total_production_price = tpp
                    new_sale_instance.total_sale_price = tsp
                    new_sale_instance.total_gain = tg

                    new_sale_instance.save()

                    
                    for ingredient in ingredients:
                        total_stock_quantity_needed = ingredient.quantity * meal_quantity
                        new_quantity = Stock.objects.get(pk = ingredient.stock_id)
                        new_quantity.quantity -= total_stock_quantity_needed
                        new_quantity.save()                    

            return redirect('sales')        
    
    else:
        formset = SaleFormSet()
    return render(request, 'Inventory/sales.html', context={'formset':formset}) 

     



def sales_view(request):
    
    all_sales = Sales.objects.all()


    totals = {
        'meal': '',
        'quantity': all_sales.aggregate(Sum('quantity'))['quantity__sum'],
        'sale_time': '',
        'total_production_price': all_sales.aggregate(Sum('total_production_price'))['total_production_price__sum'],
        'total_sale_price': all_sales.aggregate(Sum('total_sale_price'))['total_sale_price__sum'],
        'total_gain': all_sales.aggregate(Sum('total_gain'))['total_gain__sum']
    }

    context = {
        'all_sales': all_sales,
        'totals': totals
    }
    return render(request, 'Inventory/day_sales.html', context)


def generate_pdf(request):
    response = HttpResponse(content_type='Inventory/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

   
    all_sales = Sales.objects.all()


    totals = {
        'meal': 'TOTAL ',
        'quantity': all_sales.aggregate(Sum('quantity'))['quantity__sum'],
        'sale_time': '',
        'total_production_price':"{:.2f}".format(all_sales.aggregate(Sum('total_production_price'))['total_production_price__sum']),
        'total_sale_price': "{:.2f}".format(all_sales.aggregate(Sum('total_sale_price'))['total_sale_price__sum']),
        'total_gain': "{:.2f}".format(all_sales.aggregate(Sum('total_gain'))['total_gain__sum'])
    } 


    table_data = [['Meal', 'Quantity', 'Sale Time', 'Total Production Price', 'Total Sale Price', 'Total Gain']]
    for sale in all_sales:
        table_data.append([
            sale.meal.recipe, 
            sale.quantity,
            sale.sale_time.strftime('%Y-%m-%d %H:%M:%S'),
            sale.total_production_price,
            sale.total_sale_price,
            sale.total_gain
        ])


    table_data.append([
        totals['meal'],
        totals['quantity'],
        totals['sale_time'],
        totals['total_production_price'],
        totals['total_sale_price'],
        totals['total_gain']
    ])



    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    table = Table(table_data)

    
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)
    elements.append(table)

   
    doc.build(elements)
    return response



def reset_database(request):

    if request.method == 'POST':

        sales = Sales.objects.all()
        for sale in sales:
            sale.delete()
        return redirect('day_sales')
    
    else:
        return render(request, 'Inventory/day_sales.html')  
    


 #Des functions inutile dorenavant mais on sait jamais    


"""
def meal_view(request):
    meals = RecipePrice.objects.all()

    return render(request, 'Inventory/menu_view.html', context={"meals" : meals})


def create_meal_view(request):
    recipes = Recipe.objects.all()
    pp= {}
    for recipe in recipes:
        pp[recipe.id] = calculate_recipe_cost(recipe.id)
    for key, value in pp.items():
        pp[key] = round(value,2)   


    if request.method == 'POST':
        form = RecipePriceForm(request.POST)
        
        if form.is_valid():
            recipe = form.cleaned_data['recipe']
            sale_price= form.cleaned_data['sale_price']

    
            rp_instance, created = RecipePrice.objects.get_or_create(recipe=recipe)
            print(recipe.id)
            rp_instance.production_price = calculate_recipe_cost(recipe.id)
            rp_instance.sale_price = sale_price
            rp_instance.gain = sale_price - rp_instance.production_price if rp_instance.production_price != 0 else 0
            rp_instance.save()

        
            
            return redirect('success')
    else:
        form = RecipePriceForm()
    return render( request, 'Inventory/create_meal.html', context= {'form':form, 'production_prices': json.dumps(pp, cls=DjangoJSONEncoder)} )    


def create_recipe_view(request):

    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST)
        formset = RecipeIngredientFormset(request.POST)

        if recipe_form.is_valid() and formset.is_valid():
        
            recipe = recipe_form.save()
            instances= formset.save(commit=False)
            for instance in instances:
                instance.recipe = recipe
                instance.save()
            return redirect('success')
        else:
            
            print(formset.errors)     
    else:
        
        recipe_form = RecipeForm()
        formset = RecipeIngredientFormset()
    return render(request, 'Inventory/create_recipe.html', {'recipe_form': recipe_form, 'formset': formset})



def recipe_view(request):
    recipes = Recipe.objects.all()

    return render(request, 'Inventory/recipe_view.html', {'recipes':recipes} )

    
    

def stockformview(request):
    if request.method =='POST':
        form = StockForm(request.POST)

        if form.is_valid:
            form.save()
            return redirect('success')
    else:
        form = StockForm()
    return render(request, 'Inventory/stock_form.html', context={'stock_form':form} )  
    
def add_quantity_view(request):
    if request.method == 'POST':
        form = AddQuantityForm(request.POST)
        if form.is_valid():
            selected_food= form.cleaned_data['food']
            additional_quantity = form.cleaned_data['quantity']
            price= form.cleaned_data['price']
            selected_food.quantity += additional_quantity
            selected_food.buying_price += price
            selected_food.save()
                      


            return redirect('success')
    else:
        form = AddQuantityForm()

    return render( request, 'Inventory/add_quantity.html',context={'form':form})    

    

def sles(request):

    if request.method == 'POST':

        recipes = RecipePrice.objects.all()
        for recipe in recipes:
            recipe.production_price = calculate_recipe_cost(recipe.recipe_id)
            recipe.gain = recipe.sale_price - recipe.production_price 
            recipe.save()

        formset = SaleFormSet(request.POST)
   
        if formset.is_valid():
            
            for form in formset:

                selected_meal = form.cleaned_data['meal']
                meal_quantity = form.cleaned_data['quantity']

                recipe = get_recipe_id(selected_meal.id)
                ingredients = get_recipe_ingredient(recipe)

                try:
                    
                    for ingredient in ingredients:
                        total_stock_quantity_needed = ingredient.quantity * meal_quantity
                        new_quantity = Stock.objects.get(pk = ingredient.stock_id)
                    
                        if total_stock_quantity_needed > new_quantity.quantity:
                            raise ValueError("Insufficient quantity in stock. Please adjust your order.")
                    

                    calculate_new_buying_price(selected_meal.id, meal_quantity)
                    tpp = calculate_total_cost(selected_meal.id, meal_quantity)
                    tsp = calculate_total_sales(selected_meal.id, meal_quantity)
                    tg = calculate_total_gain(selected_meal.id, meal_quantity)
            
                    new_sale_instance = form.save(commit=False)

                    new_sale_instance.total_production_price = tpp
                    new_sale_instance.total_sale_price = tsp
                    new_sale_instance.total_gain = tg

                    new_sale_instance.save()

                
                    for ingredient in ingredients:
                        total_stock_quantity_needed = ingredient.quantity * meal_quantity
                        new_quantity = Stock.objects.get(pk = ingredient.stock_id)
                        new_quantity.quantity -= total_stock_quantity_needed
                        new_quantity.save()   

                
                except ValueError as e:
                    error_message = str(e)
                    messages.error(request, error_message)

            return redirect('sales')        

        
    else:
        formset = SaleFormSet()

    return render(request, 'Inventory/sales.html', context={'formset':formset})   





"""




   