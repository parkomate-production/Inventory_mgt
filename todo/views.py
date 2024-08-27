from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .models import Material_Inventory,Components_List,Category_List

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from Send__email import send
import random
from datetime import date, timedelta
import datetime
from datetime import timedelta
from datetime import datetime 
from datetime import date
import xlwt

from django.http import HttpResponse

admin_mail_id = "ajayladkat123@gmail.com"
# admin_mail_id = "ajay.ladkat@parkomate.com"


"""
Inventory : red alarm below 90%

For authority to uodate:
    first_name = authorized
    
"""


def home(request):
    return render(request, 'todo/home.html')


class convert_to_class:
    def __init__(self,a,b,c):
        self.item_name = a
        self.qty = b
        self.color = c

class convert_to_class_CL:
    def __init__(self,a):
        self.Category_name = a


def inventory_selection(request):
    cat_list = Category_List.objects.all()

    cat_information = []
    for CL in cat_list:
        cat_information.append(convert_to_class_CL(CL.Categories))


    if request.method == 'GET':

        user_info = User.objects.all().filter(id = request.user.id)[0]

        if len(user_info.first_name) > 1 or user_info.is_superuser:
            return render(request, 'todo/inventory_selection.html',{"authorized":"authorized","cat_information":cat_information})
        else:
            return render(request, 'todo/inventory_selection.html',{"cat_information":cat_information})

    
    else:
        try:            
            return redirect('check_inventory',request.POST['check_inventory'])
        except:
            pass

        try:
            return redirect('update_inventory',request.POST['update_inventory'])
        except:
            pass

        try:
            return redirect('Update_material_list',request.POST['Update_material_list'])
        except:
            pass

        try:
            return redirect('Detailed_Report',request.POST['Detailed_Report'])
        except:
            pass

        return redirect('home')


def check_inventory(request,category_name):
    component_info = Components_List.objects.all().filter(inventory_category = category_name)
    item_name_list = []
    for ii in component_info:
        item_name_list.append(ii.item_name)
    Inventory_info = Material_Inventory.objects.all().filter(inventory_category = category_name)
    colour_change = 1

    item_name, item_Qty = [],[]
    qty_in_inventory,ideal_qty_inventory = [],[]
    item_name_unique_with_std_inventory,colour_of_row = [],[]

    for ii in Inventory_info:
        item_name.append(ii.item_name)
        item_Qty.append(ii.quantity)

    item_name_unique = list(set(item_name))
        
    for inu in item_name_unique:
        qty = 0
        for i in range (len(item_name)):
            if item_name[i] == inu:
                qty = qty + item_Qty[i]
        qty_in_inventory.append(qty)           


    for inu in item_name_unique:
        for ii in component_info:
            if ii.item_name == inu:
                ideal_qty_inventory.append(ii.standard_inventory_to_maintain)

    for i in range(len(item_name_unique)):
        if colour_change == 1:
            item_name_unique_with_std_inventory.append(item_name_unique[i] + " { to be maintain : " + str(ideal_qty_inventory[i]) + " }")
            if ideal_qty_inventory[i] * 0.90 > qty_in_inventory[i]:
                colour_of_row.append("#FFC1CE")
            elif ideal_qty_inventory[i] > qty_in_inventory[i]:
                colour_of_row.append("#F0EBAA")
            else:
                colour_of_row.append("#C5FFC6")
        else:
                item_name_unique_with_std_inventory.append(item_name_unique[i])
                colour_of_row.append(" ")

    data_information = []
    for i in range(len(qty_in_inventory)):
        data_information.append(convert_to_class(item_name_unique_with_std_inventory[i],qty_in_inventory[i],colour_of_row[i]))

    if request.method == 'GET':
        return render(request, 'todo/check_inventory.html',{"item_name_list":item_name_list,"data_information":data_information,"title":category_name + " inventory"})

    else:
        c = datetime.now()
        current_time = c.strftime('%H:%M:%S')
        current_date = str(date.today())

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="'   + category_name + '_Inventory_' +  current_date   + '.xls"'

        wb = xlwt.Workbook(encoding='utf-8')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        ws = wb.add_sheet("Inventory")
        ws.write(0, 0, category_name + " Inventory", font_style)
        ws.write(0, 1, "Date  " + current_date, font_style)
        ws.write(0, 2, "Time  " + current_time, font_style)

        ws.write(2, 0, "Sr. No.", font_style)
        ws.write(2, 1, "Item Name", font_style)
        ws.write(2, 2, "Quantity", font_style)


        sr_num, row_num = 0,3
        for di in data_information:
            sr_num+=1
            ws.write(row_num, 0, str(sr_num) + ".", font_style)
            ws.write(row_num, 1, di.item_name, font_style)
            ws.write(row_num, 2, di.qty, font_style)
            row_num+=1

        wb.save(response)

        return response


def update_inventory(request,category_name):
    component_info = Components_List.objects.all().filter(inventory_category = category_name)
    item_name_list = []
    for ii in component_info:
        item_name_list.append(ii.item_name)
    if request.method == 'GET':
        return render(request, 'todo/update_inventory.html',{"item_name_list":item_name_list,"title":"Update " + category_name + " inventory"})
    else:
        item_name = request.POST['item_name']
        qty = int(request.POST['qty'])
        in_out = request.POST['in_out']
        comment = request.POST['comment']
        date1 = request.POST['date']
        date_details = date1.split("-")
        updated_date = date(int(date_details[0]), int(date_details[1]), int(date_details[2]))

        subject = category_name + " inventory updated"
        message = category_name + " inventory updated:\n\nitem name: " + item_name + "\nQuantity: " + str(qty) + "\nEntry type: " + in_out + "\nComment: " + comment + "\nDate: " + date1
        send_to = admin_mail_id
        send(subject,message, send_to)

        msg = in_out + ' -> "' +  item_name + ', Qty=' +   str(qty)  + '" is updated in inventory.'

        user = User.objects.get(id = request.user.id)

        inventory_info = Material_Inventory()
        inventory_info.user  = user
        inventory_info.item_name = item_name
        if in_out == "outward":
            qty = qty * -1
        inventory_info.quantity = qty
        inventory_info.in_out = in_out
        inventory_info.comment = comment
        inventory_info.date = updated_date
        inventory_info.inventory_category = category_name
        inventory_info.save()

        return render(request, 'todo/update_inventory.html',{"item_name_list":item_name_list,"msg":msg,"title":"Update " + category_name + " inventory"})


def Update_material_list(request,category_name):
    if request.method == 'GET':
        return render(request, 'todo/update_material_list.html',{"title":"Add new " + category_name + " to the list"})
    else:
        component_name = request.POST['component_name']
        msg = '"' +  component_name + " {minimum quantity to maintain:" + request.POST['number_to_maintain'] + ') " is added to the list successfully.' 
        component_for_inventory = Components_List()
        component_for_inventory.item_name = component_name
        component_for_inventory.standard_inventory_to_maintain = int(request.POST['number_to_maintain'])
        component_for_inventory.inventory_category = category_name
        component_for_inventory.save()
        return render(request, 'todo/update_material_list.html',{"msg":msg,"title":"Add new " + category_name + " to the list"})

def Detailed_Report(request,category_name):
    if request.method == 'GET':
        return render(request, 'todo/detailed_report.html',{"title":"Detailed report of " + category_name})
    else:
        c = datetime.now()
        current_time = c.strftime('%H:%M:%S')
        current_date = str(date.today())

        date1 = request.POST['date1']
        date_details = date1.split("-")
        start_date = date(int(date_details[0]), int(date_details[1]), int(date_details[2]))

        date2 = request.POST['date2']
        date_details = date2.split("-")
        end_date = date(int(date_details[0]), int(date_details[1]), int(date_details[2]))

        in_out = request.POST['in_out']


        if in_out != "all":
            Inventory_info = Material_Inventory.objects.all().filter(inventory_category = category_name).filter(date__gte=start_date,date__lte=end_date).filter(in_out=in_out).order_by('date')
        else:
            Inventory_info = Material_Inventory.objects.all().filter(inventory_category = category_name).filter(date__gte=start_date,date__lte=end_date).order_by('date')


        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="' + category_name +  '_Inventory_Detailed_report_' +  current_date   + '.xls"'

        wb = xlwt.Workbook(encoding='utf-8')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True



        ws = wb.add_sheet("Inventory")
        ws.write(0, 0, "Detailed " + category_name + " Inventory", font_style)
        ws.write(0, 2, "Date: " + current_date, font_style)
        ws.write(0, 3, "Time: " + current_time, font_style)

        ws.write(1, 0, "From date: " + str(start_date), font_style)

        ws.write(1, 3, "Till date: " + str(end_date), font_style)

        ws.write(3, 0, "Date", font_style)
        ws.write(3, 1, "Item Name", font_style)
        ws.write(3, 2, "Quantity", font_style)
        ws.write(3, 3, "Status", font_style)
        ws.write(3, 4, "Comment", font_style)
        ws.write(3, 5, "Responsible person", font_style)

        row_num = 4
        
        for ii in Inventory_info:
            ws.write(row_num, 0, str(ii.date), font_style)
            ws.write(row_num, 1, ii.item_name, font_style)
            ws.write(row_num, 2, ii.quantity, font_style)
            ws.write(row_num, 3, ii.in_out, font_style)
            ws.write(row_num, 4, ii.comment, font_style)

            user_Name = User.objects.all().filter(id=ii.user_id)
            ws.write(row_num, 5, user_Name[0].username, font_style)
            row_num+=1

        wb.save(response)

        return response



def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html')
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username = request.POST['username'], password=request.POST['password1'],  last_name=request.POST['password1'] )
                user.save()
                
                subject = "Parkomate Solution (Technical Department) : User authentication - "
                message = "Parkomate Solution (Technical Department) \n \nUser Authentication \n\n User name : "  + request.POST['username'] + "\n password : " + request.POST['password1']
                send_to = admin_mail_id
                send(subject,message, send_to)

                return render(request, 'todo/home.html',{'msg':'Registration Done. '})
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'That username has already been taken. Please choose a new username'})
        else:
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('home')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


