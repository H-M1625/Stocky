from django.db import models
from django.utils import timezone
from datetime import datetime
# Create your models here.


class Stock(models.Model):
    food = models.CharField(max_length = 100, verbose_name = " Food Name")
    quantity = models.DecimalField(max_digits=10,decimal_places= 0, default = 0)
    measurement_unit = models.CharField(max_length = 50)
    buying_price = models.DecimalField(max_digits=10,decimal_places= 2, default = 0.0)
    price_per_unit = models.DecimalField(max_digits=10,decimal_places= 5, default = 0.0)
    

    def save(self, *args, **kwargs):
        if self.quantity != 0:
            self.price_per_unit = self.buying_price / self.quantity
        else:
            self.price_per_unit = 0.0
        super().save(*args, **kwargs) 
    
    def __str__(self):
        return f"{self.food}, In stock: {self.quantity} {self.measurement_unit}" 
    



class Recipe(models.Model):
    name = models.CharField(max_length = 100)

    def __str__(self):
        return f"{self.name}" 
    
    class Meta:
        verbose_name = "Name of Recipe"



class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete= models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete= models.CASCADE)
    quantity = models.DecimalField(max_digits=10,decimal_places= 2)

    def __str__(self):
        return f"{self.recipe} {self.stock}, {self.quantity} needed for this recipe "
     

class RecipePrice(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete= models.CASCADE)
    production_price = models.DecimalField(max_digits=10, decimal_places=2 , default = 0.0)
    sale_price = models.DecimalField(max_digits = 10, decimal_places=2,default = 0.0)
    gain = models.DecimalField(max_digits = 10, decimal_places=2, default = 0.0)


    def __str__(self):
        return f" {self.recipe} ({self.sale_price}€) "
    



class Sales(models.Model):
    meal= models.ForeignKey(RecipePrice, on_delete=models.CASCADE)
    quantity = models.IntegerField(default = 0)
    sale_time = models.DateTimeField(auto_now=True)
    total_production_price = models.DecimalField(max_digits=10, decimal_places=2 , default = 0.0)
    total_sale_price = models.DecimalField(max_digits=10, decimal_places=2 , default = 0.0)
    total_gain = models.DecimalField(max_digits=10, decimal_places=2 , default = 0.0)

    def __str__(self):
        sale_time_local = timezone.localtime(self.sale_time)
        sale_time = sale_time_local.strftime("%d-%m-%Y at %H:%M" )

        return f" {self.quantity} - {self.meal} ordered the {sale_time} "
    
    class Meta:
        verbose_name = "Sales of the day"