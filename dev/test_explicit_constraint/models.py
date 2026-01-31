from django.db import models


class ExplicitConstraint1(models.Model):
    """Sequential migrations with explicit named constraints in Meta"""

    field1 = models.CharField(max_length=10)
    field2 = models.CharField(max_length=10)
    field3 = models.CharField(max_length=10)

    class Meta:
        """Modified Meta"""
#       0001 - no constraint

#       0002
#        constraints = [
#            models.UniqueConstraint(
#                fields=['field1', 'field2'],
#                condition=~(models.Q(field1='<empty>') & models.Q(field2='<empty>')),
#                name='explicit_constraint1_non_empty'
#            )
#        ]

#       0003
        constraints = [
            models.UniqueConstraint(
                fields=['field1', 'field2', 'field3'],
                condition=~(models.Q(field1='<empty>') & models.Q(field2='<empty>') & models.Q(field3='<empty>')),
                name='explicit_constraint1_non_empty'
            )
        ]
