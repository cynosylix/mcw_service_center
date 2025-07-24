from django.shortcuts import render,redirect
from django.shortcuts import render
import json
from django.core import serializers
from Owner.models import UsesDB
from .models import StockDB
from django.http import JsonResponse
from datetime import datetime
# Create your views here.
def SparePurchase_home(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Purchase Staff":
        
        usertable=UsesDB.objects.filter(id=user_id)
        stockdata=StockDB.objects.filter(shop=usertable[0].shop.id)
        stok=[]
        for i in stockdata:
            stok.append({"ItemCode":i.ItemCode,"ItemName":i.ItemName,"Category":i.Category,
                         "Supplier":i.Supplier,"Quantity":i.Quantity,"Unit":i.Unit,"Price":i.Price,
                         "Value":i.Value,"Status":i.Status})
        TotalItems=len(stockdata)
        LowStock=len(StockDB.objects.filter(shop=usertable[0].shop.id,Status="Low Stock"))
        OutofStock=len(StockDB.objects.filter(shop=usertable[0].shop.id,Status="Out of Stock"))

        data={"user":user_name,"TotalItems":TotalItems,"LowStock":LowStock,"OutofStock":OutofStock,"stockdata":stok}
        return render(request,"SparePurchaseHome.html",{'data': json.dumps(data)})
    else:return redirect("login")


def Attendance(request):
    return render(request,"Attendance.html")

def profile(request):
    return render(request,"profile.html")

def logout(request):
    request.session['user_id'] = "logout"
    request.session['user_name'] = "logout"
    request.session['user_position'] = "logout"
    return redirect("login")



def add_stock(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Purchase Staff"  or position=="Owner" or position=="Supervisor":
        if request.method == 'POST':
            try:
                # For form-data (files)
                userobj=UsesDB.objects.get(id=user_id)
                data = {
                    'stockid': request.POST.get('stockid'),
                    'ItemName': request.POST.get('name'),
                    'Category': request.POST.get('Category'),
                    'Supplier': request.POST.get('Supplier'),
                    'Quantity': int(request.POST.get('Quantity')),
                    'Unit': request.POST.get('Unit'),
                    'Price': int(request.POST.get('Price')),
                    'image': request.FILES.get('Photo')  # Handle file upload
                }
                Status="Out of Stock"
                quantity=int(data["Quantity"])
                if quantity==0:
                    Status="Out of Stock"
                elif quantity<4:
                    Status="Low Stock"
                elif quantity>3:
                    Status="In Stock"
                current_datetime = datetime.now()
                purch=f"userid={user_id},username={user_name},position={position},created At={current_datetime} , created new stock  , stockid={data['stockid']},ItemName={data['ItemName']},Category={data['Category']},Supplier={data['Supplier']},Quantity={data['Quantity']},Unit={data['Unit']},Price={data['Price']}"
                valu=int(data["Quantity"])*int(data["Price"])
                dbdata=StockDB.objects.filter(ItemCode=data['stockid'])
                if len(dbdata)==0:#add new
                    new_stock = StockDB.objects.create(
                        ItemCode=data['stockid'],
                        ItemName=data['ItemName'],
                        Category=data['Category'],
                        Supplier=data['Supplier'],
                        Quantity=data['Quantity'],
                        Unit=data['Unit'],
                        Price=data['Price'],
                        image=data['image'],  # File upload handled automatically
                        shop = userobj.shop,
                        Value=valu,
                        Status=Status,
                        PurchaseStatus=purch

                    )
                    
                    new_stock.save()  # Explicit save (though `create()` already does this)
                    return JsonResponse({'status': 'success', 'message': 'Item added!'})
                else:#updaate
                    # Determine which fields changed
                  
                    db_item = StockDB.objects.get(ItemCode=data['stockid'])
                    updates = {}
                    for field, new_value in data.items():
                      
                        if field!="stockid":   
                            current_value = getattr(db_item, field) 
                            if field=="image":
                                if None != new_value:
                                    if current_value != new_value:
                                        updates[field] = new_value
                            else:
                                if current_value != new_value:
                                    updates[field] = new_value
               
                    if int(data["Quantity"])==0:
                        if db_item.Status !="Out of Stock":
                            updates["Status"]="Out of Stock"
                    elif int(data["Quantity"])<4:
                        if db_item.Status !="Low Stock":
                            updates["Status"]="Low Stock"
                    elif int(data["Quantity"])>3:
                        if db_item.Status !="In Stock":
                            updates["Status"]="In Stock"
                    print(updates)
                    # Apply all updates in a single query
                    if updates:
                        StockDB.objects.filter(ItemCode=data['stockid']).update(**updates)

                    return JsonResponse({'status': 'success', 'message': 'Item added!'})
            
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    else:return redirect("login")