from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time  
import random

MAX_SPEED = 4.0

class Ball:
  def __init__(self, x, y, radius, color, acceleration, velocity, mass):
    self.x = x
    self.y = y
    self.radius = radius
    self.color = color
    self.velocity = velocity
    self.acceleration = acceleration
    self.mass = mass

  def draw(self):
    glColor3f(*self.color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(self.x, self.y)  
    for angle in range(0, 361, 10):
      angle_rad = math.radians(angle)
      glVertex2f(self.x + math.cos(angle_rad) * self.radius, self.y + math.sin(angle_rad) * self.radius)
    glEnd()
  
  def checkEdges(self, new_x, new_y, delta_time):
    left, right, bottom, top = get_screen_edges()
    t_x_min = t_y_min = float('inf')

    if self.velocity[0] != 0:
      if self.velocity[0] > 0:
        t_x_min = (right - self.radius - self.x) / self.velocity[0]
      else:
        t_x_min = (left + self.radius - self.x) / self.velocity[0]

    if self.velocity[1] != 0:
      if self.velocity[1] > 0:
        t_y_min = (top - self.radius - self.y) / self.velocity[1]
      else:
        t_y_min = (bottom + self.radius - self.y) / self.velocity[1]

    t_min = min(t_x_min, t_y_min)

    if t_min < delta_time:
      self.x += self.velocity[0] * t_min
      self.y += self.velocity[1] * t_min
      if t_x_min < t_y_min:
        self.velocity[0] = -self.velocity[0]
        self.acceleration[0] = -self.acceleration[0]
      else:
        self.velocity[1] = -self.velocity[1]
        self.acceleration[1] = -self.acceleration[1]
      self.update(delta_time - t_min)
    else:
      self.x = new_x
      self.y = new_y
  def check_Collision(self, ball):
    distance = math.sqrt((self.x - ball.x)**2 + (self.y - ball.y)**2)
    if distance < self.radius + ball.radius:
      # Calculate unit normal and unit tangent vectors
      normal = [(ball.x - self.x) / distance, (ball.y - self.y) / distance]
      tangent = [-normal[1], normal[0]]
      # Calculate initial velocity in normal and tangent directions
      v1n = self.velocity[0] * normal[0] + self.velocity[1] * normal[1]
      v1t = self.velocity[0] * tangent[0] + self.velocity[1] * tangent[1]
      v2n = ball.velocity[0] * normal[0] + ball.velocity[1] * normal[1]
      v2t = ball.velocity[0] * tangent[0] + ball.velocity[1] * tangent[1]
      # Calculate final velocity in normal and tangent directions
      new_v1n = (v1n * (self.mass - ball.mass) + 2 * ball
      .mass * v2n) / (self.mass + ball.mass)
      new_v2n = (v2n * (ball.mass - self.mass) + 2 * self
      .mass * v1n) / (self.mass + ball.mass)
      # Update velocities
      self.velocity[0] = new_v1n * normal[0] + v1t * tangent[0]
      self.velocity[1] = new_v1n * normal[1] + v1t * tangent[1]
      ball.velocity[0] = new_v2n * normal[0] + v2t * tangent[0]
      ball.velocity[1] = new_v2n * normal[1] + v2t * tangent[1]
      # Move balls so they are no longer colliding
      overlap = self.radius + ball.radius - distance
      self.x -= overlap * normal[0] / 2
      self.y -= overlap * normal[1] / 2
      ball.x += overlap * normal[0] / 2
      ball.y += overlap * normal[1] / 2
      return True

  def update(self, delta_time):

    # velocity = acceleration * time
    self.velocity[0] += self.acceleration[0] * delta_time
    self.velocity[1] += self.acceleration[1] * delta_time
    if abs(self.velocity[0]) > MAX_SPEED:
      self.velocity[0] = MAX_SPEED if self.velocity[0] > 0 else -MAX_SPEED
    if abs(self.velocity[1]) > MAX_SPEED:
      self.velocity[1] = MAX_SPEED if self.velocity[1] > 0 else -MAX_SPEED
    # position = velocity * time
    new_x = self.x + self.velocity[0] * delta_time
    new_y = self.y + self.velocity[1] * delta_time

    self.checkEdges(new_x, new_y, delta_time)


balls = [
  Ball(0.0, 0.0, 0.1, (1.0, 0.0, 0.0), [0.01, -9.8], [0.01, 0.01], 1.0),
  Ball(0.5, 0.5, 0.1, (0.0, 1.0, 0.0), [-0.01, -9.8], [-0.01, -0.01], 1.0)
]
for i in range(10):
  # Randomly generate a ball
  x = random.uniform(-0.9, 0.9)
  y = random.uniform(-0.9, 0.9)
  radius = random.uniform(0.05, 0.1)
  color = (random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))
  acceleration = [random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01)]
  velocity = [random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01)]
  mass = random.uniform(0.5, 2.0)
  balls.append(Ball(x, y, radius, color, acceleration, velocity, mass))

def get_screen_edges():
    left, right = -1.0, 1.0
    bottom, top = -1.0, 1.0
    return left, right, bottom, top

def sweep_and_prune(balls):
  # Sort balls by x
  balls.sort(key=lambda ball: ball.x)
  # Create a list of potentially colliding pairs
  for i in range(len(balls)):
    for j in range(i + 1, len(balls)):
      if balls[j].x - balls[i].x > balls[i].radius + balls[j].radius:
        break
      balls[i].check_Collision(balls[j])
  return True
def display():
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  
  for ball in balls:
    ball.draw()
  
  glFlush()

# Initialize previous time
previous_time = time.time()

def update(value):
  global previous_time
  current_time = time.time()
  delta_time = current_time - previous_time
  previous_time = current_time
  
  sweep_and_prune(balls)
  for ball in balls:
    ball.update(delta_time)  # Pass delta_time to the update method
  
  # Redisplay
  glutPostRedisplay()
  
  # Call update again after 16 milliseconds (approx. 60 frames per second)
  glutTimerFunc(16, update, 0)

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutCreateWindow(b"OpenGL with Python")
glutDisplayFunc(display)
glutTimerFunc(16, update, 0)

# Set up orthographic projection
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
left, right, bottom, top = get_screen_edges()
glOrtho(left, right, bottom, top, -1.0, 1.0)
glMatrixMode(GL_MODELVIEW)

glutMainLoop()
