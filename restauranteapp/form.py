from django import forms
from restauranteapp.models import Reserva
from .models import Resena

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva  # Usa el modelo Reserva
        fields = ['fecha_reserva', 'hora_reserva', 'numero_personas']  # Campos a incluir
        widgets = {
            'fecha_reserva': forms.DateInput(attrs={'type': 'date'}),  # Input de tipo fecha
            'hora_reserva': forms.TimeInput(attrs={'type': 'time'}),  # Input de tipo hora
        }

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'rows': 4}),
        }
