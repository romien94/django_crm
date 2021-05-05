from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _


class User(AbstractUser):
    is_organizer = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User profile'))

    def __str__(self):
        return self.user.username


class LeadManager(models.Manager):
    def get_queryset(self):
        return super(LeadManager, self).get_queryset()

    def get_blank_categories(self):
        return self.get_queryset().filter(category__isnull=True)


class Lead(models.Model):
    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    age = models.PositiveSmallIntegerField(_('Age'), default=0)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey(to='agents.Agent', on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name=_('Agent'))
    category = models.ForeignKey('Category', related_name='leads', on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_('Category'))
    description = models.TextField(_('Description'))
    date_added = models.DateField(_('Date added'), auto_now_add=True)
    phone_number = models.CharField(_('Phone number'), max_length=20)
    email = models.EmailField()
    profile_picture = models.ImageField(_('Profile picture'), upload_to='profile_pictures/', null=True, blank=True)
    converted_date = models.DateTimeField(null=True, blank=True)

    objects = LeadManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(post_user_created_signal, User)


class Category(models.Model):
    name = models.CharField(max_length=30)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


def handle_upload_follow_ups(instance, filename):
    return f'lead_followups/lead_{instance.lead.pk}/{filename}'


class FollowUp(models.Model):
    lead = models.ForeignKey(Lead, related_name='followups', on_delete=models.CASCADE, verbose_name=_('Lead'))
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    notes = models.TextField(_('Notes'), null=True, blank=True)
    file = models.FileField(_('File'), upload_to=handle_upload_follow_ups, null=True, blank=True)

    def __str__(self):
        return f'{self.lead.first_name} {self.lead.last_name}'
