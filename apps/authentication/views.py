from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from .decorators import unauthorized_user, allowed_user, admin_only
from django.contrib.auth.models import Group
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import F, Q, Count, Sum, IntegerField

# -------------------------------------------------- New ------------------------------
from .forms import LoginForm
from .forms import Payee, FeeTypeForm, OfficerStudentForm, OfficerForm, StudentForm
from apps.home.models import Student, Officer, FeeType, Transaction
from django.contrib import messages
from django.contrib.auth.models import User
import csv
from .forms import CSVUploadForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models

# -------------------------------------------------- Old ------------------------------

@unauthorized_user
def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid(): 
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    return redirect("/index")
                else:
                    login(request, user)
                    return redirect("/index-guest")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

# -------------------------------------------------- New ------------------------------

# ==================================== Import Data ====================================

@allowed_user(roles=['Admin'])
def import_students(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('import_students')

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            guest_group, created = Group.objects.get_or_create(name='Guest')

        errors = []

        for row in reader:
            try:
                # Create the User
                user = User.objects.create(
                    username=row['Corporate_email'],
                    email=row['Corporate_email'],
                    password=make_password(row['Password']),
                    first_name=row['First_name'],
                    last_name=row['Last_name'],
                )
                user.groups.add(guest_group)
                user.save()

                # Create the Student
                student = Student.objects.create(
                    Student_number=row['Student_number'],
                    First_name=row['First_name'],
                    Last_name=row['Last_name'],
                    Year_level=row.get('Year_level', None),
                    Corporate_email=row['Corporate_email'],
                    Password=row['Password'],
                )
                student.save()

            except Exception as e:
                # Log the error and continue
                errors.append(f"Error with student {row['Last_name'], row['First_name']}: {e}")

        # Report errors back to the user
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            messages.success(request, "Students imported successfully!")
        
        return redirect('import_students')

    else:
        form = CSVUploadForm()

    return render(request, 'cruds/admin/import_student.html', {'form': form})

# ----------------------------- Read / ShowList ---------------------------------

# ================================== Admin =======================================

@method_decorator(allowed_user(roles=['Admin']), name='dispatch')
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'home/index.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        queryset = Student.objects.all().order_by('Student_number')
        
        query = self.request.GET.get('search', '')
        year_level_filter = self.request.GET.get('year_level', '')

        if query:
            queryset = queryset.filter(
                Q(First_name__icontains=query) | 
                Q(Last_name__icontains=query) | 
                Q(Student_number__icontains=query)
            )

        if year_level_filter:
            queryset = queryset.filter(Year_level=year_level_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_email = self.request.user.email
            officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
            student = officer.Student
            
            transactions = Transaction.objects.filter(Student=student).values('Student').annotate(total_amount=Sum('Amount'))
            total_fees = FeeType.objects.aggregate(total_fee=Sum('Fee_amount'))['total_fee'] or 0
            total_amount_paid = transactions[0]['total_amount'] if transactions else 0
            remaining_balance = total_fees - total_amount_paid

            context['officer'] = officer
            context['student'] = student
            context['transactions'] = Transaction.objects.filter(Student=student)
            context['total_fees'] = total_fees
            context['total_amount_paid'] = total_amount_paid
            context['remaining_balance'] = remaining_balance

        except Officer.DoesNotExist:
            context['officer'] = None

        transactions = Transaction.objects.values('Student').annotate(total_amount=Sum('Amount'))
        total_fees = FeeType.objects.aggregate(total_fee=Sum('Fee_amount'))['total_fee'] or 0
        total_amount_dict = {transaction['Student']: transaction['total_amount'] for transaction in transactions}

        for student in context['students']:
            total_amount = total_amount_dict.get(student.id, 0)
            student.total_amount = total_amount
            student.remaining_balance = total_fees - total_amount

        context['total_fees'] = total_fees

        # Get unique year levels for filtering
        context['year_levels'] = Student.objects.values_list('Year_level', flat=True).distinct()

        return context


@method_decorator(allowed_user(roles=['Admin']), name='dispatch')
class OfficerListView(ListView):
    model = Officer
    template_name = 'home/adminprofile.html'
    context_object_name = 'officers'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get the officer related to the currently logged-in user
            officer = get_object_or_404(Officer, Student__Corporate_email=self.request.user.email)
            form = OfficerStudentForm(officer=officer, instance=officer)  # Pass the officer instance here
            context['officer_form'] = form
        
        try:
            user_email = self.request.user.email
            officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
            student = officer.Student

            context['officer'] = officer
            context['student'] = student

        except Officer.DoesNotExist:
            context['officer'] = None
            
        return context

    def post(self, request, *args, **kwargs):
        officer = get_object_or_404(Officer, Student__Corporate_email=request.user.email)
        form = OfficerStudentForm(request.POST, instance=officer, officer=officer)

        if form.is_valid():
            form.save()
            user = request.user
            student = officer.Student
            password_changed = False

            if form.cleaned_data['student_first_name'] != student.First_name:
                user.first_name = form.cleaned_data['student_first_name']
                student.First_name = form.cleaned_data['student_first_name']
            
            if form.cleaned_data['student_last_name'] != student.Last_name:
                user.last_name = form.cleaned_data['student_last_name']
                student.Last_name = form.cleaned_data['student_last_name']

            if form.cleaned_data['corporate_email'] != student.Corporate_email:
                user.email = form.cleaned_data['corporate_email']
                student.Corporate_email = form.cleaned_data['corporate_email']

            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
                student.Password = form.cleaned_data['password']
                password_changed = True

            user.save()
            student.save()

            if password_changed:
                update_session_auth_hash(request, user)

            return HttpResponseRedirect(reverse('officer_profile'))

        return self.get(request, *args, **kwargs)
    
@allowed_user(roles=['Admin'])
def add_officer_view(request):
    msg = None
    if request.method == 'POST':
        form = OfficerForm(request.POST)
        if form.is_valid():
            officer = form.save()

            # Adding the user to the 'Admin' group and removing from 'Guest' group
            user = User.objects.get(email=officer.Student.Corporate_email)
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            guest_group, _ = Group.objects.get_or_create(name='Guest')

            if user.groups.filter(name='Guest').exists():
                user.groups.remove(guest_group)

            if not user.groups.filter(name='Admin').exists():
                user.groups.add(admin_group)

            user.is_staff = True
            user.save()

            msg = 'Officer added successfully!'
            return redirect('officer_profile')  # Assuming you have an officer list page
    else:
        form = OfficerForm()

    return render(request, 'cruds/admin/add_officer.html', {'form': form, 'msg': msg})

@allowed_user(roles=['Admin'])
def remove_officer(request, officer_id):
    officer = get_object_or_404(Officer, id=officer_id)
    user = User.objects.get(email=officer.Student.Corporate_email)

    # Check if the officer is currently logged in
    if request.user.email == officer.Student.Corporate_email:
        messages.error(request, "You cannot remove yourself as an officer.")
        return redirect('officer_profile')

    admin_group = Group.objects.get(name='Admin')
    guest_group, _ = Group.objects.get_or_create(name='Guest')

    # Remove the officer from the Admin group and add to Guest group
    if user.groups.filter(name='Admin').exists():
        user.groups.remove(admin_group)
        user.groups.add(guest_group)

    user.is_staff = False
    user.save()
    officer.delete()

    messages.success(request, "Officer has been removed.")
    return redirect('officer_profile')

@method_decorator(allowed_user(roles=['Admin']), name='dispatch')
class TransactionListView(ListView):
    model = Transaction
    template_name = 'home/transaction_dashboard.html'
    context_object_name = 'transactions'
    paginate_by = 3

    def get_queryset(self):
        return Transaction.objects.all().order_by('-Transaction_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            user_email = self.request.user.email
            officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
            student = officer.Student

            context['officer'] = officer
            context['student'] = student

        except Officer.DoesNotExist:
            context['officer'] = None

        # Count all students
        total_students = Student.objects.count()

        # Count paid and pending payers
        student_payment_status = (
            Transaction.objects.values('Student')
            .annotate(total_amount=Sum('Amount'), fee_amount=Sum('Payment_type__Fee_amount'))
            .annotate(
                status=Count(
                    Q(Status='Fully Paid', Amount__gte=F('Payment_type__Fee_amount')),
                    output_field=IntegerField()
                )
            )
        )

        # Initialize counters
        paid_payers = 0
        pending_payers = 0

        for payment in student_payment_status:
            if payment['total_amount'] >= payment['fee_amount']:
                paid_payers += 1
            elif payment['total_amount'] > 0:
                pending_payers += 1

        # Sum all amounts (total collections)
        total_collections = Transaction.objects.aggregate(total=Sum('Amount'))['total'] or 0

        # Add these values to the context
        context['total_students'] = total_students
        context['pending_payers'] = pending_payers
        context['paid_payers'] = paid_payers
        context['total_collections'] = total_collections

        return context

@method_decorator(allowed_user(roles=['Admin']), name='dispatch')
class TransactionRecentListView(ListView):
    model = Transaction
    template_name = 'home/transaction.html'
    context_object_name = 'transactions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Transaction.objects.all().order_by('-Transaction_date')
        
        # Get the search query and payment type from the request
        search_query = self.request.GET.get('search', '')
        payment_type_filter = self.request.GET.get('payment_type', '')

        if search_query:
            # Filter by Student Number or Student Name
            queryset = queryset.filter(
                Q(Student__Student_number__icontains=search_query) | 
                Q(Student__First_name__icontains=search_query) | 
                Q(Student__Last_name__icontains=search_query)
            ).distinct()
        
        if payment_type_filter:
            # Filter by Payment Type
            queryset = queryset.filter(Payment_type__id=payment_type_filter).distinct()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_types'] = FeeType.objects.all()

        try:
            user_email = self.request.user.email
            officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
            student = officer.Student

            context['officer'] = officer
            context['student'] = student

        except Officer.DoesNotExist:
            context['officer'] = None

        return context

@method_decorator(allowed_user(roles=['Admin']), name='dispatch')
class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'cruds/admin/delete_view_T.html'
    context_object_name = 'transaction'
    success_url = reverse_lazy('list_transaction')  # Assuming this is the name of your list view URL
    
    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            user_email = self.request.user.email
            officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
            return queryset.filter(Officer=officer)  # Allow only the officer to delete their transactions
        except Officer.DoesNotExist:
            return queryset.none()

def student_detail_view(request, student_number):
    student = get_object_or_404(Student, Student_number=student_number)
    transactions = Transaction.objects.filter(Student=student)

    officer = None
    try:
        user_email = request.user.email
        officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
        logged_in_student = officer.Student
    except Officer.DoesNotExist:
        officer = None
        logged_in_student = None

    context = {
        'student': student,  
        'transactions': transactions,
        'officer': officer,  
        'logged_in_student': logged_in_student 
    }

    return render(request, 'cruds/admin/student_detail.html', context)

    
# ================================ Guest =========================================

def Student_AccountView(request):
    try:
        # Fetch the logged-in user's email and password
        user_email = request.user.email
        user_password = request.user.password
        
        # Get the student linked to the current user (based on the corporate email)
        student = get_object_or_404(Student, Corporate_email=user_email)
        
        # Get the student's transactions and calculate the total amount paid
        transactions = Transaction.objects.filter(Student=student).values('Student').annotate(total_amount=Sum('Amount'))
        
        # Get the total fee amount from all the fee types
        total_fees = FeeType.objects.aggregate(total_fee=Sum('Fee_amount'))['total_fee'] or 0
        fee = FeeType.objects.all()

        # Calculate the total paid by the student
        total_amount_paid = transactions[0]['total_amount'] if transactions else 0

        # Calculate the remaining balance
        remaining_balance = total_fees - total_amount_paid
        
        # Prepare context data for the template
        context = {
            'student': student,
            'transactions': Transaction.objects.filter(Student=student),
            'total_fees': total_fees,
            'total_amount_paid': total_amount_paid,
            'remaining_balance': remaining_balance,
            'fee' : fee
        }
        
        return render(request, "home/index-guest.html", context)
    
    except Student.DoesNotExist:
        # If student does not exist, redirect to guest page
        return render(request, "home/page-403.html")

class StudentProfileView(ListView):
    model = Student
    template_name = 'home/student_profile.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get the student related to the currently logged-in user
            student = get_object_or_404(Student, Corporate_email=self.request.user.email)
            form = StudentForm(student=student, instance=student)  # Pass the student instance here
            context['student_form'] = form
        
        try:
            user_email = self.request.user.email
            student = get_object_or_404(Student, Corporate_email=user_email)

            context['student'] = student

        except Student.DoesNotExist:
            context['student'] = None
            
        return context

    def post(self, request, *args, **kwargs):
        student = get_object_or_404(Student, Corporate_email=request.user.email)
        form = StudentForm(request.POST, instance=student, student=student)

        if form.is_valid():
            form.save()
            user = request.user
            
            if form.cleaned_data['first_name'] != student.First_name:
                user.first_name = form.cleaned_data['first_name']
                student.First_name = form.cleaned_data['first_name']
            
            if form.cleaned_data['last_name'] != student.Last_name:
                user.last_name = form.cleaned_data['last_name']
                student.Last_name = form.cleaned_data['last_name']

            if form.cleaned_data['corporate_email'] != student.Corporate_email:
                user.email = form.cleaned_data['corporate_email']
                student.Corporate_email = form.cleaned_data['corporate_email']

            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
                student.Password = form.cleaned_data['password']

            user.save()
            student.save()

            if form.cleaned_data['password']:
                update_session_auth_hash(request, user)

            return HttpResponseRedirect(reverse('student_profile'))

        return self.get(request, *args, **kwargs)
    
# ---------------------------- Forms -------------------------------------------------

@allowed_user(roles=['Admin'])
def payee_form(request):
    msg = None
    transaction = Transaction.objects.all()
    fee_types = FeeType.objects.all()
    fee_count = fee_types.count()

    officer = None
    student = None

    try:
        user_email = request.user.email
        officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
        student = officer.Student
    except Officer.DoesNotExist:
        officer = None

    if request.method == 'POST':
        form = Payee(request.POST, user=request.user)

        if form.is_valid():
            payee_instance = form.save(commit=False)
            payee_instance.Officer = officer
            payee_instance = form.save()

            fees = []
            for key in request.POST:
                if key.startswith('fee_type_'):
                    fee_index = key.split('_')[2]
                    fee_type_id = request.POST[key]
                    amount = request.POST.get(f'amount_{fee_index}')
                    status = request.POST.get(f'status_{fee_index}')

                    # Check for duplicate fee_type_id
                    if not Transaction.objects.filter(
                        Student=payee_instance.Student,
                        Payment_type_id=fee_type_id
                    ).exists():
                        # Create a new fee instance only if it doesn't already exist
                        fee_instance = Transaction(
                            Student=payee_instance.Student,
                            Officer=payee_instance.Officer,
                            Payment_type_id=fee_type_id,
                            Amount=amount,
                            Status=status
                        )
                        fees.append(fee_instance)
                    else:
                        # Log a message for duplicate fee
                        messages.warning(
                            request, 
                            f"Fee type {fee_type_id} already exists for this student."
                        )

            if fees:
                Transaction.objects.bulk_create(fees)

            # Add a success message
            messages.success(request, 'Transaction was successfully created.')
            return redirect('/transaction/payee/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}") 
    else:
        form = Payee(user=request.user)


    return render(request, 'cruds/admin/payee.html', {
        'form': form,
        'msg': msg,
        'transaction': transaction,
        'fee_types': fee_types,
        'fee_count': fee_count,
        'officer': officer,  
        'student': student 
    })


@allowed_user(roles=['Admin'])
def fee_type_list(request):
    fee_types = FeeType.objects.all()
    officer = None
    student = None
    try:
        user_email = request.user.email
        officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
        student = officer.Student  
    except Officer.DoesNotExist:
        officer = None

    if request.method == 'POST':
        form = FeeTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fee_type_list')
    else:
        form = FeeTypeForm()

    return render(request, 'cruds/admin/fee_type_list.html', {
        'fee_types': fee_types,
        'form': form,
        'officer': officer,  
        'student': student
    })

@allowed_user(roles=['Admin'])
def edit_fee_type(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    officer = None
    student = None
    try:
        user_email = request.user.email
        officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
        student = officer.Student  
    except Officer.DoesNotExist:
        officer = None

    if request.method == 'POST':
        form = FeeTypeForm(request.POST, instance=fee_type)
        if form.is_valid():
            form.save()
            return redirect('fee_type_list')
    else:
        form = FeeTypeForm(instance=fee_type)

    return render(request, 'cruds/admin/fee_type_list.html', {
        'form': form,
        'fee_types': FeeType.objects.all(),
        'editing': True,
        'officer': officer,  
        'student': student
    })

@allowed_user(roles=['Admin'])
def delete_fee_type(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    officer = None
    student = None
    try:
        user_email = request.user.email
        officer = get_object_or_404(Officer, Student__Corporate_email=user_email)
        student = officer.Student
    except Officer.DoesNotExist:
        officer = None

    if request.method == 'POST':
        fee_type.delete()
        return redirect('fee_type_list')
    
    return render(request, 'cruds/admin/delete_view_F.html', {
        'fee_type': fee_type,
        'officer': officer,
        'student': student   
    })


# Handling HTTP 404 (Page Not Found)
def handler404(request, exception):
    return render(request, 'home/page-404.html', {})

# Handling HTTP 500 (Internal Server Error)
def handler500(request):
    return render(request, 'home/page-500.html', {})