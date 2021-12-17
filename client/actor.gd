extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")

var target = Vector2()
var velocity = Vector2()

# TODO: Get this speed value from the server
export (int) var speed = 200

func update(model_delta: Dictionary):
	.update(model_delta)
	var ientity = model_delta["instanced_entity"]
	target = Vector2(float(ientity["x"]), float(ientity["y"]))
	print("set my target to: ", target)

func _physics_process(delta):
	velocity = (target - body.position).normalized() * speed
	if (target - body.position).length() > 5:
		velocity = body.move_and_slide(velocity)
