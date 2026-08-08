from django import forms
from .models import AsignacionGuardia

class AsignacionGuardiaForm(forms.ModelForm):
    class Meta:
        model = AsignacionGuardia
        fields = ['trabajador', 'guardia', 'fecha', 'observaciones']
        widgets = {
            'trabajador': forms.Select(attrs={'class': 'form-control'}),
            'guardia': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        trabajador = cleaned_data.get('trabajador')
        fecha = cleaned_data.get('fecha')
        
        if trabajador and fecha:
            # Requisito 3.2: Validar cruces (un trabajador no puede tener más de una guardia el mismo día)
            # o no pueden solaparse las horas. Como la UI suele asignar 1 guardia por día por trabajador:
            cruce = AsignacionGuardia.objects.filter(trabajador=trabajador, fecha=fecha)
            if self.instance and self.instance.pk:
                cruce = cruce.exclude(pk=self.instance.pk)
            
            if cruce.exists():
                raise forms.ValidationError("Este trabajador ya tiene un turno asignado en esta fecha.")
        
        return cleaned_data
