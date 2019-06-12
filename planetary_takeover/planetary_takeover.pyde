import random
import types

class Planet():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.number = 0
        self.ships = []
        self.owner = "mob"
        self.hp = 100
        # Choices: "mob", "player1", "player2"
        self.color = 200
        self.ship_rate = 0.05
        self.selected = False
    
class Ship():
    def __init__(self):
        self.hp = 5
        self.destination = None
        self.planet = 0
        self.altitude = 10
        self.degree = 0
        self.x = 0
        self.y = 0
        self.orbital_speed = 0.02
        self.color = 200
        self.owner = "mob"
        self.closest_enemy = None
        self.grid = "00"

def filler(color):
    if isinstance(color, types.IntType):
        fill(color)
    elif isinstance(color, types.TupleType):
        if len(color) == 3:
            fill(color[0], color[1], color[2])
        elif len(color) == 4:
            fill(color[0], color[1], color[2])
    else:
        fill(255)
        
def stroker(color):
    if isinstance(color, types.IntType):
        stroke(color)
    elif isinstance(color, types.TupleType):
        if len(color) == 3:
            stroke(color[0], color[1], color[2])
        elif len(color) == 4:
            stroke(color[0], color[1], color[2])
    else:
        stroke(255)

def find_empty_spot(planet, planets, bounds):
    for i in range(0,100):
        x = random.randint(1+planet.size,bounds[0]-planet.size)
        y = random.randint(1+planet.size,bounds[1]-planet.size)
        good_spot = True
        if len(planets) > 1:
            for p in planets:
                # Make sure planets are at least this far apart
                min_distance = planet.size + p.size
                x_distance = abs(x - p.x)
                y_distance = abs(y - p.y)
                if x_distance < min_distance and y_distance < min_distance:
                    good_spot = False
        if good_spot:
            return x, y
    # This means it failed to find a spot
    return 0, 0

def orbit_coord(ship, planet):
    if ship.destination is None:
        ship.degree += ship.orbital_speed
        if ship.degree == 360:
            ship.degree = 0
        orbit_distance = ship.altitude + (random.randint(-5,5) / 100)
        x_offset = cos(ship.degree) * orbit_distance
        y_offset = sin(ship.degree) * orbit_distance
        ship.x = planet.x + x_offset
        ship.y = planet.y + y_offset
        ship.grid = grid_index((ship.x, ship.y), bounds)
        ship_grid[id(ship)] = ship
    return ship

def build_planets(n, bounds):
    planets = []
    planet_scale = [ 30, 45, 60, 80, 100 ]
    
    p1 = Planet()
    p1.color = (200, 50, 50)
    p1.x = 120
    p1.y = 120
    p1.size = 80
    p1.ship_max = 8
    p1.number = 1
    p1.owner = "p1"
    planets.append(p1)
    
    p2 = Planet()
    p2.color = (50, 50, 200)
    p2.x = bounds[0] - 120
    p2.y = bounds[1] - 120
    p2.size = 80
    p2.ship_max = 8
    p2.number = 2
    p2.ownder = "p2"
    planets.append(p2)
    
    for p in range(3, n+3):
        planet = Planet()
        planet.number = p
        planet.size = random.choice(planet_scale)
        planet.owner = "mob"
        planet.ship_rate = planet.size / 10000
        planet.ship_max = int(planet.size / 10)
        planet.x, planet.y = find_empty_spot(planet, planets, bounds)
        if (planet.x, planet.y) != (0,0):
            planets.append(planet)
    return planets

def build_ships(planets):
    # Rate of ship generation, plus total ships, is dependent on the size of the planet.
    for planet in planets:
        if len(planet.ships) < planet.ship_max:
            r = float(random.randint(0,99))/100
            if planet.ship_rate >= r:
                newShip = Ship()
                newShip.color = planet.color
                newShip.owner = planet.owner
                newShip.altitude = planet.size * 0.7
                newShip.grid = grid_index((newShip.x, newShip.y), bounds)
                ship_grid[id(newShip)] = newShip
                # Here I need to append to the global planets variable
                planets[planet.number - 1].ships.append(newShip)

def draw_planets(planets):
    for planet in planets:
        filler(planet.color)
        ellipse(planet.x, planet.y, planet.size, planet.size)
        #textSize(32)
        #fill(0)
        #text(planet.number, planet.x, planet.y)
        if planet.selected:
            fill(255,255,255,0.1)
            ellipse(planet.x, planet.y, planet.size * 2, planet.size * 2)

def draw_ships(planets):
    for planet in planets:
        for ship in planet.ships:
            ship = orbit_coord(ship, planet)
            filler(ship.color)
            ellipse(ship.x, ship.y, 5, 5)

# This is a magical function: https://processing.org/reference/mouseClicked_.html
def mouseClicked():
    selected = None
    newSelected = None
    for planet in planets:
        if planet.selected:
            selected = planet.number

    # Update planet selections
    for planet in planets:
        distance = sqrt( (planet.x - mouseX)**2 + (planet.y - mouseY)**2 )
        if distance < 50:
            planets[planet.number - 1].selected = True
            newSelected = planet.number
        else:
            planets[planet.number - 1].selected = False
    #for ship in planets[0].ships:
    #    ship.destination = 3
    #    ships.append(ship)
    #planets[0].ships = []
    
    if selected != None and newSelected != None:
        ships_tostay = []
        for ship in planets[selected - 1].ships:
            if ship.owner == "p1":
                ship.destination = newSelected
                ships.append(ship)
            else:
                ships_tostay.append(ship)
        planets[selected - 1].ships = ships_tostay
        for planet in planets:
            planets[planet.number - 1].selected = False

def draw_ships_inflight(ships):
    for ship in ships:
        if ship.destination is not None:
            planet_number = ship.destination - 1
            dest_x = planets[planet_number].x
            dest_y = planets[planet_number].y
            dest_alt = planets[planet_number].size * 0.7
            distance = sqrt( (ship.x - dest_x)**2 + (ship.y - dest_y)**2 )
            travel_speed = 4
            if distance <= dest_alt:
                ships.remove(ship)
                ship.destination = None
                ship.altitude = planets[planet_number].size * 0.7
                planets[planet_number].ships.append(ship)
            else:
                ship.x = ship.x + (travel_speed/distance)*(dest_x - ship.x)
                ship.y = ship.y + (travel_speed/distance)*(dest_y - ship.y)
                ship.grid = grid_index((ship.x, ship.y), bounds)
                ship_grid[id(ship)] = ship
                filler(ship.color)
                ellipse(ship.x, ship.y, 5, 5)
             
def laser_ship(ship):
    try:
        ship_grid_idx = ship_grid[id(ship)].grid
        ships_in_grid = []
        for shipid, shipobj in ship_grid.iteritems():
            if shipobj.grid == ship_grid_idx:
                if shipid != id(ship):
                    ships_in_grid.append(str(shipid))
        if len(ships_in_grid) > 1:
            closest = { "id": None, "dist": 10000 }
            for shipid in ships_in_grid:
                # Get closest ship
                enemy_ship = ship_grid[int(shipid)] 
                distance = sqrt( (ship.x - enemy_ship.x)**2 + (ship.y - enemy_ship.y)**2 )
                if ship_grid[id(enemy_ship)].owner != ship.owner:
                    if distance < closest['dist']:
                        closest['id'] = id(enemy_ship)
                        closest['dist'] = distance
            if closest['id'] is not None:
                if step % 5 == 0:
                    enemy = ship_grid[int(closest['id'])]
                    enemy.hp -= 1
                    stroker(ship.color)
                    line(enemy.x, enemy.y, ship.x, ship.y)
                    stroke(0)
    except Exception as e:
        print "Couldn't find ship.  Maybe it was deleted?"
        try:
            print id(ship)
        except:
            pass
            
def calculate_damage():
    # Get ships in flight as well as ships around planets
    for ship in ships:
        laser_ship(ship)
    for planet in planets:
        for ship in planet.ships:
            laser_ship(ship)

def remove_dead_ships(ships):
    for planet in planets:
        ship_list = []
        for ship in planet.ships:
            if ship.hp > 0:
                ship_list.append(ship)
            else:
                try:
                    del ship_grid[id(ship)]
                    deleted_grid[id(ship)] = ship
                except:
                    print "Couldn't delete", id(ship)
        planets[planet.number - 1].ships = ship_list
    flight_list = []
    for ship in ships:
        if ship.hp > 0:
            flight_list.append(ship)
        else:
            del ship_grid[id(ship)]
            deleted_grid[id(ship)] = ship
    return flight_list
                
def grid_index(coord,bounds):
    idx_x = str(int(coord[0] / bounds[0] * 100 / 10))
    idx_y = str(int(coord[1] / bounds[1] * 100 / 10))
    return idx_x+idx_y
     
def calculate_takeover(planets):
    for planet in planets:
        if len(planet.ships) > 1:
            shipowners = {"p1": 0, "p2": 0, "mob": 0}
            shipcolors = {}
            #shipowners[planet.owner] = 0
            for ship in planet.ships:
                #print ship.owner
                shipowners[ship.owner] += 1
                shipcolors[ship.owner] = ship.color
            highest = max(shipowners, key=shipowners.get)
            if highest != planet.owner:
                print "Highest isn't owner.  Highest: %s, Owner: %s" % (highest, planet.owner)
                planet.hp -= 1
                print "Reducing planet %d hit points to %d" % (planet.number, planet.hp)
            if planet.hp < 0:
                planets[planet.number - 1].owner = highest
                planets[planet.number - 1].hp = 100
                planets[planet.number -1].color = shipcolors[highest]
        
def setup():
    global bounds
    bounds = (800, 600)
    size(bounds[0], bounds[1])
    frameRate(30)
    global planets
    global ships
    ships = []
    global ship_grid
    ship_grid = {}
    global deleted_grid
    deleted_grid = {}
    global step
    step = 0
    planets = build_planets(5, bounds)
    
def draw():
    background(50)
    global step
    global ships
    step += 1
    #ellipse(mouseX, mouseY, 10, 10);
    draw_ships_inflight(ships)
    calculate_takeover(planets)
    draw_planets(planets)
    draw_ships(planets)
    build_ships(planets)
    ships = remove_dead_ships(ships)
    calculate_damage()
