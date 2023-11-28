from django import forms
from .models import CSVFile

class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = CSVFile
        fields = ['file']

class LocationSelectionForm(forms.Form):
    location = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        df = kwargs.pop('df', None)  # Get the DataFrame from kwargs
        super().__init__(*args, **kwargs)
        if df is not None:
            self.fields['location'].choices = self.get_location_choices(df)

    def get_location_choices(self, df):
        # Fetch unique location names from your CSV data
        if 'Location' in df.columns:
            return [('', 'Select a location')] + [(location, location) for location in df['Location'].unique()]
        else:
            return [('', 'No locations available')]
