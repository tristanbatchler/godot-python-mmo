extends Node

# Imports
const NetworkClient = preload("res://websockets_client.gd")
const Packet = preload("res://packet.gd")

onready var _chatbox = get_node("Chatbox")
var _network_client = NetworkClient.new()

func _ready() -> void:
	_chatbox.connect("message_sent", self, "send_message")
	_network_client.connect("connected", self, "_handle_client_connected")
	_network_client.connect("disconnected", self, "_handle_client_disconnected")
	_network_client.connect("error", self, "_handle_network_error")
	_network_client.connect("data", self, "_handle_network_data")
	add_child(_network_client) # Begin network_client ready and process
	_network_client.connect_to_server('127.0.0.1', 8081)

func send_message(text: String) -> void:
	var p: Packet = Packet.new("Chat", [text])
	_network_client.send_packet(p)

func _handle_client_connected() -> void:
	print("Client connected to server!")
	
func _handle_client_disconnect(was_clean: bool) -> void:
	OS.alert("Disconnected %s" % ['cleanly' if was_clean else 'unexpectedly'])

func _handle_network_data(data: String) -> void:
	print("Received server data: ", data)
	var action_payloads: Array = Packet.json_to_action_payloads(data)
	var p: Packet = Packet.new(action_payloads[0], action_payloads[1])
	
	if p.action == "Chat":
		var message: String = p.payloads[0]
		_chatbox.add_message("Server", message)
	
func _handle_network_error() -> void:
	OS.alert("There was an error")
