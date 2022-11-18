extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")

var target = null
var server_target = null
var is_player = false
var correction_diff = Vector2.ZERO
var correction_size_squared =  0.0
var correction_radius = 50
var velocity = Vector2.ZERO
var actor_name = ""

	
func update(model_delta: Dictionary):
	.update(model_delta)
	
	var ientity = model_delta["instanced_entity"]
	server_target = Vector2(float(ientity["x"]), float(ientity["y"]))
	actor_name = ientity["entity"]["name"]
	
	print("Set ", str(model_delta["id"]),  "'s target to: ", server_target)
	
	if is_player and body:
		correction_diff = server_target - body.position
		correction_size_squared = correction_diff.length_squared()


func _physics_process(delta):
	if is_player:
		if target and body.position.distance_squared_to(target) > 25:
			velocity = body.position.direction_to(target) * 70
			velocity = body.move_and_slide(velocity)
			
		if correction_size_squared > correction_radius:
			body.position = server_target
			correction_size_squared = 0
	
	elif server_target and body.position.distance_squared_to(server_target) > 25:
			velocity = body.position.direction_to(server_target) * 70
			velocity = body.move_and_slide(velocity)
	
	label.text = actor_name
		
	
