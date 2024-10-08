# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from apps.home.models import Student,Transaction, FeeType, Officer
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input text-primary"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input text-primary"
            }
        ))

# ============================= Import Data =================================

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
        })
    )

# ============================= Admin Profile ============================= 

class OfficerStudentForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ['Position']  # Position field is from Officer model
    
        widgets = {
            'Position': forms.TextInput(attrs={"class": "form-control"})  # Set widget for Position
        }

    student_first_name = forms.CharField(
        max_length=75, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    student_last_name = forms.CharField(
        max_length=75, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    corporate_email = forms.EmailField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), 
        required=False,  # Password field is optional for updates
    )

    def __init__(self, *args, **kwargs):
        self.officer = kwargs.pop('officer', None)
        super().__init__(*args, **kwargs)

        if self.officer:
            self.fields['student_first_name'].initial = self.officer.Student.First_name
            self.fields['student_last_name'].initial = self.officer.Student.Last_name
            self.fields['corporate_email'].initial = self.officer.Student.Corporate_email
            self.fields['password'].initial = self.officer.Student.Password

    def save(self, commit=True):
        officer = super().save(commit=commit)

        student = self.officer.Student
        student.First_name = self.cleaned_data['student_first_name']
        student.Last_name = self.cleaned_data['student_last_name']
        student.Corporate_email = self.cleaned_data['corporate_email']
        student.Password = self.cleaned_data['password']

        if self.cleaned_data['password']:
            user = User.objects.get(email=student.Corporate_email)
            user.set_password(self.cleaned_data['password'])
            user.save()

        if commit:
            student.save()

        return officer

class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ['Student', 'Position']
    
        widgets = {
                'Student': forms.Select(attrs={"class": "form-control"}),
                'Position': forms.TextInput(attrs={"class": "form-control"})
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Student'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['Student'].queryset = Student.objects.exclude(officer__isnull=False)
        
# ============================= Create Transaction ==========================

class Payee(forms.ModelForm):
    Student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    
    Officer = forms.ModelChoiceField(
        queryset=Officer.objects.all(),
        widget=forms.Select(attrs={"class": "form-control", "readonly": "readonly", "disabled":"disabled" })  # Make Officer field read-only
    )

    Transaction_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local', 'readonly': 'readonly'}
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        initial=timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
    )

    Payment_type = forms.ModelChoiceField(
        queryset=FeeType.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    Amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )

    Status = forms.ChoiceField(
        choices=Transaction.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False  # We will automate this
    )

    class Meta:
        model = Transaction
        fields = ('Student', 'Officer', 'Transaction_date', 'Payment_type', 'Amount', 'Status')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user is not None:
            officer = Officer.objects.filter(Student__Corporate_email=user.email).first()
            if officer:
                self.fields['Officer'].initial = officer  # Set the officer
                self.fields['Officer'].widget.attrs['readonly'] = True  # Set as read-only, not disabled
                self.fields['Officer'].queryset = Officer.objects.filter(pk=officer.pk)

        # Set max amount based on FeeType
        if 'Payment_type' in self.data:
            try:
                fee_type_id = int(self.data.get('Payment_type'))
                fee_type = FeeType.objects.get(pk=fee_type_id)
                self.fields['Amount'].widget.attrs['max'] = fee_type.Fee_amount  # Set max value
            except (ValueError, FeeType.DoesNotExist):
                pass  # Handle invalid fee type

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('Amount')
        payment_type = cleaned_data.get('Payment_type')
        
        # Get the fee amount from the selected FeeType
        if payment_type:
            fee_amount = payment_type.Fee_amount
            
            # Automate the status based on the amount entered
            if amount is None or amount == 0:
                cleaned_data['Status'] = 'Unpaid'
            elif amount == fee_amount:
                cleaned_data['Status'] = 'Fully Paid'
            elif 0 < amount < fee_amount:
                cleaned_data['Status'] = 'Partially Paid'
            
            # Ensure the amount does not exceed the Fee_amount
            if amount > fee_amount:
                self.add_error('Amount', f"The amount cannot exceed the fee amount of {fee_amount}.")
        
        return cleaned_data

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.Status = self.cleaned_data['Status']
        if commit:
            transaction.save()
        return transaction

    
# ==================================== Create Fee ===========================================

class FeeTypeForm(forms.ModelForm):
    class Meta:
        model = FeeType
        fields = ['Fee_name', 'Fee_amount']
        widgets = {
            'Fee_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter fee name'
            }),
            'Fee_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter fee amount',
                'min': '0'  # Disable negative numbers by setting the minimum to 0
            }),
        }

    def clean_Fee_amount(self):
        fee_amount = self.cleaned_data.get('Fee_amount')
        if fee_amount < 0:
            raise forms.ValidationError("Fee amount cannot be negative.")
        return fee_amount

# =============================== End ========================================================

# ================================== Student =================================================

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['Year_level']  # Add other fields if necessary
    
        widgets = {
            'Year_level': forms.Select(attrs={"class": "form-control"})  # Use Select widget for Year Level
        }

    first_name = forms.CharField(
        max_length=75, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        max_length=75, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    corporate_email = forms.EmailField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), 
        required=False,  # Password field is optional for updates
    )

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

        if self.student:
            self.fields['first_name'].initial = self.student.First_name
            self.fields['last_name'].initial = self.student.Last_name
            self.fields['corporate_email'].initial = self.student.Corporate_email
            self.fields['password'].initial = self.student.Password

    def save(self, commit=True):
        student = super().save(commit=commit)

        student.First_name = self.cleaned_data['first_name']
        student.Last_name = self.cleaned_data['last_name']
        student.Corporate_email = self.cleaned_data['corporate_email']
        student.Password = self.cleaned_data['password']

        if self.cleaned_data['password']:
            user = User.objects.get(email=student.Corporate_email)
            user.set_password(self.cleaned_data['password'])
            user.save()

        if commit:
            student.save()

        return student