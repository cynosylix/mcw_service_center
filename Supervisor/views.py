from itertools import zip_longest
from django.shortcuts import render,redirect
import json
from Owner.models import UsesDB
from Spare_Purchase.models import StockDB
from django.db.models import Q
from django.http import JsonResponse
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

                paymentbalance=JobCardDBdata[0].TotalPayent-JobCardDBdata[0].paydPayent
                print(paymentbalance)
                data={"name":user_name,"JobCardDBdata":JobCardDBdata[0],"parts":parts,"PartsTotal":PartsTotal,"labercost":labercost,"worker":worker,"paymentbalance":paymentbalance}
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
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    try:
        print("..........................")
        # Get the job card to update
        job_card_id = request.POST.get('job_card_id')
        job_card = JobCardDB.objects.get(id=job_card_id)

        usertxt=f"{user_name} :- ({position}) change data = "
        up=""
        ######################Update basic job card info############################
        delivery_date=request.POST.get('delivery_date')
        if str(delivery_date)!=str(job_card.delivery_date):
            up=up+f"{job_card.delivery_date} : delivery date updated to :- {delivery_date},"
            job_card.delivery_date = delivery_date
            
        assigned_staff_id=request.POST.get('assigned_staff_id')
        assigned_staff_name=request.POST.get('assigned_staff_name')
        if str(assigned_staff_id)!=str(job_card.assigned_staff.id):
            up=up+f"{job_card.assigned_staff.name} :assigned staff updated to :- {assigned_staff_name},"
            stffObj=UsesDB.objects.get(id=assigned_staff_id)
            job_card.assigned_staff = stffObj

        work_description=request.POST.get('work_description')
        if str(work_description)!=str(job_card.work_description):
            up=up+f"{job_card.work_description} : worker description updated to :- {work_description},"
            job_card.work_description = work_description

        status=request.POST.get('status')
        if str(status)!=str(job_card.status):
            up=up+f"{job_card.status} : worker description updated to :- {status},"
            job_card.status = status

        labor_hours=request.POST.get('labor_hours')
        if str(labor_hours)!=str(job_card.labor_hours):
            up=up+f"{job_card.labor_hours} : labor hours updated to :- {labor_hours},"
            job_card.labor_hours = labor_hours

        hourly_rate=request.POST.get('hourly_rate')
        if str(hourly_rate)!=str(job_card.hourly_rate):
            up=up+f"{job_card.hourly_rate} : hourly rate updated to :- {hourly_rate},"
            job_card.hourly_rate=hourly_rate

        discount=request.POST.get('discount')
        if str(discount)!=str(job_card.discount):
            up=up+f"{job_card.discount} : discount updated to :- {discount},"
            job_card.discount=discount
        # need to add total payment
        paymentStatus=request.POST.get('paymentStatus')
        if str(paymentStatus)!=str(job_card.paymentStatus):
            up=up+f"{job_card.paymentStatus} : paymentStatus updated to :- {paymentStatus},"
            job_card.paymentStatus=paymentStatus


        ################################### Update customer info###########################################
        customer=job_card.customer
        
        phone=request.POST.get('customer_phone')
        if str(phone)!=str(customer.phone):
            up=up+f"{customer.phone} : customer_phone no updated to :- {phone},"
            customer.phone=phone

        email = request.POST.get('customer_email')
        if str(email)!=str(customer.email):
            up=up+f"{customer.email} : customer_email updated to :- {email},"
            customer.email=email
        address=request.POST.get('customer_address')
        if str(address)!=str(customer.address):
            up=up+f"{customer.address} : customer_address updated to :- {address},"
            customer.address=address
        
        customernotes=request.POST.get('customer_notes')
        if str(customernotes)!=str(customer.customernotes):
            up=up+f"{customer.customernotes} : customernotes updated to :- {customernotes},"
            customer.customernotes=customernotes
        customer.save()

        #############################Update vehicle info#########################
        vehicle = job_card.vehicle
        registration_no=request.POST.get('registration_no')
        if str(registration_no)!=str(vehicle.registration_no):
            up=up+f"{vehicle.registration_no} : registration_no updated to :- {registration_no},"
            vehicle.registration_no=registration_no
        model=request.POST.get('vehicle_model')
        if str(model)!=str(vehicle.model):
            up=up+f"{vehicle.model} : vehicle_model updated to :- {model},"
            vehicle.model=model
        chassis_no=request.POST.get('chassis_no')
        if str(chassis_no)!=str(vehicle.chassis_no):
            up=up+f"{vehicle.chassis_no} : chassis_no updated to :- {chassis_no},"
            vehicle.chassis_no=chassis_no
        engine_no=request.POST.get('engine_no')
        if str(engine_no)!=str(vehicle.engine_no):
            up=up+f"{vehicle.engine_no} : engine_no updated to :- {engine_no},"
            vehicle.engine_no=engine_no
        petrol_level=request.POST.get('petrol_level')
        if str(petrol_level)!=str(vehicle.petrol_level):
            up=up+f"{vehicle.petrol_level} : petrol_level updated to :- {petrol_level},"
            vehicle.petrol_level=petrol_level
        notes=request.POST.get('vehicle_notes')
        if str(notes)!=str(vehicle.notes):
            up=up+f"{vehicle.notes} : notes updated to :- {notes},"
            vehicle.notes=notes
        vehicle.save()
        ############################# Handle parts - first clear existing parts############################################
        partslist=JobCardPartsDB.objects.filter(JobCart=job_card)
        parts_data = json.loads(request.POST.get('parts', '[]'))
        
        jobcart_in_data=[]
        newd=[]
        print(parts_data)
        for i in parts_data:
            if i["is_existing"]==True:
                jobcart_in_data.append(int(i["part_id"]))
            else:
                newd.append(i)
        
        for i in partslist:
            if i.id not in jobcart_in_data:
                StockDB.objects.filter(id=i.part_obj.id).update(Quantity=int(i.quantity)+int(i.part_obj.Quantity))
                JobCardPartsDB.objects.filter(id=i.id).delete()
        
        for i in newd:
            part_obj=StockDB.objects.get(id=i["part_id"])
            oldq=part_obj.Quantity
            StockDB.objects.filter(id=i["part_id"]).update(Quantity=int(oldq)-int(i["quantity"]))
            JobCardPartsDB.objects.create(JobCart=job_card,part_obj=part_obj,quantity=int(i["quantity"]))

        job_card.save()


        PartsTotal=0
        partslist=JobCardPartsDB.objects.filter(JobCart=job_card)
        for i in partslist:
            PartsTotal+=i.quantity*i.part_obj.Price
        labercost=float(labor_hours)*float(hourly_rate)
        TotalPayment =(PartsTotal  + labercost) 

        discountTotal=TotalPayment-((TotalPayment*float(discount))/100)
        partslist=JobCardDB.objects.filter(id=job_card_id).update(TotalPayent=discountTotal)


        
        return JsonResponse({
            'success': True,
            'message': 'Job card updated successfully',
            'total_payment': job_card.TotalPayent
        })
        
    # except JobCard.DoesNotExist:
    #     return JsonResponse({'success': False, 'message': 'Job card not found'}, status=404)
    except Exception as e:
        print(e)
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
from calendar import monthrange
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




def supervisor_view_staff_attendance(request):
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    position = request.session.get('user_position')
    
    if position == "Supervisor":
        user_data = UsesDB.objects.exclude(position='Owner').exclude(position='Supervisor')
        
        # Get selected month and year (default to current)
        now = datetime.now()
        month = int(request.GET.get('month', now.month))
        year = int(request.GET.get('year', now.year))
        
        # Get number of days in selected month
        _, num_days = monthrange(year, month)
        
        # Get attendance data
        attendance_data = Attendance.objects.filter(
            employee__in=user_data,
            date__year=year,
            date__month=month
        ).select_related('employee')
        
        # Create a better data structure for the template
        staff_attendance = []
        for staff in user_data:
            # Initialize with empty data for each day
            days = {day: '' for day in range(1, num_days+1)}
            
            # Fill in actual attendance data
            for att in attendance_data.filter(employee=staff):
                print(att.day_status)
                days[att.date.day] = att.day_status
            
            staff_attendance.append({
                'staff': staff,
                'days': days,
                'present_count': sum(1 for status in days.values() if status == 'present'),
                'absent_count': sum(1 for status in days.values() if status == 'absent'),
                'leave_count': sum(1 for status in days.values() if status == 'on_leave'),
            })
            # print(staff_attendance)   
        
        context = {
            'user_data': user_data,  # Keep original for other parts of template
            'staff_attendance': staff_attendance,  # New for attendance table
            'user_name': user_name,
            'position': position,
            'selected_month': month,
            'selected_year': year,
            'month_name': datetime(year, month, 1).strftime('%B'),
            'days_range': range(1, num_days+1),
        }
        return render(request, "supervisor_view_staff_attendance.html", context)
    else:
        return render(request, "supervisor_view_staff_attendance.html")
