from django import forms
from .models import Account, userProfile

class RegisterationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password',
        'class':'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'confirm password',
        'class':'form-control'
    }))

    class Meta:
        model = Account
        fields = ['first_name','last_name','email','phone_number','password',]


    def clean(self):
        cleaned_data = super(RegisterationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Password does not match!'
            )
        
        return cleaned_data


    def __init__(self,*args,**kwargs):
        super(RegisterationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number',]

    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False,error_messages={'invalid':{'image files only'}},widget=forms.FileInput)
    class Meta:
        model = userProfile
        fields = ['address_line_1','address_line_2','profile_picture','city','state','country',]
    
    def __init__(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'