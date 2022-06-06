extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")

var target = null
var velocity = Vector2.ZERO
var actor_name = null

func _ready():
	if name:
		label.text = str(actor_name) + ":" + str(velocity)
	
func update(model_delta: Dictionary):
	.update(model_delta)
	
	var ientity = model_delta["instanced_entity"]
	target = Vector2(float(ientity["x"]), float(ientity["y"]))
#	if body != null and body.position != null:
#		velocity = (target - body.position)
	
	print("Set ", str(model_delta["id"]),  "'s target to: ", target)

	if "entity" in ientity:
		actor_name = model_delta["id"]

func _physics_process(delta):
	velocity = target - body.position
	velocity = body.move_and_slide(velocity)
	
	if name:
		label.text = str(actor_name) + ":" + str(velocity)
