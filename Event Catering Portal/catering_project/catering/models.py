from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=200)
    # विवरण (Description) के लिए फ़ील्ड जोड़ा गया ताकि home.html में आ रहा विवरण डायनामिक हो सके
    description = models.TextField(blank=True, null=True) 
    price = models.IntegerField()
    image = models.ImageField(upload_to='services/', blank=True, null=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    guests = models.IntegerField()
    address = models.TextField()
    mov_contact_no=models.CharField(max_length=15,blank=True,null=True)
    
    # अमाउंट और स्टेटस ट्रैकिंग फ़ील्ड्स
    amount = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default="Pending") # Pending, Confirmed, Cancelled
    
    # QR कोड फ़ील्ड (blank=True और null=True ताकि बुकिंग के समय एरर न आए)
    qr_code = models.ImageField(upload_to='qr/', blank=True, null=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} ({self.service.name})"
    
class Order(models.Model):
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    guests = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)