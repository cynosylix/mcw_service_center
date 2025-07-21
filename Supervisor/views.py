from django.shortcuts import render,redirect
import json
from Owner.models import UsesDB
from Spare_Purchase.models import StockDB
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from Supervisor.models import CustomerDB, JobCardDB, JobCardPartsDB, VehicleDB

def Supervisor_home(request):
    return render(request,"SupervisorHome.html")

# Create your views here.
def Supervisor_jobcard(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Supervisor":
        JobCardDBdata=JobCardDB.objects.all()[::-1]
        
        data={"JobCardDBdata":JobCardDBdata,"name":user_name}
        return render(request,"Supervisor_jobcard.html",data)

    else:return redirect("login")



def Supervisor_jobcard_create_pg(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Supervisor":
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
        
        return render(request,"jobcard_create_pg.html",{'data': json.dumps(data)})

    else:return redirect("login")
    

def Supervisor_single_jobcard(request,id):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Supervisor":
            JobCardDBdata=JobCardDB.objects.filter(id=id)
            if len(JobCardDBdata)>0:
                Jo=JobCardDB.objects.get(id=id)
                parts=JobCardPartsDB.objects.filter(JobCart=Jo)

                PartsTotal=0
                for i in parts:
                    PartsTotal=PartsTotal+(int(i.part_obj.Price)*int(i.quantity))
                labercost=float(Jo.labor_hours)*float(Jo.hourly_rate)
                

                data={"name":user_name,"JobCardDBdata":JobCardDBdata[0],"parts":parts,"PartsTotal":PartsTotal,"labercost":labercost}
                return render(request,"Supervisor_single_jobcard.html",data)
            else:return redirect('Supervisor_jobcard')
    else:return redirect("login")

@csrf_exempt  # Only if you're having CSRF issues during development
def returnparts(request):
    partsdata=[]
    p=StockDB.objects.all()
    for i in p:
        partsdata.append({"name":i.ItemName,"id":i.id,"quantity":i.Quantity,"Price":i.Price})
    return JsonResponse({'success': True,'parts': partsdata})

def is_valid_email(email):
    # More comprehensive regex pattern for email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None
@csrf_exempt  # Only if you're having CSRF issues during development
def create_job_card(request):
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
            print(job_data)
            # Create job card model here
            staffbj=UsesDB.objects.get(id=int(job_data['assigned_staff']))
            JobCardobj=JobCardDB.objects.create(customer=cusobj,vehicle=VehicleDBobj,job_type=job_data['type'],received_date=job_data['received_date'],
                                                delivery_date=job_data['delivery_date'],assigned_staff=staffbj,work_description=job_data['description']
                                                ,status=job_data['status'],labor_hours=job_data['labor_hours'],hourly_rate=job_data['hourly_rate'],
                                                discount=job_data['discount'],TotalPayent=job_data['estimated_total'])

            
            # Process parts data
            parts_data = data.get('parts', [])
            # Create job card parts relationships here

            for i in parts_data:
                part_obj=StockDB.objects.get(id=int(i['id']))
                JobCardPartsDB.objects.create(JobCart=JobCardobj,part_obj=part_obj,quantity=i["quantity"])
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            print(str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)