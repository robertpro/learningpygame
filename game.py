import pygame
import menu
from random import randint, choice as random_choice
from sara import Sara
from robot import Robot
from spider import Spider
from world import World
from os import remove as os_remove
from PIL import Image, ImageFilter
from settings import settings


# TODO move this to a unique source
SCREEN_SIZE = (800, 600)
LIFE_IMAGE_FILENAME = 'images/heart.png'


class Game:
    SONG_END = pygame.USEREVENT + 1

    def __init__(self, screen):
        self.screen = screen

#        pygame.mixer.pre_init(44100, -16, 2, 1024*4)
        pygame.mixer.music.load("music/intro.wav")
        pygame.mixer.music.set_endevent(Game.SONG_END)
        pygame.mixer.music.play(1)


        self.clock = pygame.time.Clock()

        self.world = World()

        self.sara = Sara(self.world)
        self.sara.set_location(100, SCREEN_SIZE[1] / 2)
        self.world.add_entity(self.sara, ('events', 'player'))

        self.images= dict()
        self.images['life'] = pygame.image.load(LIFE_IMAGE_FILENAME).convert_alpha()

        self.robots_created = 0
        self.create_robot()
        self.create_robot()
        self.create_robot()

        self.main()

    def main(self):
        should_quit = False
        possible_enemies = [None] * 101
        possible_enemies[100] = self.create_robot

        while not should_quit:
            if randint(1, 250) == 1:
                # Create an enemy
                hard = randint(0, 99)
                for enemy_creator in possible_enemies[hard:]:
                    if enemy_creator:
                        enemy_creator()

            # Adding enemies
            if self.robots_created == 5:
                possible_enemies[30] = self.create_spider

            events = pygame.event.get()
            for event in events:
                if event.type == Game.SONG_END and not settings['debug']:
                    pygame.mixer.music.load('music/main.wav')
                    pygame.mixer.music.play(-1)
            self.world.process_events(events)
            seconds_passed = self.clock.tick(60) / 1000.0
            should_quit = self.world.process(seconds_passed)
            self.world.render(self.screen)
            self.render()
            pygame.display.update()

        # Quit game
        self.show_game_over()

        menu.MainMenu(self.screen)

    def render(self):
        '''Use it to render HUD'''
        for i in xrange(0, self.sara.life):
            x = self.images['life'].get_width() * i + 5 * (i + 1)
            self.screen.blit(self.images['life'], (x, 10))

    def show_game_over(self):
        filename = 'gameover.jpg'
        pygame.image.save(self.screen, filename)
        im = Image.open(filename)
        im = im.filter(ImageFilter.BLUR)
        im.save(filename)
        self.screen.blit(pygame.image.load(filename), (0, 0))
        os_remove(filename)
        pygame.display.update()
        pygame.time.delay(500)

    def create_robot(self):
        robot = Robot(self.world)
        robot.set_location(randint(0, SCREEN_SIZE[0]), randint(0, SCREEN_SIZE[1]))
        self.world.add_entity(robot, ('enemies', ))
        self.robots_created += 1

    def create_spider(self):
        spider = Spider(self.world)
        spider.set_location(200, 1)
        self.world.add_entity(spider, ('enemies',))
