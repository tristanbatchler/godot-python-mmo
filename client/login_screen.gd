extends Control

onready var username_field: LineEdit = get_node("VBoxContainer/GridContainer/LineEdit_Username")
onready var password_field: LineEdit = get_node("VBoxContainer/GridContainer/LineEdit_Password")
onready var login_button: Button = get_node("VBoxContainer/CenterContainer/HBoxContainer/Button_Login")
onready var register_button: Button = get_node("VBoxContainer/CenterContainer/HBoxContainer/Button_Register")


signal login(username, password)
signal register(username, password, avatar_id)

func _ready():
	password_field.secret = true
	login_button.connect("pressed", self, "_login")
	register_button.connect("pressed", self, "_register")

func _login() -> void:
	emit_signal("login", username_field.text, password_field.text)

func _register() -> void:
	var avatar_id = 0
	emit_signal("register", username_field.text, password_field.text, avatar_id)
