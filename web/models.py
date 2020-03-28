from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    owner = models.ForeignKey(UserProfile, default=None, on_delete=models.CASCADE, related_name='owner')
    name = models.CharField(max_length=32, blank=True, default=None)
    color = models.CharField(blank=True, default=None, max_length=16)
    number_of_flashcards = models.IntegerField(default=0)
    number_of_lv1 = models.IntegerField(default=0)
    number_of_lv2 = models.IntegerField(default=0)
    number_of_lv3 = models.IntegerField(default=0)
    number_of_lv4 = models.IntegerField(default=0)
    number_of_lv5 = models.IntegerField(default=0)

    def __str__(self):
        return 'Owner: {} Name:{} Number of Flashcards: {}'.format(self.owner.user.username, self.name,
                                                                   self.number_of_flashcards)


class FlashCart(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    word = models.CharField(max_length=128)
    definition = models.CharField(max_length=512)
    synonyms = models.CharField(max_length=512)
    example = models.CharField(max_length=1024, default=None)
    lv = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return '{}-{}-{}'.format(self.word, self.lv, self.category)


def create_profile(sender, **kwargs):
    if kwargs['created']:
        UserProfile.objects.create(user=kwargs['instance'])


def add_number_of_category_flashcards(sender, **kwargs):
    if kwargs['created']:
        fcard = kwargs['instance']
        fcard.category.number_of_flashcards += 1
        fcard.category.number_of_lv1 += 1
        fcard.category.save()


post_save.connect(receiver=create_profile, sender=User)
post_save.connect(receiver=add_number_of_category_flashcards, sender=FlashCart)
