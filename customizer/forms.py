from django import forms
from .models import Order, ProductOption, DesignAsset

class OrderForm(forms.ModelForm):
    """
    Formulario para validar los datos del pedido antes de guardarlos.
    Las imágenes de diseño vienen en Base64 desde el Canvas.
    """
    front_design_base64 = forms.CharField(widget=forms.HiddenInput(), required=False)
    back_design_base64 = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Order
        fields = [
            'customer_name',
            'phone_number',
            'size',
            'color',
            'fabric_type',
            'ai_instructions',
            'additional_notes',
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition',
                'placeholder': 'Tu nombre y apellido'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition',
                'placeholder': 'Ej: 3001234567'
            }),
            'size': forms.HiddenInput(),
            'color': forms.HiddenInput(),
            'fabric_type': forms.HiddenInput(),
            'ai_instructions': forms.HiddenInput(),
            'additional_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-amber-500 focus:outline-none transition text-sm',
                'rows': 2,
                'placeholder': '¿Algún detalle extra? (ej: estampado centrado en el pecho, etc.)'
            }),
        }
