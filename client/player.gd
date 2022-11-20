extends "res://actor.gd"

signal movement_input(dir_x, dir_y)

func _ready():
	is_player = true

func _input(event):
	if event.is_action_released("click"):
		var intended_target = body.get_global_mouse_position()

		if (intended_target.x < 60 or intended_target.y < get_viewport().size.y - 50):
			target = intended_target
			emit_signal("movement_input", target.x, target.y)
