from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Tag(models.Model):
    blog_tags = models.CharField(max_length=50)
    def __str__(self) -> str:
        return self.blog_tags

class Blogs(models.Model): 
    blog_title= models.CharField(max_length=100)
    blog_description = models.TextField()
    host=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Approved')
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="images/")

    def get_absolute_url(self):
        return reverse('blog', args=[str(self.pk)])
    class Meta:
        ordering = ['-last_updated','-created']

    def __str__(self) -> str:
        return self.blog_title

class BlogView(models.Model):
    view_count = models.IntegerField(default=0)
    
class Comments(models.Model):
    
    host = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    blog = models.ForeignKey(Blogs,on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_updated','-created']

    def __str__(self):
        return self.text
    
class MailNotification(models.Model):
    email = models.EmailField(unique=True)
    subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.email

