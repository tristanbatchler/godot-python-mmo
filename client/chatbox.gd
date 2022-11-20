extends Control

onready var chat_log = get_node("CanvasLayer/VBoxContainer/RichTextLabel")
onready var input_label = get_node("CanvasLayer/VBoxContainer/HBoxContainer/Label")
onready var input_field = get_node("CanvasLayer/VBoxContainer/HBoxContainer/LineEdit")
onready var send_button = get_node("CanvasLayer/VBoxContainer/HBoxContainer/Button")

signal message_sent(message)

func _ready():
	input_field.connect("text_entered", self, "send_message")
	send_button.connect("pressed", self, "send_from_button")
	
func _gui_input(event: InputEvent):
	if event is InputEventKey and event.pressed:
		match event.scancode:
			KEY_ENTER:
				input_field.grab_focus()
			KEY_ESCAPE:
				input_field.release_focus()

func add_message(text: String):
	chat_log.bbcode_text += text + '\n'
	
func send_from_button():
	send_message(input_field.text)

func send_message(text: String):
	if len(text) > 0:
		input_field.text = ''
		
		# -2 means it came from the client
		emit_signal("message_sent", -2, text)
