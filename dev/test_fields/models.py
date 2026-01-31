from django.db import models

class UniqueField1(models.Model):
    """Sequential migrations with unique field"""

    # Changing history
#    field1 = models.CharField(max_length=10, unique=True)  # 0001
#    field1 = models.CharField(max_length=10)  # 0002
    field1 = models.CharField(max_length=10, unique=True)  # 0003


class UniqueField2(models.Model):
    """Sequential migrations with unique field"""

    # Changing history
#    field1 = models.CharField(max_length=10)  # 0001
#    field2 = models.CharField(max_length=10, unique=True)  # 0001
#    field1 = models.CharField(max_length=10, unique=True)  # 0002
#    # no field2  # 0002
    field1 = models.CharField(max_length=10)  # 0003
    # no field2  # 0003


class IndexedField1(models.Model):
    """Sequential migrations with indexed field"""

    # Changing history
#    field1 = models.CharField(max_length=10, db_index=True)  # 0001
#    field1 = models.CharField(max_length=10)  # 0002
    field1 = models.CharField(max_length=10, db_index=True)  # 0003


class IndexedField2(models.Model):
    """Sequential migrations with indexed field"""

    # Changing history
#    field1 = models.CharField(max_length=10)  # 0001
#    field2 = models.CharField(max_length=10, db_index=True)  # 0001
#    field1 = models.CharField(max_length=10, db_index=True)  # 0002
#    # no field2  # 0002
    field1 = models.CharField(max_length=10)  # 0003
    # no field2  # 0003
