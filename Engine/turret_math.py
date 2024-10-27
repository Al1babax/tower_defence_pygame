import math

# Constants for the bullet and enemy path
# BULLET_SPEED = 2
# ENEMY_SPEED = 2  # Speed at which enemy moves between waypoints
# WAYPOINT_DISTANCE = 1  # Fixed distance between waypoints

# Waypoints for the enemy path (each waypoint is spaced 1 unit apart)
# enemy_waypoints = [(0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (4, 4)]  # Example waypoints


def change_coordinate_system(x, y):
    # In game state using row, column coordinate system, origin at top-left
    # In math using x, y coordinate system, origin at bottom-left
    # row = -y, column = x
    return -y, x


# Function to calculate travel time between each waypoint (constant)
def calculate_time_per_waypoint(speed):
    WAYPOINT_DISTANCE = 1
    return WAYPOINT_DISTANCE / speed


# Step 2: Calculate time for bullet to reach the current enemy position
def calculate_time_to_hit(tx, ty, ex, ey, bullet_speed):
    dist = math.sqrt((tx - ex) ** 2 + (ty - ey) ** 2)
    return dist / bullet_speed


# Step 3: Calculate enemy's exact position and velocity vector at t_impact
def enemy_position_velocity_at_impact(waypoints, time_per_waypoint, t_impact, enemy_speed):
    elapsed_time = 0

    # Iterate through waypoints to find where t_impact lies
    for i in range(len(waypoints) - 1):
        if elapsed_time + time_per_waypoint > t_impact:
            # t_impact falls within this segment
            time_in_segment = t_impact - elapsed_time
            p1 = waypoints[i]
            p2 = waypoints[i + 1]

            # Calculate exact position at t_impact
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            ex_impact = p1[0] + dx * (time_in_segment / time_per_waypoint)
            ey_impact = p1[1] + dy * (time_in_segment / time_per_waypoint)

            # Velocity vector in this segment
            velocity_vector = (dx * enemy_speed, dy * enemy_speed)
            return (ex_impact, ey_impact), velocity_vector

        elapsed_time += time_per_waypoint

    # If t_impact exceeds total path time, return last position
    return waypoints[-1], (0, 0)


# Main function to calculate bullet velocity to hit moving enemy along a path
def calculate_bullet_velocity(tx, ty, ex, ey, bullet_speed, waypoints, enemy_speed):
    # Convert coordinates to math coordinate system
    tx, ty = change_coordinate_system(tx, ty)
    ex, ey = change_coordinate_system(ex, ey)

    # Convert the waypoints to math coordinate system
    waypoints = [change_coordinate_system(x, y) for x, y in waypoints]

    # Calculate fixed time per waypoint
    time_per_waypoint = calculate_time_per_waypoint(enemy_speed)

    # Calculate initial time to hit enemy's starting position
    t_impact = calculate_time_to_hit(tx, ty, ex, ey, bullet_speed)

    # print(f"Time to hit: {t_impact}")

    # Find the exact position and velocity of the enemy at t_impact
    enemy_impact_pos, enemy_velocity = enemy_position_velocity_at_impact(
        waypoints, time_per_waypoint, t_impact, enemy_speed
    )

    # print(f"Enemy impact position: {enemy_impact_pos}")
    # print(f"Enemy velocity vector: {enemy_velocity}")

    # Calculate bullet direction based on tower position and enemy impact position
    dx, dy = enemy_impact_pos[0] - tx, enemy_impact_pos[1] - ty
    dist_to_enemy_impact = math.sqrt(dx ** 2 + dy ** 2)

    direction_vector = (dx / dist_to_enemy_impact, dy / dist_to_enemy_impact)
    bullet_velocity = (direction_vector[0] * bullet_speed, direction_vector[1] * bullet_speed)

    return bullet_velocity


# Run calculation with given parameters
# tower_position = (4, 0)
# enemy_position = enemy_waypoints[0]
#
# bullet_velocity = calculate_bullet_velocity(
#     tower_position[0], tower_position[1],
#     enemy_position[0], enemy_position[1],
#     BULLET_SPEED, enemy_waypoints, ENEMY_SPEED
# )
#
# print("Bullet velocity vector:", bullet_velocity)
