import django
from django.db import models


class UniqueField1(models.Model):
    """Sequential migrations with unique field"""

    # Changing history
    # field1 = models.CharField(max_length=10, unique=True)  # 0001
    renamed_field1 = models.CharField(max_length=10, unique=True)  # 0002


class UniqueTogether1(models.Model):
    """Sequential migrations with unique-together fields"""

    # Changing history
    # field1 = models.CharField(max_length=10)  # 0001
    # field2 = models.CharField(max_length=10)  # 0001
    renamed_field1 = models.CharField(max_length=10)  # 0002
    renamed_field2 = models.CharField(max_length=10)  # 0002

    class Meta:
        # unique_together = (('field1', 'field2'),)
        unique_together = (('renamed_field1', 'renamed_field2'),)


if django.VERSION < (5, 1):
    class IndexTogether1(models.Model):
        """Sequential migrations with index-together fields"""

        # Changing history
        # field1 = models.CharField(max_length=10)  # 0001
        # field2 = models.CharField(max_length=10)  # 0001
        renamed_field1 = models.CharField(max_length=10)  # 0002
        renamed_field2 = models.CharField(max_length=10)  # 0002

        class Meta:
            # index_together = (('field1', 'field2'),)  # 0001
            index_together = (('renamed_field1', 'renamed_field2'),)  # 0002


class ExplicitConstraint1(models.Model):
    """Sequential migrations with explicit named constraint in Meta"""

    # Changing history
    # field1 = models.CharField(max_length=10)  # 0001
    # field2 = models.CharField(max_length=10)  # 0001
    renamed_field1 = models.CharField(max_length=10)  # 0002
    renamed_field2 = models.CharField(max_length=10)  # 0002

    class Meta:
        # 0001
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['field1', 'field2'],
        #         condition=~(models.Q(field1='<empty>') & models.Q(field2='<empty>')),
        #         name='explicit_rename_constraint1_non_empty'
        #     )
        # ]
        # 0002
        constraints = [
            models.UniqueConstraint(
                fields=['renamed_field1', 'renamed_field2'],
                condition=~(models.Q(renamed_field1='<empty>') & models.Q(renamed_field2='<empty>')),
                name='explicit_rename_constraint1_non_empty'
            )
        ]


class ExplicitIndex1(models.Model):
    """Sequential migrations with explicit named index in Meta"""

    # field1 = models.CharField(max_length=10)  # 0001
    # field2 = models.CharField(max_length=10)  # 0001
    renamed_field1 = models.CharField(max_length=10)  # 0002
    renamed_field2 = models.CharField(max_length=10)  # 0002

    class Meta:
        """Modified Meta"""
        # indexes = [models.Index(fields=['field1', 'field2'], name='explicit_rename_index1_index')]  # 0001
        indexes = [models.Index(fields=['renamed_field1', 'renamed_field2'], name='explicit_rename_index1_index')]  # 0002
