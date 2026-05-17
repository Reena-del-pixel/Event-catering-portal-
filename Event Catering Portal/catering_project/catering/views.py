import qrcode
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import Service, Booking


# --- LOGIN PAGE ---
def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")
    return render(request, 'login.html')

# --- REGISTER PAGE ---
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already exists! Try another one.")
            return render(request, 'register.html')
        
        User.objects.create_user(username=u, password=p)
        messages.success(request, "Account created! Now you can login.")
        return redirect('login')
        
    return render(request, 'register.html')


# --- HOME PAGE ---
@login_required(login_url='login')
def home(request):
    if not Service.objects.exists():
        Service.objects.bulk_create([
            Service(name="Wedding Buffet", price=50000, description="Delicious wedding buffet."),
            Service(name="Cocktail Evening", price=50000, description="Luxury cocktail evenings."),
            Service(name="New Year Party", price=50000, description="Celebrate New Year."),
            Service(name="Birthday Party", price=20000, description="Special birthday party menus."),
            Service(name="Award Ceremony", price=50000, description="Elegant catering setup."),
            Service(name="Festive Gathering", price=15000, description="Traditional festive catering."),
            Service(name="Corporate Event", price=35000, description="Professional corporate event."),
            Service(name="Kitty Party", price=15000, description="Perfect custom menu."),
        ])

    services = Service.objects.all()
    return render(request, 'home.html', {'services': services})


# --- BOOKING PAGE (FIXED) ---
@login_required(login_url='login')
def booking(request, event_type):
    pricing_data = {
        'wedding': {'name': 'Wedding Buffet', 'price': 50000},
        'birthday': {'name': 'Birthday Party', 'price': 20000},
        'corporate': {'name': 'Corporate Event', 'price': 35000},
        'kitty': {'name': 'Kitty Party', 'price': 15000},
        'cocktail evening': {'name': 'cocktail evening', 'price': 50000},
        'new year party': {'name': 'New Year Party', 'price': 50000},
        'award ceremony': {'name': 'Award Ceremony', 'price': 50000},
        'festive gathering': {'name': 'festive gathering', 'price': 15000},
    }
    
    selected_service = pricing_data.get(event_type.lower(), {'name': 'Custom Event', 'price': 0})

    if request.method == 'POST':
        guests_count = int(request.POST.get('guests', 1))
        total_amount = selected_service['price'] 

        service_instance, created = Service.objects.get_or_create(
            name=selected_service['name'],
            defaults={'price': total_amount, 'description': selected_service['name']}
        )

        # [FIXED] यहाँ आपके नए मॉडल्स के अनुसार 'mov_contact_no' फ़ील्ड का नाम जोड़ दिया गया है
        b = Booking.objects.create(
            user=request.user,
            service=service_instance,  
            date=request.POST.get('date'),
            guests=guests_count,
            address=request.POST.get('address'),
            amount=total_amount,
            mov_contact_no=request.POST.get('contact_number') # HTML फॉर्म से आने वाला नंबर यहाँ स्टोर होगा
        )
        return redirect('payment', id=b.id)

    context = {
        'service_name': selected_service['name'],
        'service_price': selected_service['price'],
    }
    return render(request, 'booking.html', context)
   

# --- PAYMENT PAGE ---
@login_required(login_url='login')
def payment(request, id):
    booking_item = get_object_or_404(Booking, id=id, user=request.user)
    
    if request.method == 'POST':
        updated_date = request.POST.get('edit_date')
        updated_guests = request.POST.get('edit_guests')
        
        if updated_date:
            booking_item.date = updated_date
        if updated_guests:
            booking_item.guests = int(updated_guests)
            
        booking_item.save()  
        return redirect('op_page', id=booking_item.id)
        
    return render(request, 'payment.html', {'booking': booking_item})


# --- QR GENERATION PAGE ---
@login_required(login_url='login')
def op_page(request, id):
    booking = get_object_or_404(Booking, id=id)
    service_display_name = booking.service.name if hasattr(booking.service, 'name') else str(booking.service)

    data = f"Booking ID: {booking.id} | Service: {service_display_name} | Status: Confirmed"
    qr = qrcode.make(data)

    qr_dir = os.path.join(settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else 'media', 'qr')
    os.makedirs(qr_dir, exist_ok=True)
    
    file_name = f"qr_{booking.id}.png"
    path = os.path.join(qr_dir, file_name)
    qr.save(path)

    booking.qr_code = f"qr/{file_name}"
    booking.status = "Confirmed"  
    booking.save()

    return render(request, 'qr.html', {'booking': booking})


# --- VIEW DETAILS FOR AJAX ---
@login_required(login_url='login')
def get_order_details(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    service_name = booking.service.name if hasattr(booking.service, 'name') else str(booking.service)
    
    return JsonResponse({
        'service_name': service_name,
        'date': str(booking.date),
        'guests': booking.guests,
        'amount': str(booking.amount),
        'address': booking.address
    })


# --- MY BOOKINGS LIST ---
@login_required(login_url='login')
def my_bookings(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-id')
    return render(request, 'my_bookings.html', {'bookings': user_bookings})

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.status = 'Cancelled'
    booking.save()
    messages.success(request, f"Booking #{booking_id} successfully cancelled.")
    return redirect('my_bookings')

def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        new_date = request.POST.get('date')
        new_guests = request.POST.get('guests')
        if new_date:
            booking.date = new_date
        if new_guests:
            booking.guests = new_guests
        booking.save()
        messages.success(request, f"Booking #{booking_id} successfully updated.")
        return redirect('my_bookings')
    return render(request, 'update_booking.html', {'booking': booking})

@login_required(login_url='login')
def profile(request):
    return render(request, 'profile.html')

def about_us(request):
    return render(request, 'about.html')

def contact_us(request):
    return render(request, 'contact.html')

def logout_page(request):
    logout(request)
    return redirect('login')