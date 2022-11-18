extends "res://actor.gd"

signal movement_input(dir_x, dir_y)

func _ready():
	is_player = true

func _input(event):
	if event.is_action_released("click"):
		target = body.get_global_mouse_position()
		emit_signal("movement_input", target.x, target.y)
