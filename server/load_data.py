# Required for importing the server app (upper dir)
import sys
import pathlib
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

from server import manage
from server import models


ent_floor = models.Entity(name="Floor")
ent_floor.save()

inst_floor = models.InstancedEntity(entity=ent_floor, x=3, y=5)
inst_floor.save()

cont_floor = models.Container(instanced_entity=inst_floor)
cont_floor.save()


ent_beer = models.Entity(name="Beer")
ent_beer.save()

item_beer = models.Item(entity=ent_beer, price=5.0)
item_beer.save()

cont_item_beer = models.ContainerItem(item=item_beer, container=cont_floor, quantity=1)
cont_item_beer.save()
