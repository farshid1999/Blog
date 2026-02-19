from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name="وبلاگ"

    # def ready(self):
    #     from blog import models
    #     global my_list
    #     try:
    #         my_list = list(models.Post.status_state.published().all())
    #         print(my_list)
    #     except:
    #         pass

