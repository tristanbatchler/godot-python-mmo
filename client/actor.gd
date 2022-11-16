extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")

var target = null
var velocity = Vector2.ZERO
var actor_name = null
var is_player = false
var sync_time = 1000
var time = OS.get_system_time_msecs()

func _ready():
	if name:
		label.text = str(actor_name) + ":" + str(velocity)
	
func update(model_delta: Dictionary):
	.update(model_delta)
	
	var ientity = model_delta["instanced_entity"]
	target = Vector2(float(ientity["x"]), float(ientity["y"]))
	
	print("Set ", str(model_delta["id"]),  "'s target to: ", target)

	if "entity" in ientity:
		actor_name = model_delta["id"]
	
	# Update the player's velocity (delcared in player.gd)
	if body and is_player:
		velocity = target - body.position
		

func _physics_process(delta):
	if is_player:
		body.position += velocity * delta
	else:
		# Other actors' positions are updated manually
		body.position += (target - body.position) * delta
	
	if name:
		label.text = str(actor_name) 
		
	
