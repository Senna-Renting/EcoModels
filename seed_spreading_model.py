import numpy as np
import pygame

class Plant():
    def __init__(self, x, y, world = None):
        self.x = x
        self.y = y
        self.water_uptake_rate = 10
        self.water_tolerance = (3,30) # outside of this range the plant immediately dies
        self.reproduce_rate = 1
        self.disperse_dist = np.random.normal
        self.dist_params = [0,5,2]
        self.world = world
    def __str__(self):
        return f"Plant ({self.x},{self.y})"
    def position(self):
        return np.array([self.x, self.y])
    def reproduce(self):
        pos = self.disperse_dist(*self.dist_params)
        plant = Plant(self.x + pos[0], self.y + pos[1], self.world)
        self.world.add_species(plant)

    def uptake_rate(self):
        return self.water_uptake_rate
    
    def take(self,source):
        dist = np.sqrt(np.sum((self.position() - source.position())**2))
        uptake = min(self.uptake_rate(), source.uptake_factor(dist)*source.get_amount())
        source.empty(uptake)
        #print(f"uptake ({self.x},{self.y}): {uptake}")
        return uptake
    
    def step(self):
        uptake = np.sum([self.take(source) for source in self.world.get_sources()])
        # check for death
        if uptake < self.water_tolerance[0] or uptake > self.water_tolerance[1]:
            self.world.species.remove(self)
        else:
            # reproduce
            self.reproduce()
    
    def set_world(self, world):
        self.world = world
        
        

class Source():
    def __init__(self, s_type, x, y, amount, world = None):
        self.type = s_type
        self.x = x
        self.y = y
        self.refill_rate = 50
        self.amount = amount
        self.max_amount = amount
        self.world = world
    def __str__(self):
        return f"Source ({self.x},{self.y},{self.amount})"
    def step(self):
        self.amount = min(self.max_amount, self.amount+self.refill_rate)
    def empty(self,amount):
        self.amount -= amount
    def uptake_factor(self,dist):
        return np.exp(-dist)
    def position(self):
        return np.array([self.x,self.y])
    def set_world(self, world):
        self.world = world
    def get_amount(self):
        return self.amount

class World():
    def __init__(self, species = list(), sources = list()):
        self.species = species
        self.sources = sources
        # Couple the world to the agents (plants, sources)
        for spec in self.species:
            spec.set_world(self)
        for source in self.sources:
            source.set_world(self)
    
    def __str__(self):
        spec_title = "Species alive \n ----------- \n"
        species_info = "\n".join([str(spec) for spec in self.species])
        source_title = "\n\n Sources present \n ----------- \n"
        sources_info = "\n".join([str(source) for source in self.sources])
        return spec_title + species_info + source_title + sources_info


    def add_species(self, species):
        self.species.append(species)
    def get_sources(self):
        return self.sources
    def get_species(self):
        return self.species 
    def step(self):
        [source.step() for source in self.sources]
        [spec.step() for spec in self.species]



def simulation():
    species = [Plant(1,5), Plant(3,4), Plant(5,1), Plant(2,2)]
    sources = [Source("water", 2, 2, 20)]
    w = World(species=species, sources=sources)
    for i in range(5):
        w.step()
        print(f"\n Simulation step {i+1}: ")
        print(w)


if __name__ == "__main__":
    #simulation()
    # model setup
    species = [Plant(1,5), Plant(3,4), Plant(5,1), Plant(2,2)]
    sources = [Source("water", 4, 4, 500), Source("water", -8, -8, 500)]
    w = World(species=species, sources=sources)

    # pygame setup
    pygame.init()
    WIDTH = 500
    HEIGHT = 400
    SCALE = 10
    x_origin = WIDTH/2
    y_origin = HEIGHT/2
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    start_ticks=pygame.time.get_ticks()
    running = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")

        for spec in w.get_species():
            pos = spec.position()
            x = x_origin+pos[0]*SCALE
            y = y_origin+pos[1]*SCALE
            pygame.draw.circle(screen, (0,255,0), (x,y), 0.5*SCALE)
        for source in w.get_sources():
            pos = source.position()
            x = x_origin+pos[0]*SCALE
            y = y_origin+pos[1]*SCALE
            pygame.draw.circle(screen, (0,0,255), (x,y), 0.5*SCALE)
        #[pygame.draw.circle(screen, (0,1,0), x_origin+spec.position()[0]*SCALE) for spec in w.get_species()]
        if (pygame.time.get_ticks()-start_ticks)%60 == 0:
            w.step()
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()
