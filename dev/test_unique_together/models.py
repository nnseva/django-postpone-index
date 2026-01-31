from django.db import models


class UniqueTogether1(models.Model):
    """Single migration with unique_together"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)

    class Meta:
        unique_together = ('field1', 'field2')  # init


class UniqueTogether2(models.Model):
    """Seqential migrations with unique_together"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)
    field3 = models.CharField(max_length=10)

    class Meta:
        """Meta changed"""
#        # 0001 - no unique together
#        unique_together = ('field1', 'field2')  # 0002
        unique_together = ('field1', 'field2', 'field3')  # 0003


class UniqueTogether3(models.Model):
    """Sequential migrations with custom column names in unique_together"""

    field1 = models.CharField(max_length=10, db_column='test_field1')
    field2 = models.CharField(max_length=10, db_column='test_field2')
    field3 = models.CharField(max_length=10, db_column='test_field3')

    class Meta:
        """Meta changed"""
#        # 0001 - no unique together
#        unique_together = ('field1', 'field2')  # 0002
        unique_together = ('field1', 'field2', 'field3')  # 0003
