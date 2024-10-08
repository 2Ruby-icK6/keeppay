from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
import uuid

#Create your models here.

class Recents(models.Model) :
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, null=True
    )
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

# -------------------------------------------------- New ------------------------------

class Student(Recents):
    YEAR_LEVEL_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
    ]
    
    Student_number = models.CharField(max_length=15, null=False, unique=True)
    First_name = models.CharField(max_length=75, null=False)
    Last_name = models.CharField(max_length=75, null=False)
    Year_level = models.CharField(max_length=10, choices=YEAR_LEVEL_CHOICES, null=True)  # Updated here
    Corporate_email = models.EmailField(max_length=150, unique=True, null=False)
    Password = models.CharField(max_length=75, null=False)

    def __str__(self):
        return f"{self.First_name} {self.Last_name}"


class Officer(Recents):
    Student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="officer")
    Position = models.CharField(max_length=75, null=False)

    def __str__(self):
        return f"{self.Student.Last_name} - {self.Position}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        admin_group, _ = Group.objects.get_or_create(name='Admin')
        guest_group, _ = Group.objects.get_or_create(name='Guest')

        user = User.objects.get(email=self.Student.Corporate_email)
        if user.groups.filter(name='Guest').exists():
            user.groups.remove(guest_group)

        if not user.groups.filter(name='Admin').exists():
            user.groups.add(admin_group)

        user.is_staff = True
        user.save()


class FeeType(Recents):
    Fee_name = models.CharField(max_length=75, null=False)
    Fee_amount = models.BigIntegerField(null=False)

    def __str__(self):
        return f"{self.Fee_name} - {self.Fee_amount}"


class Transaction(Recents):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="transaction")
    Officer = models.ForeignKey(Officer, on_delete=models.CASCADE, related_name="transaction", null=True)
    Transaction_date = models.DateTimeField(default=timezone.now)
    Payment_type = models.ForeignKey(FeeType, on_delete=models.CASCADE)
    Amount = models.BigIntegerField(null=False)

    STATUS_CHOICES = [
        ('Fully Paid', 'Fully Paid'),
        ('Partially Paid', 'Partially Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    
    Status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Unpaid')

    def save(self, *args, **kwargs):
        if self.Amount >= self.Payment_type.Fee_amount:
            self.Status = 'Fully Paid'
        elif self.Amount > 0:
            self.Status = 'Partially Paid'
        else:
            self.Status = 'Unpaid'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.Status}"
