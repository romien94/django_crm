from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import reverse, redirect
from django.http.response import JsonResponse

from .models import Lead, Category, FollowUp
from .forms import (
    LeadForm,
    CustomUserCreationForm,
    AssignAgentForm,
    LeadCategoryUpdateForm,
    CategoryForm,
    FollowUpForm
)
from agents.mixins import OrganizerAndLoginRequiredMixin


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class LandingPage(generic.TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super(LandingPage, self).dispatch(request, *args, **kwargs)


class DashboardView(OrganizerAndLoginRequiredMixin, generic.TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(DashboardView, self).get_context_data(**kwargs)
        queryset = Lead.objects.filter(organization=user.userprofile)
        month_ago = datetime.today() - timedelta(days=30)
        context.update({
            'total_lead_count': queryset.count(),
            'total_new_leads': queryset.filter(date_added__gte=month_ago).count(),
            'total_converted_new_leads': queryset.filter(category__name='Converted', date_added__gte=month_ago).count()
        })
        return context


class LeadListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'leads'
    template_name = 'leads/lead_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization).filter(agent__user=user,
                                                                                        agent__isnull=False)
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organizer:
            context.update({
                'unassigned_leads': Lead.objects.filter(organization=user.userprofile, agent__isnull=True)
            })
        return context


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    context_object_name = 'lead'
    template_name = 'leads/lead_detail.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization).filter(agent__user=user)
        return queryset


class LeadCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    form_class = LeadForm
    success_url = reverse_lazy('leads:lead-list')
    template_name = 'leads/lead_create.html'

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile
        lead.save()
        send_mail(
            'A lead has been created',
            'Go to the site to see the new lead',
            from_email='test@test.com',
            recipient_list=['test@test.com']
        )
        messages.success(self.request, 'The lead has been successfully created')
        return super(LeadCreateView, self).form_valid(form)


class LeadUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    form_class = LeadForm
    template_name = 'leads/lead_update.html'

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        messages.success(self.request, 'The lead has been successfully updated')
        return reverse('leads:lead-list')


class LeadDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/lead_delete.html'

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        messages.success(self.request, 'The lead has been successfully deleted')
        return reverse('leads:lead-list')


class AssignAgentView(OrganizerAndLoginRequiredMixin, generic.FormView):
    template_name = 'leads/assign_agent.html'
    form_class = AssignAgentForm
    success_url = reverse_lazy('leads:lead-list')

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        agent = form.cleaned_data.get('agent')
        lead = Lead.objects.get(id=self.kwargs.get('pk'))
        lead.agent = agent
        lead.save()
        messages.success(self.request, f'The {agent.user.username} has been assigned to {lead.first_name} {lead.last_name}')
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context.update({
            'unassigned_leads_count': Lead.objects.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'leads/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        category = self.get_object()
        context.update({
            'category': category
        })

        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset


class CategoryCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = 'leads/category_create.html'
    form_class = CategoryForm
    success_url = reverse_lazy('leads:category-list')

    def form_valid(self, form):
        category = form.save(commit=False)
        organization = self.request.user.userprofile
        category.organization = organization
        category.save()
        messages.success(self.request, f'The {category.name} category has been successfully created')
        return super(CategoryCreateView, self).form_valid(form)


class CategoryUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/category_update.html'
    form_class = CategoryForm
    success_url = reverse_lazy('leads:category-list')

    def get_queryset(self):
        return Category.objects.filter(organization=self.request.user.userprofile)


class CategoryDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/category_delete.html'
    success_url = reverse_lazy('leads:category-list')
    queryset = Category.objects.all()

    def get_queryset(self):
        return Category.objects.filter(organization=self.request.user.userprofile)


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/lead_category_update.html'
    form_class = LeadCategoryUpdateForm

    def form_valid(self, form):
        lead_before_update = self.get_object()
        converted_category = Category.objects.get(name='Converted')
        lead = form.save(commit=False)
        if form.cleaned_data.get('category') == converted_category:
            if lead_before_update.category != converted_category:
                lead.converted_date = datetime.now()
        lead.save()
        return super(LeadCategoryUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('leads:lead-detail', kwargs={'pk': self.get_object().pk})

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization).filter(agent__user=user)
        return queryset


class LeadJsonView(generic.View):
    def get(self, request, *args, **kwargs):
        data = {}
        queryset = Lead.objects.all()
        for i in queryset:
            data[i.first_name] = i.last_name
        return JsonResponse(data)


class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'leads/followup_create.html'
    form_class = FollowUpForm

    def get_success_url(self):
        return reverse('leads:lead-detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super(FollowUpCreateView, self).get_context_data(**kwargs)
        context.update({
            'lead': Lead.objects.get(pk=self.kwargs.get('pk'))
        })
        return context

    def form_valid(self, form):
        lead = Lead.objects.get(pk=self.kwargs.get('pk'))
        followup = form.save(commit=False)
        followup.lead = lead
        followup.save()
        return super(FollowUpCreateView, self).form_valid(form)


class FollowUpUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/followup_update.html'
    form_class = FollowUpForm
    queryset = FollowUp.objects.all()

    def get_success_url(self):
        return reverse('leads:lead-detail', kwargs={'pk': self.get_object().lead.pk})

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = FollowUp.objects.filter(lead__organization=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(lead__organization=user.agent.userprofile)
            queryset = queryset.filter(lead__agent__user=user)
        return queryset


class FollowUpDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/followup_delete.html'
    queryset = FollowUp.objects.all()

    def get_success_url(self):
        followup = FollowUp.objects.get(pk=self.kwargs.get('pk'))
        return reverse('leads:lead-detail', kwargs={'pk': followup.lead.pk})

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = FollowUp.objects.filter(lead__organization=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(lead__organization=user.agent.userprofile)
            queryset = queryset.filter(lead__agent__user=user)
        return queryset

