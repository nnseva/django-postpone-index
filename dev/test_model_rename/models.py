import django
from django.db import models


# class UniqueField1(models.Model):  # 0001
class UniqueField1Renamed(models.Model):  # 0002
    """Sequential migrations with unique field"""

    field1 = models.CharField(max_length=10, unique=True)


# class UniqueTogether1(models.Model):  # 0001
class UniqueTogether1Renamed(models.Model):  # 0002
    """Sequential migrations with unique-together fields"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)

    class Meta:
        unique_together = (('field1', 'field2'),)


if django.VERSION < (5, 1):
    # class IndexTogether1(models.Model):  # 0001
    class IndexTogether1Renamed(models.Model):  # 0002
        """Sequential migrations with index-together fields"""

        field1 = models.CharField(max_length=10)
        field2 = models.CharField(max_length=10)

        class Meta:
            index_together = (('field1', 'field2'),)


# class ExplicitConstraint1(models.Model):  # 0001
class ExplicitConstraint1Renamed(models.Model):  # 0002
    """Sequential migrations with explicit named constraint in Meta"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['field1', 'field2'],
                condition=~(models.Q(field1='<empty>') & models.Q(field2='<empty>')),
                name='explicit_model_constraint1_non_empty'
            )
        ]


# class ExplicitIndex1(models.Model):  # 0001
class ExplicitIndex1Renamed(models.Model):  # 0002
    """Sequential migrations with explicit named index in Meta"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)

    class Meta:
        indexes = [models.Index(fields=['field1', 'field2'], name='explicit_model_index1_index')]
