from django.db import models


class User(models.Model):
    username = models.CharField(unique=True, max_length=20)
    password = models.CharField(max_length=1024)


class Entity(models.Model):
    name = models.CharField(max_length=100)


class InstancedEntity(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING)
    x = models.FloatField()
    y = models.FloatField()


class Container(models.Model):
    instanced_entity = models.ForeignKey(InstancedEntity, unique=True, on_delete=models.CASCADE)


class Item(models.Model):
    entity = models.ForeignKey(Entity, unique=True, on_delete=models.DO_NOTHING)
    price = models.FloatField()


class ContainerItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    container = models.ForeignKey(Container, unique=True, on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField()


class Actor(models.Model):
    instanced_entity = models.ForeignKey(InstancedEntity, unique=True, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Container, unique=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, unique=True, null=True, default=None, on_delete=models.DO_NOTHING)

    def get_name(self):
        return self.instanced_entity.entity.name
