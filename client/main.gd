extends Node

# Imports
const NetworkClient = preload("res://websockets_client.gd")
const Packet = preload("res://packet.gd")
const Actor = preload("res://Actor.tscn")
const Player = preload("res://Player.tscn")
const Chatbox = preload("res://Chatbox.tscn")

var _network_client = NetworkClient.new()
var _world
var _chatbox
var state: FuncRef
var _actors: Dictionary = {}
var _player = null

onready var _login_screen = get_node("Login")

func _ready() -> void:
	_network_client.connect("connected", self, "_handle_client_connected")
	_network_client.connect("disconnected", self, "_handle_client_disconnected")
	_network_client.connect("error", self, "_handle_network_error")
	_network_client.connect("data", self, "_handle_network_data")
	add_child(_network_client) # Begin network_client ready and process
	_network_client.connect_to_server('127.0.0.1', 8081)

	_login_screen.connect("login", self, "_handle_login_button")
	_login_screen.connect("register", self, "_handle_register_button")
	
func LOGIN(p):
	match p.action:
		"OK":
			_enter_game()
		"Deny":
			OS.alert("Username or password incorrect")

func REGISTER(p):
	match p.action:
		"OK":
			OS.alert("Registration successful")
		"Deny":
			OS.alert("Can't register")
		
func PLAY(p):
	match p.action:
		"ModelDelta":
			var model_delta: Dictionary = p.payloads[0]
			_update_models(model_delta)

		"Chat":
			var message: String = p.payloads[0]
			_chatbox.add_message(message)

func _update_models(model_delta: Dictionary):
	var model_id: int = model_delta["id"]
	match model_delta["model_type"]:
		"Actor":
			if model_id in _actors:
				_actors[model_id].update(model_delta)
			else:
				var a
				if not _player:  # The first model we ever receive will be our player
					a = Player.instance().init(model_delta)
					a.connect("movement_input", self, "_send_player_direction")
				else:
					a = Actor.instance().init(model_delta)
				_actors[model_id] = a
				add_child(a)
			print("Received actor data: %s" % JSON.print(model_delta))

func _handle_login_button(username: String, password: String) -> void:
	state = funcref(self, "LOGIN")
	var p: Packet = Packet.new("Login", [username, password])
	_network_client.send_packet(p)

func _handle_register_button(username: String, password: String) -> void:
	state = funcref(self, "REGISTER")
	var p: Packet = Packet.new("Register", [username, password])
	_network_client.send_packet(p)

func _enter_game():
	state = funcref(self, "PLAY")

	# Remove the login screen
	remove_child(_login_screen)

	# Instance the chatbox
	_chatbox = Chatbox.instance()
	_chatbox.connect("message_sent", self, "send_chat")
	add_child(_chatbox)


func send_chat(text: String) -> void:
	var p: Packet = Packet.new("Chat", [text])
	_network_client.send_packet(p)

func _send_player_direction(dir_x: float, dir_y: float) -> void:
	var p: Packet = Packet.new("Direction", [dir_x, dir_y])
	_network_client.send_packet(p)

func _handle_client_connected() -> void:
	print("Client connected to server!")
	
func _handle_client_disconnected(was_clean: bool) -> void:
	OS.alert("Disconnected %s" % ['cleanly' if was_clean else 'unexpectedly'])
	get_tree().quit()

func _handle_network_data(data: String) -> void:
	print("Received server data: ", data)
	var action_payloads: Array = Packet.json_to_action_payloads(data)
	var p: Packet = Packet.new(action_payloads[0], action_payloads[1])
	# Pass the packet to our current state
	state.call_func(p)
	
func _handle_network_error() -> void:
	OS.alert("There was an error")
