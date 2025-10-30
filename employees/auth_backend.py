from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Employee

class EmployeeBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            employee = Employee.objects.get(employee_no=username)
            user = employee.user
            if user.check_password(password):
                return user
        except Employee.DoesNotExist:
            return None
        return None