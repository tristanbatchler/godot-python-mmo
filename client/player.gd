extends "res://actor.gd"

var movement_direction = Vector2.ZERO

signal movement_input(dir_x, dir_y)

func _ready():
	is_player = true

func get_input():
	var old_movement_direction = movement_direction
	movement_direction = Vector2.ZERO
	if Input.is_action_pressed("right"):
		movement_direction.x += 1
	if Input.is_action_pressed("left"):
		movement_direction.x -= 1
	if Input.is_action_pressed("down"):
		movement_direction.y += 1
	if Input.is_action_pressed("up"):
		movement_direction.y -= 1
	movement_direction = movement_direction.normalized()
	
	# Client side velocity for smoothness
	velocity = movement_direction * 63.5

	if movement_direction != old_movement_direction:
		emit_signal("movement_input", movement_direction.x, movement_direction.y)

func _physics_process(delta):
	get_input()
	._physics_process(delta)
