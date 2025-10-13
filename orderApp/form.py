from django import forms

from orderApp.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields =  ['first_name','last_name','email','phone_number','address_line_1','address_line_2','country','state','city','order_note',]

    
class CouponApplyForm(forms.Form):
    code = forms.CharField(label='Coupon Code', max_length=50)
