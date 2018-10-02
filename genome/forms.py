from django import forms
from genome.models import BoardGame, BGGUser


class GenomeForm(forms.ModelForm):
	class Meta:
		model = BoardGame
		fields = ['title']


class BGGUserForm(forms.Form):
	username = forms.CharField(help_text='BGG Username', required=True)
	owned = forms.BooleanField(help_text='Owned only?', required=False)
	rating = forms.IntegerField(help_text='At or above what rating is a like?',
								min_value=0, max_value=10, required=False)

	def clean_owned(self):
		"""
		URL parameter does not take a bool
		"""
		return int(self.cleaned_data.get('owned', 0))
