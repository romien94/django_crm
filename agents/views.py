from django.views import generic
from django.urls import reverse_lazy
from django.core.mail import send_mail

from .models import Agent
from .forms import AgentForm
from .mixins import OrganizerAndLoginRequiredMixin

# Create your views here.


class AgentListView(OrganizerAndLoginRequiredMixin, generic.ListView):
    template_name = 'agents/agent_list.html'
    context_object_name = 'agents'

    def get_queryset(self):
        return Agent.objects.filter(organization=self.request.user.userprofile)


class AgentCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = 'agents/agent_create.html'
    form_class = AgentForm
    success_url = reverse_lazy('agents:agent-list')

    def get_queryset(self):
        return Agent.objects.filter(organization=self.request.user.userprofile)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organizer = False
        user.save()
        Agent.objects.create(user=user, organization=self.request.user.userprofile)
        send_mail(
            subject='You are invited to be an agent',
            message=f'You were added as an agent on the django crm. Please come and login to start working.',
            from_email='test@test.com',
            recipient_list=[
                user.email
            ]
        )
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView(OrganizerAndLoginRequiredMixin, generic.DetailView):
    template_name = 'agents/agent_detail.html'
    context_object_name = 'agent'

    def get_queryset(self):
        return Agent.objects.filter(organization=self.request.user.userprofile)


class AgentUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = 'agents/agent_update.html'
    form_class = AgentForm
    success_url = reverse_lazy('agents:agent-list')

    def get_queryset(self):
        return Agent.objects.filter(organization=self.request.user.userprofile)


class AgentDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'agents/agent_delete.html'
    success_url = reverse_lazy('agents:agent-list')

    def get_queryset(self):
        return Agent.objects.filter(organization=self.request.user.userprofile)
