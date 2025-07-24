from django.shortcuts import render,redirect
from django.contrib import messages
from Owner.models import UsesDB
from Spare_Purchase.models import StockDB
from django.http import JsonResponse
import json

from Supervisor.models import Attendance

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

from django.shortcuts import render
from datetime import datetime
from calendar import monthrange
from .models import UsesDB

def ViewStaffPg(request):
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    position = request.session.get('user_position')
    
    if position == "Owner":
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
        return render(request, "view_staff.html", context)
    else:
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



# Attendance related views
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import date, datetime

def owner_attendance_page(request):
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    position = request.session.get('user_position')
    if position == "Owner":
        return render(request, "owner_attedence_view.html", {"user_name": user_name})
    return redirect("login")


@require_http_methods(["GET"])
def owner_attendance_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
   
    try:
        attendance_data = []
        employees = UsesDB.objects.exclude(position='Owner').exclude(position='Supervisor')
        print("employees:", employees)
        
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
def owner_update_attendance(request, attendance_id):
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
