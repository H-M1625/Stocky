from django import forms
from .models import Stock, Recipe, RecipeIngredient, RecipePrice, Sales




class StockForm(forms.ModelForm):
    class Meta:
        model= Stock
        fields = ['food', 'quantity', 'measurement_unit', 'buying_price']



class AddQuantityForm(forms.Form):
    food = forms.ModelChoiceField(queryset = Stock.objects.all(), label='Select a food')
    quantity = forms.IntegerField(min_value=1, label="Quantity")
    price = forms.DecimalField(min_value=1, label="Buying Price")



class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model= RecipeIngredient
        fields= ['stock','quantity']
           
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.all()
        
RecipeIngredientFormset = forms.inlineformset_factory(Recipe, RecipeIngredient, form=RecipeIngredientForm, extra=1, can_delete=False)

class RecipeForm(forms.ModelForm):
    class Meta:
        model=Recipe
        fields= ['name']          


class RecipePriceForm(forms.ModelForm):
    class Meta:
        model= RecipePrice
        fields= ['recipe','sale_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipe'].queryset= Recipe.objects.all()


class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ["meal", "quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal'].queryset= RecipePrice.objects.all()


SaleFormSet = forms.formset_factory(SalesForm)





class MealForm(forms.ModelForm):
    class Meta:
        model = RecipePrice
        fields = ['sale_price']

        


#class RepasForm(forms.Form):
     #meal_id = forms.IntegerField(widget=forms.HiddenInput())
     #sale_price = forms.DecimalField(label='Sale Price', max_digits=10, decimal_places=2)
    