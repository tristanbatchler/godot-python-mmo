extends Node

var data: Dictionary = {}

func init(initial_data: Dictionary):
	update(initial_data)
	return self

func update(model_delta: Dictionary):
	for key in model_delta:
		data[key] = model_delta[key]
