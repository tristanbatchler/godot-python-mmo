extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")

var target = null
var velocity = Vector2.ZERO
var actor_name = null
var is_player = false
var correction_diff = Vector2.ZERO
var correction_size_squared =  0.0
var correction_velocity = Vector2.ZERO
var correction_radius_big = 50
var correction_radius_small = 30

	
func update(model_delta: Dictionary):
	.update(model_delta)
	
	var ientity = model_delta["instanced_entity"]
	target = Vector2(float(ientity["x"]), float(ientity["y"]))
	
	print("Set ", str(model_delta["id"]),  "'s target to: ", target)

	if "entity" in ientity:
		actor_name = model_delta["id"]
		
	
	if is_player and body:
		correction_diff = target - body.position
		correction_size_squared = correction_diff.length_squared()
		
		# If the player is stopped, allow more sensitive corrections
		if velocity.length_squared() < 100: # TODO: Magic number for detecting if player is more or less "stopped"
			if correction_size_squared > pow(correction_radius_small, 2):
				correction_velocity = correction_diff


func _physics_process(delta):
	if is_player:
		body.position += (velocity + correction_velocity) * delta
		
		# If the player is detected to be very off, correct during physics process
		if correction_size_squared > pow(correction_radius_big, 2):
			correction_velocity = target - body.position
			
	# Non-player actors are treated differently on the screen, don't need their movement to be "smooth"
	else:
		body.position += (target - body.position) * delta
		
		
	if name:
		label.text = str(actor_name) + ' : ' + str(correction_velocity)
		
	
