extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")

var target = null
var velocity = Vector2.ZERO

# TODO: Get this speed value from the server
export (int) var speed = 200

func update(model_delta: Dictionary):
	.update(model_delta)
	var ientity = model_delta["instanced_entity"]
	target = Vector2(float(ientity["x"]), float(ientity["y"]))
	print("set my target to: ", target)

func _physics_process(delta):
	if target:
		if (target - body.position).length() > 5:
			velocity = (target - body.position) * 20
		else:
			target = null

	velocity = body.move_and_slide(velocity)
