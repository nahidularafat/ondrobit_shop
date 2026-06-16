from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100,  unique=True)
    description = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name_plural = ' Categories'
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE,related_name='products' )
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock =models.PositiveBigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)   
    updated = models.DateTimeField(auto_now=True)   
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return self.name
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / ratings.count()
        return 0    

    class Rating(models.Model):
        product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
        user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
        rating = models.PositiveIntegerField(default=MinValueValidator(1), validators=[MaxValueValidator(5)])
        comment = models.TextField(blank=True, null=True)
        created = models.DateTimeField(auto_now_add=True)

        class Meta:
            unique_together = ('product', 'user')

        def __str__(self):
              return self.user.username + ' - ' + str(self.rating)
   