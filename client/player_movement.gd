extends KinematicBody2D

export (int) var speed = 200

signal velocity_changed(dx, dy)

var old_velocity = null
var velocity = Vector2()
var interpol_target = null

func get_input():
    velocity = Vector2()
    if Input.is_action_pressed("right"):
        velocity.x += 1
    if Input.is_action_pressed("left"):
        velocity.x -= 1
    if Input.is_action_pressed("down"):
        velocity.y += 1
    if Input.is_action_pressed("up"):
        velocity.y -= 1
    velocity = velocity.normalized() * speed

    if velocity != old_velocity:
        emit_signal("velocity_changed", velocity.x, velocity.y)
    
    old_velocity = velocity

func _physics_process(delta):
    get_input()
    velocity = move_and_slide(velocity)

    # The main script may change our interpolation target, meaning
    # the server has sent us our true location and we need to move 
    # toward it to sync up the client with the server.
    if interpol_target:
        velocity = position.direction_to(interpol_target) * speed
        # look_at(target)
        if position.distance_to(interpol_target) > 5:
            velocity = move_and_slide(velocity)
        else:
            interpol_target = null
