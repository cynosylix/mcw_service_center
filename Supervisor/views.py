from django.shortcuts import render,redirect
import json
from Owner.models import UsesDB
from Spare_Purchase.models import StockDB
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from Supervisor.models import CustomerDB, JobCardDB, JobCardPartsDB, VehicleDB, Attendance
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
import json

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

# def attendance_page(request):
#     user_id=request.session['user_id'] 
#     user_name=request.session['user_name'] 
#     position=request.session['user_position'] 
#     if position == "Supervisor":
#         return render(request, "attendance.html", {"user_name": user_name})
#     else:
#         return redirect("login")

def api_employees(request):
    if request.method == "GET":
        employees = UsesDB.objects.filter(position__in=["Mechanic", "Senior Mechanic", "Helper", "Other"])  # Adjust positions as needed
        employee_list = [{"id": emp.id, "name": emp.name} for emp in employees]
        return JsonResponse(employee_list, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)





    
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
                
                worker=[]
                w=UsesDB.objects.all()
                for i in w:
                    if i.position!="Owner":
                        worker.append({"id":i.id,"name":i.name,"position":i.position})
                data={"name":user_name,"JobCardDBdata":JobCardDBdata[0],"parts":parts,"PartsTotal":PartsTotal,"labercost":labercost,"worker":worker}
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


@csrf_exempt  # Only if you're having CSRF issues during development
def update_job_card(request):
    
    try:
        # Get the job card to update
        job_card_id = request.POST.get('job_card_id')
        job_card = JobCardDB.objects.get(id=job_card_id)

        up=""

        
        # Update basic job card info
        # job_card.status = request.POST.get('status', job_card.status)
        # job_card.paymentStatus = request.POST.get('payment_status', job_card.paymentStatus)
        # job_card.received_date = request.POST.get('received_date', job_card.received_date)
        # job_card.delivery_date = request.POST.get('delivery_date', job_card.delivery_date)
        # job_card.work_description = request.POST.get('work_description', job_card.work_description)
        # job_card.labor_hours = float(request.POST.get('labor_hours', job_card.labor_hours))
        # job_card.hourly_rate = float(request.POST.get('hourly_rate', job_card.hourly_rate))
        # job_card.discount = float(request.POST.get('discount', job_card.discount))
        
        # # Update customer info
        # customer = job_card.customer
        # customer.name = request.POST.get('customer_name', customer.name)
        # customer.phone = request.POST.get('customer_phone', customer.phone)
        # customer.email = request.POST.get('customer_email', customer.email)
        # customer.address = request.POST.get('customer_address', customer.address)
        # customer.customernotes = request.POST.get('customer_notes', customer.customernotes)
        # customer.save()
        
        # # Update vehicle info
        # vehicle = job_card.vehicle
        # vehicle.registration_no = request.POST.get('registration_no', vehicle.registration_no)
        # vehicle.model = request.POST.get('vehicle_model', vehicle.model)
        # vehicle.chassis_no = request.POST.get('chassis_no', vehicle.chassis_no)
        # vehicle.engine_no = request.POST.get('engine_no', vehicle.engine_no)
        # vehicle.petrol_level = request.POST.get('petrol_level', vehicle.petrol_level)
        # vehicle.notes = request.POST.get('vehicle_notes', vehicle.notes)
        # vehicle.save()
        
        # Handle parts - first clear existing parts
        # JobCardPart.objects.filter(job_card=job_card).delete()
        
        # # Add new parts from the form
        # parts_data = json.loads(request.POST.get('parts', '[]'))
        # for part_data in parts_data:
        #     try:
        #         part = Part.objects.get(id=part_data['part_id'])
        #         JobCardPart.objects.create(
        #             job_card=job_card,
        #             part=part,
        #             quantity=int(part_data['quantity']),
        #             price=float(part_data['price'])
        #         )
        #     except Part.DoesNotExist:
        #         continue  # Skip if part doesn't exist
        
        # # Recalculate total payment (adjust according to your logic)
        # parts_total = sum(jp.price * jp.quantity for jp in job_card.jobcardpart_set.all())
        # labor_cost = job_card.labor_hours * job_card.hourly_rate
        # discount_amount = (parts_total + labor_cost) * (job_card.discount / 100)
        # job_card.TotalPayent = (parts_total + labor_cost) - discount_amount
        # job_card.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Job card updated successfully',
            'total_payment': job_card.TotalPayent
        })
        
    # except JobCard.DoesNotExist:
    #     return JsonResponse({'success': False, 'message': 'Job card not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

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



def supervisor_view_stock(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if position=="Supervisor":
        
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
        # return render(request,"Stock.html",{'data': json.dumps(data)})
    return render(request, "Supervisor_view_stock.html",{'data': json.dumps(data)})



from django.views.decorators.http import require_http_methods
from datetime import date, datetime




def attendance_page(request):
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    position = request.session.get('user_position')
    if position == "Supervisor":
        return render(request, "attendance.html", {"user_name": user_name})
    return redirect("login")


@require_http_methods(["GET"])
def attendance_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
   
    try:
        attendance_data = []
        employees = UsesDB.objects.exclude(position='Owner').exclude(position='Supervisor')
        
        for employee in employees:
            # Get or create attendance record
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                defaults={
                    'morning_status': 'absent',
                    'afternoon_status': 'absent',
                    'day_status': 'absent'
                }
            )
            
            attendance_data.append({
                'id': attendance.id,
                'employee_id': employee.id,
                'employee_name': employee.name,
                'position': employee.position,
                'date': attendance.date,
                
                # Morning data
                'morning_check_in': attendance.morning_check_in.isoformat()[:5] if attendance.morning_check_in else None,
                'morning_check_out': attendance.morning_check_out.isoformat()[:5] if attendance.morning_check_out else None,
                'morning_status': attendance.morning_status,
                'morning_remarks': attendance.morning_remarks,
                
                # Afternoon data
                'afternoon_check_in': attendance.afternoon_check_in.isoformat()[:5] if attendance.afternoon_check_in else None,
                'afternoon_check_out': attendance.afternoon_check_out.isoformat()[:5] if attendance.afternoon_check_out else None,
                'afternoon_status': attendance.afternoon_status,
                'afternoon_remarks': attendance.afternoon_remarks,
                
                # Overtime data
                'overtime_check_in': attendance.overtime_check_in.isoformat()[:5] if attendance.overtime_check_in else None,
                'overtime_check_out': attendance.overtime_check_out.isoformat()[:5] if attendance.overtime_check_out else None,
                'overtime_hours': float(attendance.overtime_hours),
                'overtime_approved': attendance.overtime_approved,
                'overtime_remarks': attendance.overtime_remarks,
                
                # Summary data
                'total_working_hours': float(attendance.total_working_hours),
                'late_hours': float(attendance.late_hours),
                'day_status': attendance.day_status,
                'daily_remarks': attendance.daily_remarks,
            })
            
        return JsonResponse(attendance_data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

from datetime import datetime
@csrf_exempt
def update_attendance(request, attendance_id):
    """Update attendance record"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method == "PATCH":
        try:
            attendance = Attendance.objects.get(pk=attendance_id)
            data = json.loads(request.body)

            def parse_time(time_str):
                if time_str:
                    return datetime.strptime(time_str, '%H:%M').time()
                return None
            
            # Update morning session
            if 'morning_check_in' in data:
                attendance.morning_check_in = parse_time(data['morning_check_in'])
            if 'morning_check_out' in data:
                attendance.morning_check_out = parse_time(data['morning_check_out'])
            if 'morning_status' in data:
                attendance.morning_status = data['morning_status']
                
            # Update afternoon session
            if 'afternoon_check_in' in data:
                attendance.afternoon_check_in = parse_time(data['afternoon_check_in'])
            if 'afternoon_check_out' in data:
                attendance.afternoon_check_out = parse_time(data['afternoon_check_out'])
            if 'afternoon_status' in data:
                attendance.afternoon_status = data['afternoon_status']
                
            # Update overtime session
            if 'overtime_check_in' in data:
                attendance.overtime_check_in = parse_time(data['overtime_check_in'])
            if 'overtime_check_out' in data:
                attendance.overtime_check_out = parse_time(data['overtime_check_out'])
            if 'overtime_approved' in data:
                attendance.overtime_approved = data['overtime_approved']
            if 'overtime_remarks' in data:
                attendance.overtime_remarks = data['overtime_remarks']
            
            # Recalculate totals and save
            attendance.calculate_working_hours()
            attendance.save()
            
            # Return updated data
            return JsonResponse({
                'id': attendance.id,
                'total_working_hours': float(attendance.total_working_hours),
                'late_hours': float(attendance.late_hours),
                'overtime_hours': float(attendance.overtime_hours),
                'day_status': attendance.day_status,
                'message': 'Attendance updated successfully'
            })
            
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'Attendance record not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
