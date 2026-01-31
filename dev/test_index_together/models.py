from django.db import models


class IndexTogether1(models.Model):
    """Single migration with index_together"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)

    class Meta:
        index_together = ('field1', 'field2')  # init


class IndexTogether2(models.Model):
    """Seqential migrations with index_together"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)
    field3 = models.CharField(max_length=10)

    class Meta:
        """Meta changed"""
#        # 0001 - no index together
#        index_together = ('field1', 'field2')  # 0002
        index_together = ('field1', 'field2', 'field3')  # 0003


class IndexTogether3(models.Model):
    """Sequential migrations with custom column names in index_together"""

    field1 = models.CharField(max_length=10, db_column='test_field1')
    field2 = models.CharField(max_length=10, db_column='test_field2')
    field3 = models.CharField(max_length=10, db_column='test_field3')

    class Meta:
        """Meta changed"""
#        # 0001 - no index together
#        index_together = ('field1', 'field2')  # 0002
        index_together = ('field1', 'field2', 'field3')  # 0003
