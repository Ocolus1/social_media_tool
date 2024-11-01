from django.db import models
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class TwitterAccount(models.Model):
    """
    Model to store Twitter account details associated with a user.

    Attributes:
        user (User): The Django user associated with this Twitter account.
        access_token (str): Access token for authenticating API requests.
        access_token_secret (str): Secret for the access token.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the TwitterAccount instance.

        Returns:
            str: The username of the associated Django user.
        """
        return self.user.username
