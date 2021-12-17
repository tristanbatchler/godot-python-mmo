from django.db import models
from django.forms import model_to_dict

# TODO: This might be better as a method of each entity type - but I know inheritance is screwy here...
def create_dict(model: models.Model) -> dict:
    """
    Recursively creates a dictionary based on the supplied model and all its foreign relationships.
    """
    d: dict = model_to_dict(model)
    model_type: type = model.__class__
    
    if model_type in (Item, InstancedEntity):
        d["entity"] = create_dict(model.entity)
    elif model_type == Container:
        d["instanced_entity"] = create_dict(model.instanced_entity)
    elif model_type == ContainerItem:
        d["item"] = create_dict(model.item)
        d["container"] = create_dict(model.container)
    elif model_type == Actor:
        d["instanced_entity"] = create_dict(model.instanced_entity)
        d["inventory"] = create_dict(model.inventory)
        d["user"] = create_dict(model.user)
    
    return d


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
    # TODO: Add speed

    def get_name(self):
        return self.instanced_entity.entity.name
