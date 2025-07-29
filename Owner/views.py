from django.shortcuts import render,redirect
from django.contrib import messages
from Owner.models import UsesDB, remindersDB
from Spare_Purchase.models import StockDB
from django.http import JsonResponse
import json
from django.db.models import Q
from Supervisor.models import CustomerDB, JobCardDB, JobCardPartsDB, VehicleDB
import re
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Max
# Create your views here.
def login(request):
    return render(request,"login.html")

def Owner_home(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position']

    current_month = timezone.now().month
    current_year = timezone.now().year
    
    jobs = JobCardDB.objects.filter(
        created_at__month=current_month,
        created_at__year=current_year
    ).order_by('-created_at')

    jobsYear = JobCardDB.objects.filter(
        created_at__year=current_year
    ).order_by('-created_at')
    Total_Earnings=0
    Pending_Payments=0
    Completed_Payments=0
    Tasks =len(jobs)
    Pending_jon=0
    for i in jobs:
        Total_Earnings+=float(i.TotalPayent)
        Completed_Payments+=float(i.paydPayent)
        Pending_Payments+=float(i.TotalPayent)-float(i.paydPayent)
        if i.status=="Pending":
            Pending_jon+=1
    Earnings_Annual=0
    for i in jobsYear:
        Earnings_Annual+=float(i.TotalPayent)
    outoffstock=len(StockDB.objects.filter(Status="Out of Stock"))
    lowstock=len(StockDB.objects.filter(Status="Low Stock"))

    start_date = timezone.now() - timedelta(days=1)
    # Get unique customers with recent job cards
    # ✅ Correct
    last_customers = JobCardDB.objects.annotate(
        last_job_date=Max('created_at')
    ).order_by('-created_at')[:5]  # Latest 8

    users=UsesDB.objects.all()


    userobj=UsesDB.objects.get(id=user_id)
    remindersobj=remindersDB.objects.filter(assignedto=userobj)
    reminders=[]
    today = date.today()  # Returns datetime.date(2025, 7, 29)
    formatted_date = today.strftime("%Y-%m-%d")  # "2025-07-29"
    
    for i in remindersobj:
        if i.remindDate !=None:
            if str(i.remindDate)==str(formatted_date):
                reminders.append(i)
    reminderslen=len(reminders)
    print(reminders)
    data={"user":user_name,"Total_Earnings":Total_Earnings,"Pending_Payments":Pending_Payments,"Completed_Payments":Completed_Payments,
          "Tasks":Tasks,"Earnings_Annual":Earnings_Annual,"Pending_jon":Pending_jon,"outoffstock":outoffstock,"lowstock":lowstock,
          "last_customers":last_customers,"users":users,"reminderslen":reminderslen,"reminders":reminders}
    return render(request,"OwnerHome.html",data)

def OwnerCustomerPg(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position']
    Active_Customers=0
    New_This_Month=0
    if position=="Owner":
        data=JobCardDB.objects.all()[::-1]
        Total_Customers=len(data)
        for i in data:
            if i.status!="Completed":
                Active_Customers+=1
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        jobs = JobCardDB.objects.filter(
            created_at__month=current_month,
            created_at__year=current_year
        ).order_by('-created_at')
        New_This_Month=len(jobs)

        userobj=UsesDB.objects.get(id=user_id)
        remindersobj=remindersDB.objects.filter(assignedto=userobj)
        reminders=[]
        today = date.today()  # Returns datetime.date(2025, 7, 29)
        formatted_date = today.strftime("%Y-%m-%d")  # "2025-07-29"
        
        for i in remindersobj:
            if i.remindDate !=None:
                if str(i.remindDate)==str(formatted_date):
                    reminders.append(i)
        reminderslen=len(reminders)
        send={"user":user_name,"Total_Customers":Total_Customers,"Active_Customers":Active_Customers,"New_This_Month":New_This_Month,"data":data,
              "reminders":reminders,"reminderslen":reminderslen}
        return render(request,"OwnerCustomerPg.html",send)
    else:return redirect("login")
    

def Owner_jobcard_create_pg(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Owner":
        usertable=UsesDB.objects.all()
        worker=[]
        stock=[]
        for i in usertable:
            if i.position!="Owner" and i.position!="Supervisor" and i.position!="Purchase Staff":
                worker.append({"id":i.id,"name":i.name,"position":i.position,})
        available_items = StockDB.objects.filter(Q(Status='In Stock') | Q(Status='Low Stock'))
        for i in available_items:
            stock.append({"id":i.id,"name":i.ItemName,"quantity":i.Quantity,"price":i.Price})
        

        
        data={"worker":worker,"stock":stock,"user_name":user_name,"user_id":user_id}
        
        return render(request,"Owner_jobcard_create_pg.html",{'data': json.dumps(data)})

    else:return redirect("login")
    # return render(request,"Owner_jobcard_create_pg.html")
def JobCardpg(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Owner":
        JobCardDBdata=JobCardDB.objects.all()[::-1]
        
        userobj=UsesDB.objects.get(id=user_id)
        remindersobj=remindersDB.objects.filter(assignedto=userobj)
        reminders=[]
        today = date.today()  # Returns datetime.date(2025, 7, 29)
        formatted_date = today.strftime("%Y-%m-%d")  # "2025-07-29"
        
        for i in remindersobj:
            if i.remindDate !=None:
                if str(i.remindDate)==str(formatted_date):
                    reminders.append(i)
        reminderslen=len(reminders)
        data={"JobCardDBdata":JobCardDBdata,"name":user_name,"reminders":reminders,"reminderslen":reminderslen}
        return render(request,"JobCard.html",data)

    else:return redirect("login")
    # return render(request,"JobCard.html")

def view_single_job(request,id):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Owner":
            JobCardDBdata=JobCardDB.objects.filter(id=id)
            if len(JobCardDBdata)>0:
                Jo=JobCardDB.objects.get(id=id)
                parts=JobCardPartsDB.objects.filter(JobCart=Jo)

                PartsTotal=0
                for i in parts:
                    PartsTotal=PartsTotal+(int(i.part_obj.Price)*int(i.quantity))
                labercost=float(Jo.labor_hours)*float(Jo.hourly_rate)
                
                worker=[]
                w=UsesDB.objects.all()
                for i in w:
                    if i.position!="Owner":
                        worker.append({"id":i.id,"name":i.name,"position":i.position})

                paymentbalance=JobCardDBdata[0].TotalPayent-JobCardDBdata[0].paydPayent
                
                userobj=UsesDB.objects.get(id=user_id)
                remindersobj=remindersDB.objects.filter(assignedto=userobj)
                reminders=[]
                today = date.today()  # Returns datetime.date(2025, 7, 29)
                formatted_date = today.strftime("%Y-%m-%d")  # "2025-07-29"
                
                for i in remindersobj:
                    if i.remindDate !=None:
                        if str(i.remindDate)==str(formatted_date):
                            reminders.append(i)
                reminderslen=len(reminders)
                data={"name":user_name,"JobCardDBdata":JobCardDBdata[0],"parts":parts,"PartsTotal":PartsTotal,"labercost":labercost,"worker":worker,
                      "paymentbalance":paymentbalance,"reminders":reminders,"reminderslen":reminderslen}
                return render(request,"view_single_job.html",data)
            else:return redirect('JobCardpg')
    else:return redirect("login")
    # return render(request,"view_single_job.html")

def ViewStaffPg(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    userobj=UsesDB.objects.get(id=user_id)
    remindersobj=remindersDB.objects.filter(assignedto=userobj)
    reminders=[]
    today = date.today()  # Returns datetime.date(2025, 7, 29)
    formatted_date = today.strftime("%Y-%m-%d")  # "2025-07-29"
    
    for i in remindersobj:
        if i.remindDate !=None:
            if str(i.remindDate)==str(formatted_date):
                reminders.append(i)
    reminderslen=len(reminders)
    data={"reminders":reminders,"reminderslen":reminderslen,"user_name":user_name}

    return render(request,"view_staff.html",data)
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
                        return redirect("Supervisor_jobcard")
                    
                else:
                    messages.error(request, 'Account is not active')
            else:
                messages.error(request, 'Invalid password')
        except UsesDB.DoesNotExist:
            messages.error(request, 'User does not exist')
       
    return render(request,"login.html")

def profile(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position']
    userobjd=UsesDB.objects.filter(id=user_id)
    userobj=UsesDB.objects.get(id=user_id)
    remindersobj=remindersDB.objects.filter(assignedto=userobj)
    reminders=[]
    today = date.today()  # Returns datetime.date(2025, 7, 29)
    formatted_date = today.strftime("%Y-%m-%d")  # "2025-07-29"
    
    for i in remindersobj:
        if i.remindDate !=None:
            if str(i.remindDate)==str(formatted_date):
                reminders.append(i)
    reminderslen=len(reminders)
    data={"user":user_name,"userobj":userobjd,"reminders":reminders,"reminderslen":reminderslen}

    return render(request,"owner_profile.html",data)



def is_valid_email(email):
    # More comprehensive regex pattern for email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None
def owner_profileUpdate(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if request.method == 'POST':
        userobj=UsesDB.objects.get(id=user_id)

        # Get data from POST request
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        new_password = request.POST.get('new_password')
        current_password = request.POST.get('current_password')
        
        print(email)
        print(mobile)
        print(new_password)
        if email and is_valid_email(email):
            # Valid email
            userobj.email=email
        userobj.mobile=mobile
        a='Profile updated successfully!'
        if len(new_password)!=0:
            if userobj.password==current_password:
                userobj.password=new_password
            else:
                a=a + "  incorect current password ."
        userobj.save()
        
        messages.success(request, a)
        return redirect('ownerprofile')
    
    return redirect('ownerprofile')



def is_valid_email(email):
    # More comprehensive regex pattern for email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None
@csrf_exempt  # Only if you're having CSRF issues during development
def owner_create_job_card(request):
    print(">...........................")
    if request.method == 'POST':
        user_id=request.session['user_id'] 
        userobj=UsesDB.objects.get(id=user_id)
        try:
            data = json.loads(request.body)
            
            # Process customer data
            customer_data = data.get('customer', {})
            em="dummy@gmail.com"
            email = customer_data['email']
            if email and is_valid_email(email):
                # Valid email
                em=email
          
            # Create or update customer model here
            cusobj=CustomerDB.objects.create(createdby=userobj,name=customer_data["name"],phone=customer_data['phone'],email=em,address=customer_data["address"],
                                             customernotes=customer_data["notes"])
            # Process vehicle data
            vehicle_data = data.get('vehicle', {})
            # Create or update vehicle model here
            VehicleDBobj=VehicleDB.objects.create(customer=cusobj,registration_no=vehicle_data['registration'],model=vehicle_data['model'],make=vehicle_data['make'],
                                                  chassis_no=vehicle_data['chassis_no'],engine_no=vehicle_data['engine_no'],petrol_level=vehicle_data['petrol_level'],
                                                  notes=vehicle_data['notes'])
            
            # Process job card data
            job_data = data.get('job', {})
            # print(job_data)
            # Create job card model here
            staffbj=UsesDB.objects.get(id=int(job_data['assigned_staff']))
            JobCardobj=JobCardDB.objects.create(customer=cusobj,vehicle=VehicleDBobj,job_type=job_data['type'],received_date=job_data['received_date'],
                                                delivery_date=job_data['delivery_date'],assigned_staff=staffbj,work_description=job_data['description']
                                                ,status=job_data['status'],labor_hours=job_data['labor_hours'],hourly_rate=job_data['hourly_rate'],
                                                discount=job_data['discount'],TotalPayent=job_data['estimated_total'])

            
            # Process parts data
            parts_data = data.get('parts', [])
            # Create job card parts relationships here
            # stok=StockDB.objects.get(ItemCode=data['stockid'])
            # stok.Quantity=stok.Quantity-int(data['Quantity'])
            # stok.save()
            for i in parts_data:
                part_obj=StockDB.objects.get(id=int(i['id']))
                print(part_obj.Quantity,int(i["quantity"]))
                part_obj.Quantity=part_obj.Quantity-int(i["quantity"])
                part_obj.save()   
                JobCardPartsDB.objects.create(JobCart=JobCardobj,part_obj=part_obj,quantity=i["quantity"])
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            print(str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt  # Only if you're having CSRF issues during development
def reminders(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            data = json.loads(request.body)

            # Validate required fields
            if not all([data.get('title'), data.get('date'), data.get('staff_id')]):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
            
            title=data.get('title')
            date=data.get('date')
            staff_id=data.get('staff_id')
            notes=data.get('notes')
            createdby=UsesDB.objects.get(id=user_id)
            assignedto=UsesDB.objects.get(id=staff_id)

            remindersDB.objects.create(Title=title,note=notes,createdby=createdby,assignedto=assignedto,remindDate=date)
            return JsonResponse({
                'success': True,
                'message': 'Reminder created successfully'
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)