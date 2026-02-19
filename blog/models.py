from django.core.files.storage import storages
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_jalali.db import models as jmodels
from django.urls import reverse
from django.core.validators import ValidationError
from django_resized import ResizedImageField


class Account(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE,related_name='account')
    birthdate = jmodels.jDateField(blank=True, null=True,verbose_name='تاریخ تولد')
    bio=models.TextField(blank=True, null=True,verbose_name='درباره')
    photo=ResizedImageField(upload_to="account_photo",size=[400,300],quality=60,crop=['middle','top'],
                            blank=True,null=True,verbose_name='عکس پروفایل')
    job=models.CharField(max_length=100,verbose_name='شغل')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'حساب کاربری'
        verbose_name_plural = 'حساب های کاربری'
        ordering=('-birthdate',)


def generate_slug(slug: str):
    temp = slug.split(" ")
    result = "_".join(temp)
    return result

class PublishedManager(models.Manager):
    def published(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

    def rejected(self):
        return super().get_queryset().filter(status=Post.Status.REJECTED)

    def draft(self):
        return super().get_queryset().filter(status=Post.Status.DRAFT)

class Post(models.Model):
    title = models.CharField(max_length=250, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیح")
    slug = models.SlugField(max_length=250, unique=True, null=True, blank=True)
    publish = jmodels.jDateTimeField(default=timezone.now, db_index=True, verbose_name="تاریخ انتشار")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")
    updated = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ آپدیت")
    reading_time=models.PositiveIntegerField(verbose_name='مدت زمان مطالعه',null=True,blank=True)

    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PP", "Published"
        REJECTED = "RJ", "Rejected"

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")

    CATEGORY_CHOICES = (
    ('تکنولوژی','tech'),
    ('عمومی','public'),
    )

    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='دسته بندی')

    categories=models.ManyToManyField(
        'Post',
        through="Categories",
        related_name="categories",
        on_delete=models.CASCADE,
        verbose_name="دسته بندی ها",
    )

    objects = jmodels.jManager()
    status_state = PublishedManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail_page',kwargs={"slug":self.slug})

    def delete(self, *args, **kwargs):
        for img in self.images_post.all():
            storage,path=img.image_file.storage,img.image_file.path
            storage.delete(path)
        return super().delete(self, *args, **kwargs)

    class Meta:
        verbose_name = "پست"
        verbose_name_plural = "پست ها"
        ordering = ['-publish']
        indexes = [models.Index(fields=['-publish'])]


class Ticket(models.Model):
    message=models.TextField(verbose_name='پیام')
    name = models.CharField(verbose_name='نام',max_length=50)
    phone=models.CharField(verbose_name='تلفن',max_length=15)
    email=models.EmailField(verbose_name='ایمیل',max_length=50)
    subject=models.CharField(verbose_name='موضوع')
    status=models.CharField(verbose_name='وضعیت',null=True,blank=True)


    def __str__(self):
        return self.subject

    class Meta:
        verbose_name="تیکت"
        verbose_name_plural="تیکت ها"


@receiver(pre_save, sender=Post)
def set_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = generate_slug(instance.title)


class Comment(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comment')
    name=models.CharField(verbose_name='نام',max_length=50)
    body=models.TextField(verbose_name='متن پیام')
    publish = jmodels.jDateTimeField(default=timezone.now, db_index=True, verbose_name="تاریخ انتشار")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")
    active=models.BooleanField(default=False,verbose_name='فعال/غیرفعال')


    class Meta:
        verbose_name='کامنت'
        verbose_name_plural='کامنت ها'
        ordering=['-created']
        indexes=[models.Index(fields=['-created'])]

    def __str__(self):
        return f'{self.name} : {self.post}'

class Image(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='images_post')
    title=models.CharField(verbose_name='عنوان تصویر',max_length=50)
    description=models.TextField(verbose_name='توضیحات',max_length=500,null=True,blank=True)
    created=jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")
    image_file=ResizedImageField(upload_to="images/",null=True,blank=True,size=[150, 150],crop=['middle', 'center'],quality=75)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name='تصویر'
        verbose_name_plural='تصویر ها'
        ordering=['-created']
        indexes=[models.Index(fields=['-created'])]