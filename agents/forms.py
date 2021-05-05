from django.contrib.auth import get_user_model
from django.forms import models

User = get_user_model()


class AgentForm(models.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
