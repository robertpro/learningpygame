from vector import Vector
import pygame
from statemachine import StateMachine


BLACK = (0, 0, 0)
SCREEN_SIZE = (800, 600)


class Entity(pygame.sprite.Sprite):

    def __init__(self, world, name, image=None, spritesheet=None, flip=False):
        super(Entity, self).__init__()
        self.world = world
        self.name = name
        if not image:
            self.spritesheet = spritesheet
            image = spritesheet.get_image(0)
        self._image = image
        self.rect = image.get_rect()
        self.location = Vector(0, 0)
        self.destination = None
        self.speed = 0.0
        self.passable = True  # you can occupy the same space that this entity
        self.can_leave_screen = True

        self._is_flip = False
        if flip:
            self.flip()

        self.brain = StateMachine()

        self.id = 0
        self._has_collide = None

    def is_flip(self):
        return self._is_flip

    def get_width(self):
        return self._image.get_width()

    def get_height(self):
        return self._image.get_height()

    def set_image(self, image):
        self._image = image
        if self._is_flip:
            self._is_flip = False  # Force flip
            self.flip()

    def flip(self):
        if not self._is_flip:
            self._is_flip = True
            self._image = pygame.transform.flip(self._image, True, False)

    def reverse_flip(self):
        if self._is_flip:
            self._is_flip = False
            self._image = pygame.transform.flip(self._image, True, False)

    def set_location(self, x, y):
        self.location = Vector(x, y)
        self.rect.x = x
        self.rect.y = y

    def render(self, surface):
        x = self.location.x
        y = self.location.y
        surface.blit(self._image, (x, y))

    def process(self, time_passed):
        self.brain.think()
        self.move(time_passed)

    def move(self, time_passed):
        self._has_collide = None
        if self.speed > 0 and self.location != self.destination:
            if not self.can_leave_screen:
                self.keep_inside_screen()
            if not self.passable:
                old_location = self.location

            vec_to_destination = self.destination - self.location
            distance_to_destination = vec_to_destination.get_magnitude()
            vec_to_destination.normalize()
            travel_distance = min(distance_to_destination, time_passed * self.speed)
            vec_to_destination.x *= travel_distance
            vec_to_destination.y *= travel_distance
            self.set_location(self.location.x + vec_to_destination.x,
                              self.location.y + vec_to_destination.y)

            # cancel movement
            if not self.passable and self.is_colliding_with_impassable_entities():
                self._has_collide = self.destination
                # because movement is interrupted can be defined as a float, which may lead to troubles
                self.set_location(int(old_location.x), int(old_location.y))
                self.destination = self.location
            return True
        # Known issue: if there is a collition between impassable entities when they are not moving
        # e.g. during first render, they won't be able to cancel any movement and they will stay blocked

        return False

    def keep_inside_screen(self):
        if self.destination.x < 0:
            self.destination.x = 0
        elif self.destination.x > SCREEN_SIZE[0] - self._image.get_width():
            self.destination.x = SCREEN_SIZE[0] - self._image.get_width()

        if self.destination.y < 0:
            self.destination.y = 0
        elif self.destination.y > SCREEN_SIZE[1] - self._image.get_height():
            self.destination.y = SCREEN_SIZE[1] - self._image.get_height()

    def is_colliding_with_impassable_entities(self):
        entities = self.world.get_impassable_entities(but_me=self)
        collisions = pygame.sprite.spritecollide(self, entities, False)
        return len(collisions) != 0
