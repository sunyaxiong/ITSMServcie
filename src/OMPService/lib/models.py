from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseQuerySet(models.query.QuerySet):
    def delete(self):
        '''
        Update is_delete field to True.
        '''
        fields = (f.name for f in self.model._meta.fields)
        if 'is_deleted' in fields:
            return self.update(is_deleted=True)
        else:
            super(BaseQuerySet, self).delete()


class BaseManager(models.manager.Manager.from_queryset(BaseQuerySet)):
    def get_queryset(self):
        queryset = super(BaseManager, self).get_queryset()
        fields = (f.name for f in self.model._meta.fields)
        if 'is_deleted' in fields:
            queryset = queryset.filter(is_deleted=False)
        return queryset


class BaseModel(models.Model):
    is_deleted = models.BooleanField(default=False, editable=False, verbose_name=_('is deleted'))
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name=_('created datetime'))
    dt_updated = models.DateTimeField(auto_now=True, verbose_name=_('updated datetime'))

    objects = BaseManager()

    class Meta:
        abstract = True

    def delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return str(self.id)
