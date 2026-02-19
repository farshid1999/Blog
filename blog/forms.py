from django import forms
from django.forms import ModelForm
from .models import *
class TicketForm(forms.ModelForm):
    class Meta:
        model=Ticket
        fields=["message","name","email","phone","subject"]
        widgets={
            "message":forms.Textarea(attrs={
              "required":True
            }),
            "name":forms.TextInput(attrs={
                "required":True
            }),
            "email":forms.EmailInput(attrs={

            }),
            "phone":forms.TextInput(attrs={

            }),
            "subject":forms.TextInput(attrs={
                "required": True
            }),
        }
        def clean_phone(self):
            phone=self.cleaned_data['phone']
            if not phone.isdigit():
                raise forms.ValidationError("شماره تلفن فقط باید شامل اعداد باشد")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields=['name','body']

class PostModelForm(forms.ModelForm):
    class Meta:
        model=Post
        fields=['title','description','reading_time']


class SearchPost(forms.Form):
    query=forms.CharField()


class RegisterPost(forms.Form):
    username=forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            "required":True
        })
    )
    email=forms.CharField(
        max_length=50,
        widget=forms.EmailInput(attrs={
            "required":True
        })
    )
    password=forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            "required":True
        })
    )
    password_again=forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            "required":True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_again = cleaned_data.get("password_again")

        if password and password_again and password != password_again:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

class LoginForm(forms.Form):
    username=forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            "required":True
        })
    )
    password=forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            "required":True
        })
    )

class UserRegisterForm(forms.Form):
    password=forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            "required":True
        })
    )
    password2=forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={
            "required":True
        })
    )
    def clean_password(self):
        cd=self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("پسورد ها مطابقت ندارد")
        return cd["password"]

    class Meta:
        model=User
        fields=['first_name','last_name','username','email']

class UserEditForm(forms.ModelForm):
    class Meta:
        model=Account
        fields = ['first_name','last_name','email','birthdate']