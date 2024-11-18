import pygame
import random
import math

pygame.init()

# Predefined parameters
num_boids = 80 # Number of boids on screen
proximity = 50  # Proximity radius
obstacle_radius = 20 # This variable represents how big the obstacle is
max_speed = 2.0  # Maximum speed
smoothing_factor = 0.1  # Factor to smooth transitions in direction and speed

# Adjustable parameters
weight_c = 1.2  # Weight factor of cohesion; moving towards the average position of nearby boids
weight_s = 1.5  # Weight factor of separation; moving away to avoid crowding 
weight_a = 1.3  # Weight factor of alignment; matching velocities with nearby boids
weight_avoid = 15.0  # Weight factor of obstacle avoidance; moving away from obstacles

# Screen setup
window_width, window_height = 1080, 720
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Boids Flocking Simulator")

# Colors
GRAY = (200, 200, 200)
BLUE = (100, 100, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 24)

def draw_slider(screen, label, x, y, value, min_value, max_value, dragging, mouse_pos):
    pygame.draw.rect(screen, GRAY, (x, y, 150, 10))  # Slider background
    
    # Update the slider position calculation to account for the 0-3 range
    slider_pos = int((value - min_value) / (max_value - min_value) * 150)
    knob_rect = pygame.Rect(x + slider_pos - 8, y - 3, 16, 16)
    pygame.draw.circle(screen, BLUE if dragging else GRAY, (x + slider_pos, y + 5), 8)
    text = font.render(f"{label}: {value:.1f}", True, WHITE)
    screen.blit(text, (x, y - 20))
    return knob_rect

class Boid:
    def __init__(self, window_width, window_height):
        self.velocity = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        self.window_width = window_width
        self.window_height = window_height
        self.direction = random.uniform(0.0, 2.0 * math.pi)
        self.x = random.randrange(40, window_width)
        self.y = random.randrange(40, window_height)

    def update(self, boids, obstacles, weight_c, weight_s, weight_a, weight_avoid):
        # Calculates each of these variables for the boids
        cohesion = self.cohesion(boids, proximity)
        separation = self.separation(boids, proximity)
        alignment = self.alignment(boids, proximity)
        avoidance = self.avoid_obstacles(obstacles)

        # Combines all behavioral vectors with their respective weights
        behaviors = [cohesion, separation, alignment, avoidance]
        weights = [weight_c, weight_s, weight_a, weight_avoid]
        for i in range(len(behaviors)):
            # Check if the behavior vector is valid
            if behaviors[i] is not None:
                # Adjust the boid's velocity by adding the weighted influence of the behavior
                self.velocity = (
                    self.velocity[0] + behaviors[i][0] * weights[i] * smoothing_factor,
                    self.velocity[1] + behaviors[i][1] * weights[i] * smoothing_factor,
                )

        # Limit the boid's speed to the maximum allowable speed, otherwise boids speed up too much when flocking together
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > max_speed:
            # Scales the velocity of the boid down to the maximum speed while preserving direction
            self.velocity = (self.velocity[0] / speed * max_speed, self.velocity[1] / speed * max_speed)

        # Velocity componenets
        VelocityX = self.velocity[0]
        VelocityY = self.velocity[1]

        # Adds its velocity to its current coordinates to update positions
        self.x += VelocityX
        self.y += VelocityY

        # Wrap around screen so in case boid goes out of screen, it comes back on other side
        self.x %= self.window_width
        self.y %= self.window_height

        # Updates the direction the boids based on its current velocity
        # The angle is calculated using the arctangent of the velocity components (Vx and Vy)
        self.direction = math.degrees(math.atan2(VelocityY, VelocityX))

    def draw(self, window):
        # Calculate triangle points for the boid
        size = 10
        angle = math.radians(self.direction)

        # The front is the tip of the boid, these are the coordinates for it
        frontX = self.x + size * math.cos(angle)
        frontY = self.y + size * math.sin(angle)
        front = (frontX, frontY)

        # Calculate the coordinates of the left point of the triangle
        leftX = self.x + size * math.cos(angle + 2.5)
        leftY = self.y + size * math.sin(angle + 2.5)
        left = (leftX, leftY)

        # Calculate the coordinates of the right point of the triangle
        
        rightX = self.x + size * math.cos(angle - 2.5)
        rightY = self.y + size * math.sin(angle - 2.5)
        right = (rightX, rightY)

        pygame.draw.polygon(window, WHITE, [front, left, right])

    def avoid_obstacles(self, obstacles):
        # Starts off as none until an obstacle to avoid is found
        direction = None

        # Iterate through all the obstacles they are close to any of the boids
        for obstacle in obstacles:
            # Distance Formula
            distance = math.sqrt((self.x - obstacle[0]) ** 2 + (self.y - obstacle[1]) ** 2)
            
            # Check if the obstacle is within a defined proximity range
            # 15 is a buffer distance, increase to make the boids avoid from further away
            if distance < obstacle_radius + 15:
                # Calculate the vector difference between the boid's position and the obstacle's position
                diff = (self.x - obstacle[0], self.y - obstacle[1])
                # Normalize the vector
                magnitude = math.sqrt(diff[0] ** 2 + diff[1] ** 2)
                # If the magnitude is non-zero (to avoid division by zero), normalize the vector
                if magnitude > 0:
                    # Normalize the vector by dividing the difference by the magnitude, which gives us the unit vector
                    direction = (diff[0] / magnitude, diff[1] / magnitude)
        # Return the normalized direction to avoid the closest obstacle
        return direction

    def cohesion(self, boids, proximity):
        # Cohesion is based off how many boids are nearby
        # Start by initializing total_x, total_y to accumulate the positions of nearby boids, and count to track how many boids are nearby
        total_x, total_y, count = 0, 0, 0
        # Check all the boids in the simulation that aren't itself
        for boid in boids:
            if boid != self:
                # Check if the other boids are close enough
                distance = math.sqrt((self.x - boid.x) ** 2 + (self.y - boid.y) ** 2)
                if distance < proximity:
                    # If they are increase total_x, total_y and count
                    total_x += boid.x # Add the other boids X coordinate
                    total_y += boid.y # Add the other boids Y coordinate
                    count += 1 # +1 boid nearby
        # If count is greater than 0, cohesion occurs
        if count > 0:
            # Calculate the average x and y positions of the nearby boids
            center_x = total_x / count
            center_y = total_y / count
            # Return the direction vector to move the boid toward the center of the nearby boids
            return (center_x - self.x, center_y - self.y)
        # If no boids nearby, no cohesion occurs
        return None

    def separation(self, boids, proximity):
        # Initialize Variables
        diff_x, diff_y, count = 0, 0, 0
        # Check all the boids in the simulation that aren't itself
        for boid in boids:
            if boid != self:
                # Check how many boids are in proximity to the current boid
                distance = math.sqrt((self.x - boid.x) ** 2 + (self.y - boid.y) ** 2)
                if distance < proximity / 2:  # Stronger repulsion within half proximity radius
                    # Accumulate the positional difference to calculate the average repulsion direction
                    diff_x += self.x - boid.x
                    diff_y += self.y - boid.y
                    count += 1
        # If there are boids in the proximity 
        if count > 0:
            # Return average positional difference
            return (diff_x / count, diff_y / count)
        # If no boids in proximity return None
        return None

    def alignment(self, boids, proximity):
        # Initialize Variables
        avg_velocity_x, avg_velocity_y, count = 0, 0, 0
        # Check for boids within proximity that aren't itself
        for boid in boids:
            if boid != self:
                distance = math.sqrt((self.x - boid.x) ** 2 + (self.y - boid.y) ** 2)
                if distance < proximity:
                    # Add average velocity of nearby boids to current boid
                    avg_velocity_x += boid.velocity[0]
                    avg_velocity_y += boid.velocity[1]
                    count += 1
        # If boids are in proximity
        if count > 0:
            # Then return average velocity of the boids in proximity
            return (avg_velocity_x / count, avg_velocity_y / count)
        return None

# Create the boids
boids = [Boid(window_width, window_height) for _ in range(num_boids)]
# Starts with no obstacles
obstacles = []

slider_states = {"dragging": None, "mouse_x": 0}

# Set up sliders
weight_c_slider = pygame.Rect(10, 30, 150, 10)
weight_s_slider = pygame.Rect(10, 70, 150, 10)
weight_a_slider = pygame.Rect(10, 110, 150, 10)

add_obstacles_mode = False
running = True
follow_cursor_mode = False

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Look out for button presses
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # If obstacle mode is on, add obstacles to button press
            if add_obstacles_mode:
                obstacles.append(mouse_pos)

            # Check for slider dragging by looking for button presses
            if slider_states["dragging"] is None:
                if weight_c_slider.collidepoint(mouse_pos):
                    slider_states["dragging"] = "weight_c"
                    slider_states["mouse_x"] = mouse_pos[0]
                elif weight_s_slider.collidepoint(mouse_pos):
                    slider_states["dragging"] = "weight_s"
                elif weight_a_slider.collidepoint(mouse_pos):
                    slider_states["dragging"] = "weight_a"

        # Check for slider dragging
        elif event.type == pygame.MOUSEBUTTONUP:
            slider_states["dragging"] = None

        
        if event.type == pygame.KEYDOWN:
            # Toggle obstacle mode when X is pressed on your keyboard
            if event.key == pygame.K_x:
                obstacles.append(mouse_pos)
            
            # Toggle follow cursor mode when Y is pressed
            if event.key == pygame.K_y:
                follow_cursor_mode = not follow_cursor_mode


    if slider_states["dragging"] == "weight_c":
        weight_c = min(max((mouse_pos[0] - 10) / 150.0 * 3, 0), 3.0)  # scale to 0-3
    elif slider_states["dragging"] == "weight_s":
        weight_s = min(max((mouse_pos[0] - 10) / 150.0 * 3, 0), 3.0)  # scale to 0-3
    elif slider_states["dragging"] == "weight_a":
        weight_a = min(max((mouse_pos[0] - 10) / 150.0 * 3, 0), 3.0)  # scale to 0-3


    window.fill(BLACK)

    # Draw sliders
    draw_slider(window, "Cohesion", 10, 30, weight_c, 0, 3, slider_states["dragging"], mouse_pos)
    draw_slider(window, "Separation", 10, 70, weight_s, 0, 3, slider_states["dragging"], mouse_pos)
    draw_slider(window, "Alignment", 10, 110, weight_a, 0, 3, slider_states["dragging"], mouse_pos)

    # Update boids
    for boid in boids:
        if follow_cursor_mode:
            # Make the boid move toward the cursor with a minimum velocity threshold
            cursor_direction = (
                mouse_pos[0] - boid.x, # Difference in x-coordinates
                mouse_pos[1] - boid.y, # Difference in y-coordinates
            )
            #  Magnitude is the length of the direction vector
            magnitude = math.sqrt(cursor_direction[0] ** 2 + cursor_direction[1] ** 2)

            # Ensure the cursor direction is valid (not zero-length) to avoid division errors
            if magnitude > 1:
                # Add a small random perturbation to the direction to help mimic natural movement
                # This creates slight deviations from a straight line for more realistic behavior
                random_perturbation = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
                normalized_direction = (
                    (cursor_direction[0] + random_perturbation[0]) / magnitude, # Adjusted and normalized x-component
                    (cursor_direction[1] + random_perturbation[1]) / magnitude, # Adjusted and normalized y-component
                )
                # Smoothly blend the cursor-following behavior with the boid's current velocity
                # The smoothing factor controls how quickly the boid's velocity aligns with the target direction
                # max_speed scales the normalized direction to achieve the desired speed
                boid.velocity = (
                    boid.velocity[0] * (1 - smoothing_factor) + normalized_direction[0] * max_speed * smoothing_factor,
                    boid.velocity[1] * (1 - smoothing_factor) + normalized_direction[1] * max_speed * smoothing_factor,
                )
            # Update the boid's position based on its velocity.
            boid.x += boid.velocity[0]
            boid.y += boid.velocity[1]


        boid.update(boids, obstacles, weight_c, weight_s, weight_a, weight_avoid)
        boid.draw(window)


    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.circle(window, RED, obstacle, obstacle_radius)

    # Draw drop obstacle message
    toggle_message = "Press X to Place Obstacle Where Your Cursor is:"
    text_surface = font.render(toggle_message, True, WHITE)
    window.blit(text_surface, (window_width - text_surface.get_width() - 10, window_height - 30))

    # Draw toggle follow mode message
    toggle_message = "Press Y to Make Boids Flock Towards your Cursor: ON" if follow_cursor_mode else "Press Y to Make Boids Flock Towards your Cursor: OFF"
    text_surface = font.render(toggle_message, True, WHITE)
    window.blit(text_surface, (window_width - text_surface.get_width() - 10, window_height - 50))

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()


