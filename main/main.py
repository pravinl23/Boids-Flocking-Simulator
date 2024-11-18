import pygame
import random
import math

pygame.init()

# Predefined parameters
proximity = 50  # Proximity radius
obstacle_radius = 20
max_speed = 2.0  # Maximum speed
smoothing_factor = 0.1  # Factor to smooth transitions in direction and speed

# Adjustable parameters
weight_c = 1.2  # Weight factor of cohesion
weight_s = 1.5  # Weight factor of separation
weight_a = 1.3  # Weight factor of alignment
weight_avoid = 15.0  # Weight factor of obstacle avoidance

# Screen setup
window_width, window_height = 640, 480
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

# Button state
add_obstacles_mode = False

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
        self.x = random.randrange(40, 600)
        self.y = random.randrange(40, 440)

    def update(self, boids, obstacles, weight_c, weight_s, weight_a, weight_avoid):
        cohesion = self.cohesion(boids, proximity)
        separation = self.separation(boids, proximity)
        alignment = self.alignment(boids, proximity)
        avoidance = self.avoid_obstacles(obstacles)

        # Weighted combination of behaviors
        behaviors = [cohesion, separation, alignment, avoidance]
        weights = [weight_c, weight_s, weight_a, weight_avoid]
        for i in range(len(behaviors)):
            if behaviors[i] is not None:
                self.velocity = (
                    self.velocity[0] + behaviors[i][0] * weights[i] * smoothing_factor,
                    self.velocity[1] + behaviors[i][1] * weights[i] * smoothing_factor,
                )

        # Limit speed
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > max_speed:
            self.velocity = (self.velocity[0] / speed * max_speed, self.velocity[1] / speed * max_speed)

        # Update position
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # Wrap around screen
        self.x %= self.window_width
        self.y %= self.window_height

        # Update direction
        self.direction = math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def draw(self, window):
        # Calculate triangle points for the boid
        size = 10
        angle = math.radians(self.direction)
        front = (self.x + size * math.cos(angle), self.y + size * math.sin(angle))
        left = (self.x + size * math.cos(angle + 2.5), self.y + size * math.sin(angle + 2.5))
        right = (self.x + size * math.cos(angle - 2.5), self.y + size * math.sin(angle - 2.5))

        pygame.draw.polygon(window, WHITE, [front, left, right])

    def avoid_obstacles(self, obstacles):
        direction = None
        for obstacle in obstacles:
            distance = math.sqrt((self.x - obstacle[0]) ** 2 + (self.y - obstacle[1]) ** 2)
            if distance < obstacle_radius + 10:
                diff = (self.x - obstacle[0], self.y - obstacle[1])
                magnitude = math.sqrt(diff[0] ** 2 + diff[1] ** 2)
                if magnitude > 0:
                    direction = (diff[0] / magnitude, diff[1] / magnitude)
        return direction

    def cohesion(self, boids, proximity):
        total_x, total_y, count = 0, 0, 0
        for boid in boids:
            if boid != self:
                distance = math.sqrt((self.x - boid.x) ** 2 + (self.y - boid.y) ** 2)
                if distance < proximity:
                    total_x += boid.x
                    total_y += boid.y
                    count += 1
        if count > 0:
            center_x = total_x / count
            center_y = total_y / count
            return (center_x - self.x, center_y - self.y)
        return None

    def separation(self, boids, proximity):
        diff_x, diff_y, count = 0, 0, 0
        for boid in boids:
            if boid != self:
                distance = math.sqrt((self.x - boid.x) ** 2 + (self.y - boid.y) ** 2)
                if distance < proximity / 2:  # Stronger repulsion within half proximity radius
                    diff_x += self.x - boid.x
                    diff_y += self.y - boid.y
                    count += 1
        if count > 0:
            return (diff_x / count, diff_y / count)
        return None

    def alignment(self, boids, proximity):
        avg_velocity_x, avg_velocity_y, count = 0, 0, 0
        for boid in boids:
            if boid != self:
                distance = math.sqrt((self.x - boid.x) ** 2 + (self.y - boid.y) ** 2)
                if distance < proximity:
                    avg_velocity_x += boid.velocity[0]
                    avg_velocity_y += boid.velocity[1]
                    count += 1
        if count > 0:
            return (avg_velocity_x / count, avg_velocity_y / count)
        return None


boids = [Boid(window_width, window_height) for _ in range(50)]
obstacles = []

slider_states = {"dragging": None, "mouse_x": 0}

# Set up sliders
weight_c_slider = pygame.Rect(10, 30, 150, 10)
weight_s_slider = pygame.Rect(10, 70, 150, 10)
weight_a_slider = pygame.Rect(10, 110, 150, 10)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if add_obstacles_mode:
                obstacles.append(mouse_pos)

            # Check for slider dragging
            if slider_states["dragging"] is None:
                if weight_c_slider.collidepoint(mouse_pos):
                    slider_states["dragging"] = "weight_c"
                    slider_states["mouse_x"] = mouse_pos[0]
                elif weight_s_slider.collidepoint(mouse_pos):
                    slider_states["dragging"] = "weight_s"
                elif weight_a_slider.collidepoint(mouse_pos):
                    slider_states["dragging"] = "weight_a"

        elif event.type == pygame.MOUSEBUTTONUP:
            slider_states["dragging"] = None

        # Toggle obstacle mode when X is pressed on your keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                obstacles.append(mouse_pos)

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
        boid.update(boids, obstacles, weight_c, weight_s, weight_a, weight_avoid)
        boid.draw(window)

    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.circle(window, RED, obstacle, obstacle_radius)

    # Draw toggle mode message
    toggle_message = "Press X to Place Obstacle Where Your Cursor is:"
    text_surface = font.render(toggle_message, True, WHITE)
    window.blit(text_surface, (window_width - text_surface.get_width() - 10, window_height - 30))

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()


