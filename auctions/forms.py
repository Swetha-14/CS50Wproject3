from django import forms  
from .models import Auctionlisting

class CreateForm(forms.ModelForm):  
    class Meta:  
        model = Auctionlisting  
        fields = "__all__"
        exclude = ['created_date','active']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Title'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Describe your product..'}),
            'starting_bid': forms.NumberInput(attrs={'class':'form-control'}),
            'item_slug': forms.URLInput(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-control'})
        }