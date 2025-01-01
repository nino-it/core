from django import forms
from django.db.models import Count
from .models import Article
from django.utils import timezone
from django.utils.timezone import now

class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles
    """

    time_scheduled = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=now().strftime('%Y-%m-%dT%H:%M'),  # Ensure no seconds are included
        input_formats=['%Y-%m-%dT%H:%M'],  # Match the datetime-local format
    )

    class Meta:
        model = Article
        fields = ['title', 'text', 'category', 'priority', 'time_scheduled']
        widgets = {
            'time_scheduled': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local', 
                    'value': ''  # This sets an empty default value
                }
            ),
            'category': forms.TextInput(attrs={
                'list': 'category-list',
                'autocomplete': 'off'
            })
        }
        
    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validation if needed
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['time_scheduled'].initial = None

        if self.instance and self.instance.pk:
            self.fields['time_scheduled'].initial = None

        # Add autocomplete functionality for category
        self.categories = Article.objects.values_list('category', flat=True) \
            .annotate(count=Count('id')) \
            .order_by('-count')