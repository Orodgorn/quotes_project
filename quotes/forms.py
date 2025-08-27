from django import forms
from django.core.exceptions import ValidationError

from .models import Quote, Source


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }


class QuoteForm(forms.ModelForm):
    source_name = forms.CharField(max_length=200, label="Название источника",
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    source_type = forms.ChoiceField(choices=Source.SOURCE_TYPES, label="Тип источника",
                                    widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Quote
        fields = ['text', 'weight']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        source_name = cleaned_data.get('source_name')
        source_type = cleaned_data.get('source_type')
        text = cleaned_data.get('text')

        if source_name and source_type and text:
            # Получаем или создаем источник для проверки
            source, created = Source.objects.get_or_create(
                name=source_name,
                type=source_type,
                defaults={'name': source_name, 'type': source_type}
            )

            # Проверяем, не превышен ли лимит цитат
            if source.quotes.count() >= 3:
                raise ValidationError("У этого источника уже максимальное количество цитат (3).")

            # Проверяем, не существует ли уже такая цитата
            if Quote.objects.filter(text=text, source=source).exists():
                raise ValidationError("Такая цитата уже существует для этого источника.")

            # Сохраняем источник для использования в save()
            self.cleaned_data['source_obj'] = source

        return cleaned_data

    def save(self, commit=True):
        # Используем уже созданный и проверенный источник
        source = self.cleaned_data.get('source_obj')

        if not source:
            # Если источника нет (на всякий случай), создаем его
            source_name = self.cleaned_data['source_name']
            source_type = self.cleaned_data['source_type']
            source, created = Source.objects.get_or_create(
                name=source_name,
                type=source_type,
                defaults={'name': source_name, 'type': source_type}
            )

        quote = super().save(commit=False)
        quote.source = source

        if commit:
            quote.save()

        return quote