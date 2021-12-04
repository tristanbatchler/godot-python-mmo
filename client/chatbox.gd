extends Control

onready var chat_log = get_node("VBoxContainer/RichTextLabel")
onready var input_label = get_node("VBoxContainer/HBoxContainer/Label")
onready var input_field = get_node("VBoxContainer/HBoxContainer/LineEdit")

signal message_sent(message)

func _ready():
	input_field.connect("text_entered", self, "text_entered")
	pass
	
func _input(event: InputEvent):
	if event is InputEventKey and event.pressed:
		match event.scancode:
			KEY_ENTER:
				input_field.grab_focus()
			KEY_ESCAPE:
				input_field.release_focus()

func add_message(username: String, text: String):
	chat_log.bbcode_text += "[%s]: %s\n" % [username, text]

func text_entered(text: String):
	input_field.text = ''
	emit_signal("message_sent", text)
