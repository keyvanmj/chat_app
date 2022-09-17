from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

NOTIFICATION_TYPE = [
    ('PRIVATE','private'),
    ('PUBLIC','public'),
    ('GENERAL','general'),
]
class Notification(models.Model):
    # notification type for private or public room
    notification_type = models.CharField(choices=NOTIFICATION_TYPE,default=NOTIFICATION_TYPE[0],max_length=50)
    # for single user
    target = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name='from_user')
    redirect_url = models.URLField(max_length=500,null=True,blank=True,unique=False,help_text='The URL to be visited when a notification is clicked.')
    verb = models.CharField(max_length=1000,unique=False,blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        if self.verb:
            return self.verb
        else:
            return ''


    def get_content_object_type(self):

        return str(self.content_object.get_cname)

    def get_content_object_room(self):

        return str(self.content_object.get_room)



