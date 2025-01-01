from django.db import models
from django.utils import timezone
from django.utils.timezone import now

class Bill(models.Model):
    bill_id = models.AutoField(primary_key=True)
    pib = models.CharField(max_length=20, null=True, blank=True)
    store = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    municipality = models.CharField(max_length=100, null=True, blank=True)
    buyer_id = models.CharField(max_length=50, null=True, blank=True)
    asked = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cnt_type = models.CharField(max_length=50, null=True, blank=True)
    cnt_total = models.CharField(max_length=50, null=True, blank=True)
    ext = models.CharField(max_length=50, null=True, blank=True)
    cnt = models.CharField(max_length=50, null=True, blank=True)
    signed = models.CharField(max_length=100, null=True, blank=True)
    server_time = models.DateTimeField(null=True, blank=True)
    time_entry = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bill {self.bill_id} - {self.store}"

class BillSpec(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='specifications')
    gtin = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax_base_amnt = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    vat = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    label = models.CharField(max_length=10, null=True)
    time_entry = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.quantity} x {self.unit_price}"
    
# Create your models here.
class Article(models.Model):

    PRIORITY_CHOICES = [(i, str(i)) for i in range(1, 11)]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    category = models.CharField(max_length=100)
    priority = models.IntegerField(choices=PRIORITY_CHOICES)
    time_scheduled = models.DateTimeField(null=True, blank=True)
    time_entry = models.DateTimeField(auto_now_add=True)
    time_edit = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # class Meta:
    #     ordering = ['-created_at']

