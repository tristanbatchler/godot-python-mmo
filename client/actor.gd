extends "res://model.gd"

onready var body: KinematicBody2D = get_node("KinematicBody2D")
onready var label: Label = get_node("KinematicBody2D/Label")
onready var _sprite: Sprite = get_node("KinematicBody2D/Sprite")
onready var _animation_player: AnimationPlayer = get_node("KinematicBody2D/Sprite/AnimationPlayer")
onready var speechbox: Label = get_node("KinematicBody2D/Chat")
onready var _speech_timer: Timer = get_node("Timer")


var target = null
var server_target = null
var is_player = false
var correction_diff = Vector2.ZERO
var correction_size_squared =  0.0
var correction_radius = 100
var velocity = Vector2.ZERO
var actor_name = ""
var direction_angle: float = 0
var avatar_id: int = 0
var initial_position_set: bool = false

	
func update(model_delta: Dictionary):
	.update(model_delta)
	
	var ientity = model_delta["instanced_entity"]
	server_target = Vector2(float(ientity["x"]), float(ientity["y"]))
	actor_name = ientity["entity"]["name"]
	
	if "avatar_id" in model_delta:
		avatar_id = model_delta["avatar_id"]
	
	if label:
		label.text = actor_name
	
#	print("Set ", str(model_delta["id"]),  "'s target to: ", server_target)
	
	if is_player and body:
		correction_diff = server_target - body.position
		correction_size_squared = correction_diff.length_squared()
		
	if body and not initial_position_set:
		body.position = server_target
		initial_position_set = true

func speak(message: String):
	self.speechbox.text = message
	_speech_timer.start()

func _physics_process(delta):
	if is_player and target:
		direction_angle = target.angle_to_point(body.position)
		velocity = body.position.direction_to(target) * 70
			
		if correction_size_squared > pow(correction_radius, 2):
			body.position = server_target
			correction_size_squared = 0
			
		if body.position.distance_squared_to(target) <= 25:
			velocity = Vector2.ZERO
	
	elif server_target:
			direction_angle = server_target.angle_to_point(body.position)
			velocity = body.position.direction_to(server_target) * 70
			
			if body.position.distance_squared_to(server_target) <= 25:
				velocity = Vector2.ZERO
	
	body.position += velocity * delta
		
func _process(delta):
	if velocity.length_squared() <= 25:
		_animation_player.stop()
	else:
		if (-PI/4 <= direction_angle and direction_angle < 0) or (0 <= direction_angle and direction_angle < PI/4):
			_animation_player.play("walk_right")
		elif -3*PI/4 <= direction_angle and direction_angle < -PI/4:
			_animation_player.play("walk_up")
		elif PI/4 <= direction_angle and direction_angle < 3*PI/4:
			_animation_player.play("walk_down")
		else:
			_animation_player.play("walk_left")
			
	if _speech_timer.is_stopped():
		self.speechbox.text = ""
		
	if _sprite:
		_sprite.set_region_rect(Rect2(Vector2(369, avatar_id * 48 + 1), Vector2(63, 47)))
