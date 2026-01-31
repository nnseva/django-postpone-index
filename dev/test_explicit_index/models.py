from django.db import models


class ExplicitIndex1(models.Model):
    """Sequential migrations with explicit named index in Meta"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)

    class Meta:
        """Modified Meta"""
#       0001 (no index)
#        indexes = [models.Index(fields=['field1'], name='explicit_index1_index')]  # 0002
        indexes = [models.Index(fields=['field1', 'field2'], name='explicit_index1_index')]  # 0003
