from itertools import zip_longest
from django.shortcuts import render,redirect
import json
from Owner.models import UsesDB
from Spare_Purchase.models import StockDB
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from Supervisor.models import CustomerDB, JobCardDB, JobCardPartsDB, VehicleDB
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings
from datetime import datetime
from datetime import datetime

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
                part_obj.Quantity=part_obj.Quantity-int(i["quantity"])
                part_obj.save()   
                JobCardPartsDB.objects.create(JobCart=JobCardobj,part_obj=part_obj,quantity=i["quantity"])
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            print(str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)





@csrf_exempt
def record_payment(request):
    user_id=request.session['user_id'] 
    user_name=request.session['user_name'] 
    position=request.session['user_position'] 
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_card = JobCardDB.objects.get(id=data['job_card_id'])
            notes=job_card.PaymentNotes
            paidaomut=job_card.paydPayent
            totalamount=job_card.TotalPayent
            Paymentdonebynote=job_card.Paymentdonebynote
            newPaymentdonebynote=""
            # Convert amount to float
            print(data)
            payment_amount = float(data['amount'])

           
            newpaidaomut=float(paidaomut)+float(payment_amount)
            
            newtotalamount=float(totalamount)-float(newpaidaomut)
            
            if notes==None:
                newnote=data['notes'] + "$$$"
            else:
                if data['notes']!="":
                    newnote=notes+data['notes'] + ", $$$ ,"

            if Paymentdonebynote==None:
                newPaymentdonebynote=f"{Paymentdonebynote} user_id :- {user_id} , user_name :- {user_name}({position}, paid amount :- {payment_amount} , Payment Method :- {data['method']})  $$$"
            else:newPaymentdonebynote=f"{Paymentdonebynote} user_id :- {user_id} , user_name :- {user_name}({position}, paid amount :- {payment_amount} , Payment Method :- {data['method']})  $$$"
            

            job_card.PaymentNotes=newnote
            # job_card.TotalPayent=newtotalamount
            job_card.paydPayent=newpaidaomut
            job_card.PaymentMethod=data['method']
            job_card.Paymentdonebynote=newPaymentdonebynote


            paidaomut=float(format(job_card.paydPayent, '.2f'))
            totalamount=float(format(job_card.TotalPayent, '.2f'))
            print(f"{paidaomut} {totalamount}")
            if paidaomut==totalamount:
                job_card.paymentStatus="Completed"


            job_card.save()
        
            
            
            
            return JsonResponse({
                'success': True,
                'message': 'Payment recorded successfully',
                'new_balance': float(3402) - float(30)
            })
            
        except JobCardDB.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Job card not found'}, status=404)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid payment amount'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta

def generate_invoice(request):
    output_filename="invoice.pdf"
    
    data = json.loads(request.body)
    jobObj=JobCardDB.objects.get(id=int(data["job_card_id"]))
    address=jobObj.customer.address
    filename = f"Invoice_{'invoice_number'}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'invoices', filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                           rightMargin=36, leftMargin=36,
                           topMargin=36, bottomMargin=36)
    
    # Content container
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='InvoiceTitle', 
                             fontSize=24, 
                             leading=28,
                             alignment=1,  # center aligned
                             textColor=colors.HexColor("#2c3e50"),
                             spaceAfter=24,
                             fontName="Helvetica-Bold"))
    
    styles.add(ParagraphStyle(name='Header', 
                             fontSize=10, 
                             leading=12,
                             textColor=colors.HexColor("#34495e")))
    
    styles.add(ParagraphStyle(name='Footer', 
                             fontSize=8, 
                             leading=10,
                             textColor=colors.HexColor("#7f8c8d"),
                             alignment=1))
    
    # Add logo (replace with your actual logo path)
    # logo_path = "logo.png"  # Replace with your logo file or remove this section
    # if os.path.exists(logo_path):
    #     logo = Image(logo_path, width=2*inch, height=0.5*inch)
    #     elements.append(logo)
    #     elements.append(Spacer(1, 0.25*inch))
    
    # Invoice title with accent color
    elements.append(Paragraph(f"{data['invoiceNam']}", styles['InvoiceTitle']))
    
    # Decorative line
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Table([[""]], colWidths=[7*inch], style=[
        ('LINEABOVE', (0,0), (0,0), 1, colors.HexColor("#3498db"))
    ]))
    elements.append(Spacer(1, 0.25*inch))
    
    # Company and client information with improved layout
    company_info = [
        [Paragraph("<b>From.</b>", styles['Header']), 
         Paragraph("<b>BILL TO</b>", styles['Header'])],
       
    ]
    lines1 = ["Piller no:113, Metro station, near Companypady,",
             "Thaikkattukara, Aluva, Kerala 683106"]
    lines=[]
    current_line = ""
    for part in address:
        # If adding this part would exceed 45 chars, start a new line
        if current_line and len(current_line) + len(part) + 2 > 48:  # +2 for comma and space
            lines.append(current_line)
            current_line = part
        else:
            if current_line:
                current_line +=   part
            else:
                current_line = part

    if current_line:
        lines.append(current_line)
    result = [[x or "", y] for x, y in zip_longest(lines1, lines, fillvalue="")]
    
    print(result)
    for i in result:
        company_info.append(i)
    company_info.append(["Email:- ", "Email:- "+str(jobObj.customer.email)])
    company_info.append(["Phone:- +91 96562 56743", f"Phone:- {jobObj.customer.phone}"])
    
    
    company_table = Table(company_info, colWidths=[doc.width/2]*2)
    company_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # More space after headers
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.4*inch))
    print(data)
    # Invoice details with better visual hierarchy
    invoice_details = [
        [Paragraph("<font color='#3498db'><b>INVOICE #</b></font>", styles['Header']), 
         Paragraph(f"{data['invoice_number']}", styles['Header'])],
        [Paragraph("<font color='#3498db'><b>DATE</b></font>", styles['Header']), 
         datetime.now().strftime("%B %d, %Y")],
        # [Paragraph("<font color='#3498db'><b>DUE DATE</b></font>", styles['Header']), 
        #  (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")],
        # [Paragraph("<font color='#3498db'><b>PAYMENT TERMS</b></font>", styles['Header']), 
        #  "Net 30"],
        [Paragraph("<font color='#3498db'><b>PAYMENT METHOD</b></font>", styles['Header']), 
         f"{jobObj.PaymentMethod}"]
    ]
    
    invoice_table = Table(invoice_details, colWidths=[1.5*inch, 3*inch])
    invoice_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Items table with premium styling
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], 
                               fontName='Helvetica-Bold',
                               textColor=colors.HexColor("#2c3e50"))
    
    items = [
        [
            Paragraph("<font color='#3498db'>ITEM</font>", bold_style),
            Paragraph("<font color='#3498db'>DESCRIPTION</font>", bold_style),
            Paragraph("<font color='#3498db'>QTY</font>", bold_style),
            Paragraph("<font color='#3498db'>UNIT PRICE</font>", bold_style),
            Paragraph("<font color='#3498db'>AMOUNT</font>", bold_style)
        ],
        
    ]
    part=JobCardPartsDB.objects.filter(JobCart=jobObj)
    de={}
    n1=1
    for i in part:
        if i.part_obj.id in de.keys():
            de[i.part_obj.id][2]=int(de[i.part_obj.id][2])+int(i.quantity)
        else:
            de[i.part_obj.id]=[str(n1),str(i.part_obj.ItemName),str(i.quantity),"$"+str(i.part_obj.Price),"$"+str(i.quantity*i.part_obj.Price)]
            n1
    for i in de.values():
        items.append(i)
    lbcharge=jobObj.labor_hours*jobObj.hourly_rate
    items.append([f"{n1}", "Labor Charges", "", "", f"${lbcharge}"])
    items.append(["", "", "", Paragraph("<b>Subtotal:</b>", bold_style), f"${jobObj.TotalPayent}"],)
    items.append(["", "", "", Paragraph("<font color='#3498db'><b>TOTAL DUE:</b></font>", bold_style), 
         Paragraph(f"<font color='#3498db'><b>${jobObj.TotalPayent}</b></font>", bold_style)])
 
        # # ["", "", "", Paragraph("<b>Tax (10%):</b>", bold_style), "$640.00"],

    items_table = Table(items, colWidths=[1.2*inch, 2.5*inch, 0.6*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#3498db")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor("#bdc3c7")),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#3498db")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.5*inch))
    
    
    
   
   
    
    # Build the document
    doc.build(elements)
    print(f"Premium invoice generated: {filepath}")
    
    return JsonResponse({
        'success': True,
        'invoice_url': os.path.join(settings.MEDIA_URL, 'invoices', filename)
    })
