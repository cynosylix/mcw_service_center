from django.shortcuts import render,redirect
from django.contrib import messages
from Owner.models import UsesDB
from Spare_Purchase.models import StockDB
from django.http import JsonResponse
import json

# Create your views here.
def login(request):
    return render(request,"login.html")

def Owner_home(request):
    return render(request,"OwnerHome.html")

def OwnerCustomerPg(request):
    return render(request,"OwnerCustomerPg.html")

def JobCardpg(request):
    return render(request,"JobCard.html")

def view_single_job(request):
    return render(request,"view_single_job.html")

def ViewStaffPg(request):
    user_id = request.session['user_id'] 
    user_name = request.session['user_name'] 
    position = request.session['user_position'] 
    
    if position == "Owner":
        user_data = UsesDB.objects.exclude(position='Owner')
        print(user_data)
        
        context = {
            'user_data': user_data,
            'user_name': user_name,
            'position': position
        }
        return render(request, "view_staff.html", context)
    else:
        # Handle non-owner access if needed
        return render(request, "view_staff.html")






def StockPg(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Owner":
        
        usertable=UsesDB.objects.filter(id=user_id)
        stockdata=StockDB.objects.all()
        stok=[]
        TotalstokValue=0
        for i in stockdata:
            stok.append({"ItemCode":i.ItemCode,"ItemName":i.ItemName,"Category":i.Category,
                         "Supplier":i.Supplier,"Quantity":i.Quantity,"Unit":i.Unit,"Price":i.Price,
                         "Value":i.Value,"Status":i.Status})
            TotalstokValue+=int(i.Value)
        TotalItems=len(stockdata)
        LowStock=len(StockDB.objects.filter(shop=usertable[0].shop.id,Status="Low Stock"))
        OutofStock=len(StockDB.objects.filter(shop=usertable[0].shop.id,Status="Out of Stock"))

        data={"user":user_name,"TotalItems":TotalItems,"LowStock":LowStock,"OutofStock":OutofStock,"stockdata":stok,"TotalstokValue":TotalstokValue}
        return render(request,"Stock.html",{'data': json.dumps(data)})
    else:return redirect("login")



def login_btn(request):
    if request.method == 'POST':
        UsName = request.POST.get('username')
        password = request.POST.get('password')
        # ,password=password
        try:
            user = UsesDB.objects.get(name=UsName)
            if user.password == password:  # Or use check_password if hashed
                if user.Status == 'Active':
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    request.session['user_position'] = user.position
                    if user.position=="Owner":
                        return redirect("OwnerHome")
                    elif user.position=="Purchase Staff":
                        return redirect("SparePurchase_home")
                    elif user.position=="Supervisor":
                        return redirect("Supervisor_home")
                    
                else:
                    messages.error(request, 'Account is not active')
            else:
                messages.error(request, 'Invalid password')
        except UsesDB.DoesNotExist:
            messages.error(request, 'User does not exist')
       
    return render(request,"login.html")
