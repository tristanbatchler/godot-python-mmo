extends Control

onready var username_field: LineEdit = get_node("VBoxContainer/GridContainer/LineEdit_Username")
onready var password_field: LineEdit = get_node("VBoxContainer/GridContainer/LineEdit_Password")
onready var login_button: Button = get_node("VBoxContainer/CenterContainer/HBoxContainer/Button_Login")
onready var register_button: Button = get_node("VBoxContainer/CenterContainer/HBoxContainer/Button_Register")
onready var popup: CenterContainer = get_node("Popup")
onready var select_left_button: Button = get_node("Popup/VBoxContainer/HBoxContainer/LeftButton")
onready var select_right_button: Button = get_node("Popup/VBoxContainer/HBoxContainer/RightButton")
onready var avatar_sprite: Sprite = get_node("Popup/VBoxContainer/HBoxContainer/Sprite")
onready var avatar_animation_player: AnimationPlayer = get_node("Popup/VBoxContainer/HBoxContainer/Sprite/AnimationPlayer")
onready var confirm_registration_button: Button = get_node("Popup/VBoxContainer/HBoxContainer/OK")
onready var animation_change_timer: Timer = get_node("Timer")

signal login(username, password)
signal register(username, password, avatar_id)

var avatar_id = 0
var animations_list = ["walk_down", "walk_up", "walk_right", "walk_left"]
var current_animation_index = 0

func _ready():
	popup.visible = false
	password_field.secret = true
	login_button.connect("pressed", self, "_login")
	register_button.connect("pressed", self, "_register")
	select_left_button.connect("pressed", self, "_select_left")
	select_right_button.connect("pressed", self, "_select_right")
	confirm_registration_button.connect("pressed", self, "_confirm_registration")

func _login() -> void:
	emit_signal("login", username_field.text, password_field.text)

func _register() -> void:
	popup.visible = true
	avatar_animation_player.play(animations_list[current_animation_index])
	register_button.disabled = true
	
func _confirm_registration() -> void:
	emit_signal("register", username_field.text, password_field.text, avatar_id)
	register_button.disabled = false

func _select_left() -> void:
	avatar_id = (avatar_id - 1) % 6
	if avatar_id == -1:
		avatar_id = 5
	_update_sprite()

func _select_right() -> void:
	avatar_id = (avatar_id + 1) % 6
	_update_sprite()
	
func _update_sprite() -> void:
	avatar_sprite.set_region_rect(Rect2(Vector2(369, avatar_id * 48 + 1), Vector2(63, 47)))
	
func _process(delta):
	if animation_change_timer.is_stopped():
		current_animation_index = (current_animation_index + 1) % 4
		avatar_animation_player.play(animations_list[current_animation_index])
		animation_change_timer.start()
