import pygame
import random
import math

pygame.init()

# Predefined parameters
weight_c = 1.0  # Weight factor of coherence
weight_s = 1.5  # Weight factor of separation
weight_a = 1.0  # Weight factor of alignment
proximity = 50  # Proximity radius

# Window screen
window_width, window_height = 640, 480
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Boids")

# Boid shape from PNG
boid_shape = pygame.image.load("boid.png")

# Boid setup
class Boid:
    def __init__(self, window_width, window_height):
        # Boid parameters setup
        self.shape = pygame.transform.scale(boid_shape, (20, 14))
        self.velocity = (random.uniform(-0.75, 0.75), random.uniform(-0.75, 0.75))
        self.window_width = window_width
        self.window_height = window_height
        self.direction = random.uniform(0.0, 2.0 * math.pi)

        # Generate random coordinates for boid spawn
        self.x = random.randrange(40, 600)
        self.y = random.randrange(40, 440)

    # Calculate where boid is in the next updated frame
    def update(self, boids, weight_c, weight_s, weight_a):
        cohesion = self.cohesion(boids, proximity)
        separation = self.separation(boids, proximity)
        alignment = self.alignment(boids, proximity)

        # Adjust velocity using the cohesion, alignment, and separation behaviors
        weight = [weight_c, weight_s, weight_a]
        behaviors = [cohesion, separation, alignment]
        for i in range(len(behaviors)):
            if behaviors[i] is not None:
                self.velocity = (self.velocity[0] + behaviors[i][0] * weight[i],
                                 self.velocity[1] + behaviors[i][1] * weight[i])

        # Limit speed
        max_speed = 1.5
        speed = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        if speed > max_speed:
            # Scale down the boid's velocity and multiply by max speed to ensure the speed is appropriate
            self.velocity = ((self.velocity[0] / speed) * max_speed, (self.velocity[1] / speed) * max_speed)

        # Update boid's position on screen
        self.x = self.x + self.velocity[0]
        self.y = self.y + self.velocity[1]

        # Wrap around the screen x-axis
        if self.x > self.window_width:
            self.x = 0
        elif self.x < 0:
            self.x = self.window_width

        # Wrap around the screen y-axis
        if self.y >= self.window_height:
            self.y = 0
        elif self.y < 0:
            self.y = self.window_height

        # Calculate direction of boid
        self.direction = math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def angle(self, neighbors):
        direction = (self.x - neighbors.x, self.y - neighbors.y)
        dot_product = (self.velocity[0] * direction[0] + self.velocity[1] * direction[1])
        magnitude_x = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        magnitude_y = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
        if magnitude_x * magnitude_y == 0:
            return 180  # Avoid division by zero
        angle = math.degrees(math.acos(dot_product / (magnitude_x * magnitude_y)))
        return angle

    # Draw boid onto screen
    def draw(self, window):
        rotated_image = pygame.transform.rotate(self.shape, -self.direction)
        rectangle = rotated_image.get_rect(center=(self.x, self.y))
        window.blit(rotated_image, rectangle)

    # Cohesion behavior for boid
    def cohesion(self, boids, proximity):
        new_direction = None
        proximity_radius = proximity
        neighboring_boids = 0

        # Calculate if there are other boids in the proximity of the boid
        for neighbors in boids:
            if neighbors != self:
                boid_angle = self.angle(neighbors)
                if boid_angle < 120:
                    distance = ((self.x - neighbors.x) ** 2 + (self.y - neighbors.y) ** 2) ** 0.5
                    if distance < proximity_radius:
                        if new_direction is None:
                            new_direction = (0, 0)
                        new_direction = (new_direction[0] + neighbors.x, new_direction[1] + neighbors.y)
                        neighboring_boids += 1

        # Calculate average position of neighboring boids and return as the new direction value
        if neighboring_boids > 0 and new_direction is not None:
            new_direction = (new_direction[0] / neighboring_boids, new_direction[1] / neighboring_boids)
            return new_direction
        return None

    # Separation behavior for boid
    def separation(self, boids, proximity):
        new_direction = None
        proximity_radius = proximity
        neighboring_boids = 0

        # Calculate if there are other boids in the proximity of the boid
        for neighbors in boids:
            if neighbors != self:
                boid_angle = self.angle(neighbors)
                if boid_angle < 120:
                    distance = ((self.x - neighbors.x) ** 2 + (self.y - neighbors.y) ** 2) ** 0.5
                    if distance < proximity_radius:
                        direction = (self.x - neighbors.x, self.y - neighbors.y)
                        distance = ((direction[0]) ** 2 + (direction[1]) ** 2) ** 0.5
                        if distance > 0:
                            if new_direction is None:
                                new_direction = (0, 0)
                            new_direction = (new_direction[0] + direction[0] / distance,
                                             new_direction[1] + direction[1] / distance)
                            neighboring_boids += 1

        # Calculate average direction away from neighboring boids
        if neighboring_boids > 0 and new_direction is not None:
            new_direction = (new_direction[0] / neighboring_boids, new_direction[1] / neighboring_boids)
            return new_direction
        return None

    # Alignment behavior for boid
    def alignment(self, boids, proximity):
        new_direction = None
        proximity_radius = proximity
        neighboring_boids = 0

        # Calculate if there are other boids in the proximity of the boid
        for neighbors in boids:
            if neighbors != self:
                boid_angle = self.angle(neighbors)
                if boid_angle < 120:
                    distance = ((self.x - neighbors.x) ** 2 + (self.y - neighbors.y) ** 2) ** 0.5
                    if distance < proximity_radius:
                        if new_direction is None:
                            new_direction = (0, 0)
                        new_direction = (new_direction[0] + neighbors.velocity[0],
                                         new_direction[1] + neighbors.velocity[1])
                        neighboring_boids += 1

        # Calculate average velocity of neighboring boids
        if neighboring_boids > 0 and new_direction is not None:
            new_direction = (new_direction[0] / neighboring_boids, new_direction[1] / neighboring_boids)
            return new_direction
        return None

boids = []
# Predefined number of boids
num_boids = 50  # Set the number of boids to 50 by default
for i in range(num_boids):
    boid = Boid(window_width, window_height)
    boids.append(boid)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    window.fill((0, 0, 0))

    # Update and draw each boid
    for boid in boids:
        boid.update(boids, weight_c, weight_s, weight_a)
        boid.draw(window)

    # Update display
    pygame.display.flip()

pygame.quit()
