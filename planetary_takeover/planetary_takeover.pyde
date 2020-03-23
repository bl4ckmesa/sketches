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
        self.range = 0

class Ship():
    def __init__(self):
        self.hp = 5
        self.destination = None
        self.source = None
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
        self.clockwise = True
        self.orientation = 0

class GlobalVars():
    def __init__(self):
        self.bounds = (1000, 800)
        self.framerate = 30
        self.planets = []
        self.ships = []
        self.stars = []
        self.grid_size = 10
        self.deleted_grid = {}
        self.ship_grid = {}
        self.step = 0
        self.total_ship_count = { "p1": 0, "p2": 0, "mob": 0 }
        self.total_planet_count = { "p1": 0, "p2": 0, "mob": 0 }
        self.population_limit = { "p1": 0, "p2": 0, "mob": 0 }
        self.current_population = { "p1": 0, "p2": 0, "mob": 0 }
        self.current_planets = { "p1": 0, "p2": 0, "mob": 0 }
        self.ai_speed = 100
        self.p2 = "computer"
        self.gameover = False
        self.explosion = []
        self.state = "menu"
        self.menu_button_names = [ "Play", "Settings", "Quit" ]
        self.menu_buttons = []
        self.show_settings = False

class Button():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.msg = "Button"
        self.hover = False
        self.clicked = False
        self.height = 80
        self.width = 300
        self.font_size = 50

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
    for i in range(0, 100):
        x = random.randint(1 + planet.size, bounds[0] - planet.size)
        y = random.randint(1 + planet.size, bounds[1] - planet.size)
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
        if ship.clockwise: 
            ship.degree += ship.orbital_speed
            ship.orientation = ship.degree + PI/2
        else:
            ship.degree -= ship.orbital_speed
            ship.orientation = ship.degree - PI/2
        if ship.degree == 360 or ship.degree == -360:
            ship.degree = 0
        orbit_distance = ship.altitude + (random.randint(-5, 5) / 100)
        x_offset = cos(ship.degree) * orbit_distance
        y_offset = sin(ship.degree) * orbit_distance
        ship.x = planet.x + x_offset
        ship.y = planet.y + y_offset
        ship.grid = grid_index((ship.x, ship.y), g.bounds, g.grid_size)
        g.ship_grid[id(ship)] = ship
    return ship

def build_planets(n, bounds):
    planets = []
    planet_scale = [30, 45, 60, 80, 100]
    p1 = Planet()
    p1.color = (200, 50, 50)
    p1.hp = 200
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
    p2.hp = 200
    p2.ship_max = 8
    p2.number = 2
    p2.owner = "p2"
    planets.append(p2)

    for p in range(3, n + 3):
        planet = Planet()
        planet.number = p
        planet.size = random.choice(planet_scale)
        planet.owner = "mob"
        planet.hp = planet.size
        planet.ship_rate = planet.size / 10000
        planet.ship_max = int(planet.size / 10)
        planet.x, planet.y = find_empty_spot(planet, planets, bounds)
        if (planet.x, planet.y) != (0, 0):
            planets.append(planet)
            
    for p in planets:
        p.range = p.size * 10
    return planets

def build_ships(planets):
    # Rate of ship generation, plus total ships, is dependent on the size of
    # the planet.
    for planet in planets:
        if len(planet.ships) < planet.ship_max:
            r = float(random.randint(0, 99)) / 100
            if planet.ship_rate >= r and g.current_population[planet.owner] < g.population_limit[planet.owner]:
                newShip = Ship()
                newShip.color = planet.color
                newShip.owner = planet.owner
                newShip.altitude = planet.size * 0.7
                newShip.grid = grid_index((newShip.x, newShip.y), g.bounds, g.grid_size)
                newShip.clockwise = bool(random.getrandbits(1)) # Faster than random.choice([True, False])
                newShip.orbital_speed = newShip.orbital_speed * (random.randint(90,110)/100.0)
                g.ship_grid[id(newShip)] = newShip
                # Here I need to append to the global planets variable
                planets[planet.number - 1].ships.append(newShip)

def draw_planets(planets):
    # Rebuild population from scratch every time
    g.population_limit = { "p1": 0, "p2": 0, "mob": 0 }
    for planet in planets:
        stroke(0)
        strokeWeight(1)
        filler(planet.color)
        ellipse(planet.x, planet.y, planet.size, planet.size)
        # textSize(32)
        # fill(0)
        #text(planet.number, planet.x, planet.y)
        if planet.selected:
            fill(255, 255, 255, 30)
            ellipse(planet.x, planet.y, planet.range, planet.range)
        
        g.population_limit[planet.owner] += planet.ship_max
        # Also make an HP bar if it's under attack
        if planet.hp < planet.size:
            ship_colors = {}
            for ship in planet.ships:
                try:
                    ship_colors[ship.color] += 1
                except:
                    ship_colors[ship.color] = 1
            clr = sorted(ship_colors, key=(lambda key:ship_colors[key]), reverse=True)
            if len(clr) > 0:
                filler(clr[0])
            else:
                filler(0)
            rect(planet.x + (planet.size * 0.9), planet.y - (planet.size / 2), 10, planet.size)
            filler(planet.color)
            rect(planet.x + (planet.size * 0.9), planet.y - (planet.size / 2), 10, (planet.hp / 100.0 * planet.size))

def draw_ships(planets):
    for planet in planets:
        for ship in planet.ships:
            ship = orbit_coord(ship, planet)
            draw_ship(ship)

def send_ships(s, new):
    ships_tostay = []
    for ship in s.ships:
        if ship.owner == s.owner:
            ship.destination = new.number
            ship.source = s.number
            # Calculate their orientation to the new planet
            newDegree = atan2((new.y - ship.y), (new.x - ship.x)) + PI
            ship.degree = newDegree
            ship.orientation = newDegree + PI
            g.ships.append(ship)
        else:
            ships_tostay.append(ship)
    s.ships = ships_tostay

# This is a magical function:
# https://processing.org/reference/mouseClicked_.html
def mousePressed():
    global g
    if not g.gameover and g.state == "game":
        selected = None
        newSelected = None
        for planet in g.planets:
            if planet.selected:
                selected = planet.number
    
        # Update planet selections
        for planet in g.planets:
            if planet.owner == "p1" or selected is not None:
                distance = sqrt((planet.x - mouseX) ** 2 + (planet.y - mouseY) ** 2)
                if distance < 50:
                    g.planets[planet.number - 1].selected = True
                    newSelected = planet.number
                else:
                    g.planets[planet.number - 1].selected = False
    
        if selected != None and newSelected != None:
            s = g.planets[selected - 1]
            new = g.planets[newSelected - 1]
            planet_distance = sqrt((s.x - new.x) ** 2 + (s.y - new.y) ** 2)
            planet_range = s.range / 2 + new.size/2 
            #print planet_distance, "/", planet_range
            if planet_distance < planet_range:
                send_ships(s, new)
                for planet in g.planets:
                    g.planets[planet.number - 1].selected = False
            else:
                s.selected = False
                new.selected = False
    elif g.state == "menu":
        for button in g.menu_buttons:
            if mouseX >= button.x and mouseX <= (button.x + button.width) and mouseY >= button.y and mouseY <= (button.y + button.height):
                if button.msg == "Play":
                    g.state = "game"
                    g.step = 0
                    startgame(g)
                elif button.msg == "Quit":
                    exit()
                elif button.msg == "Settings":
                    g.show_settings = True
                    
    elif g.gameover and g.state == "game":
        g = GlobalVars()
        setup_menu(g)

def draw_ship(ship):
    filler(ship.color)
    stroker(0)
    #ellipse(ship.x, ship.y, 5, 5)
    #line_length = 5
    #line_x = ship.x + (cos(ship.orientation) * line_length)
    #line_y = ship.y + (sin(ship.orientation) * line_length)
    #line(ship.x, ship.y, line_x, line_y)
    x1 = ship.x + (cos(ship.orientation) * 14)
    y1 = ship.y + (sin(ship.orientation) * 14)
    x2 = ship.x - (cos(ship.orientation+PI/2) * 4)
    y2 = ship.y - (sin(ship.orientation+PI/2) * 4)
    x3 = ship.x - (cos(ship.orientation-PI/2) * 4)
    y3 = ship.y - (sin(ship.orientation-PI/2) * 4)
    triangle(x1, y1, x2, y2, x3, y3)

def p2_ai(g):
    if g.step % g.ai_speed == 0:
        #print "Thinking..."
        p2_planets = []
        for planet in g.planets:
            if planet.owner == "p2":
                p2_planets.append(planet)
        planets_to_attack = []
        for p in p2_planets:
            #print "Thinking about", p.number
            for planet in g.planets:
                distance = sqrt((p.x - planet.x) ** 2 + (p.y - planet.y) ** 2)
                planet_range = p.range / 2 + planet.size/2
                if distance < planet_range:
                    #print "Planet %d is in range. (Distance: %d/%d)" % (planet.number, distance, p.range)
                    if planet.owner != p.owner:
                        #print "Planet %d is an enemy (%s)" % (planet.number, planet.owner)
                        if len(planet.ships) < len(p.ships):
                            #print "Planet %d is weak.  Attacking!" % planet.number
                            planets_to_attack.append([p,planet])
        if len(planets_to_attack) > 0:
            #print "%d planets available." % len(planets_to_attack)
            source, target = random.choice(planets_to_attack)
            #print "Sending ships from %d to %d" % (p.number, target.number)
            send_ships(source, target)
        else:
            pass
            #print "No planets in range/enough ships/enemy"
                
            
def draw_ships_inflight(ships):
    for ship in ships:
        if ship.destination is not None:
            pdest = g.planets[ship.destination - 1]
            psource = g.planets[ship.source - 1]
            dest_alt = pdest.size * 0.7
            distance = sqrt((ship.x - pdest.x) ** 2 + (ship.y - pdest.y) ** 2)
            distance_source = sqrt((ship.x - psource.x) ** 2 + (ship.y - psource.y) ** 2)
            if distance >= distance_source:
                travel_speed = distance_source / 30.0
            else:
                travel_speed = distance / 30.0
            if travel_speed < 2.0:
                travel_speed = 2.0
            if distance <= dest_alt:
                ships.remove(ship)
                ship.destination = None
                ship.altitude = pdest.size * 0.7
                pdest.ships.append(ship)
            else:
                ship.x = ship.x + (travel_speed / distance) * (pdest.x - ship.x)
                ship.y = ship.y + (travel_speed / distance) * (pdest.y - ship.y)
                ship.grid = grid_index((ship.x, ship.y), g.bounds, g.grid_size)
                g.ship_grid[id(ship)] = ship
                filler(ship.color)
                draw_ship(ship)

def laser_ship(ship):
    if g.step % 5 == 0:
        try:
            #ship_grid_idx = g.ship_grid[id(ship)].grid
            ships_in_grid = []
            for shipid, shipobj in g.ship_grid.iteritems():
                if shipobj.grid == ship.grid:
                    if shipid != id(ship):
                        if shipobj.owner != ship.owner:
                            ships_in_grid.append(str(shipid))
            if len(ships_in_grid) > 1:
                # Largest possible distance is the diagonal of one grid
                max_dist = int(sqrt((g.bounds[0] ** 2) + (g.bounds[1] ** 2)) / g.grid_size)
                closest = {"id": None, "dist": max_dist}
                for shipid in ships_in_grid:
                    # Get closest ship
                    next_enemy_ship = g.ship_grid[int(shipid)]
                    distance = sqrt((ship.x - next_enemy_ship.x) ** 2 + (ship.y - next_enemy_ship.y) ** 2)
                    if distance < closest['dist']:
                        closest['id'] = id(next_enemy_ship)
                        closest['dist'] = distance
                if closest['id'] is not None:                    
                    enemy = g.ship_grid[int(closest['id'])]
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

def calculate_damage(ships):
    # Get ships in flight as well as ships around planets
    for ship in ships:
        laser_ship(ship)
    for planet in g.planets:
        for ship in planet.ships:
            laser_ship(ship)

def remove_dead_ships(ships):
    for planet in g.planets:
        ship_list = []
        for ship in planet.ships:
            if ship.hp > 0:
                ship_list.append(ship)
            else:
                try:
                    del g.ship_grid[id(ship)]
                    g.deleted_grid[id(ship)] = ship
                    g.explosion.append([ship.x,ship.y,0])
                except:
                    print "Couldn't delete", id(ship)
        g.planets[planet.number - 1].ships = ship_list
    flight_list = []
    for ship in ships:
        if ship.hp > 0:
            flight_list.append(ship)
        else:
            del g.ship_grid[id(ship)]
            g.deleted_grid[id(ship)] = ship
    return flight_list

def grid_index(coord, bounds, grid_size):
    idx_x = str(int(coord[0] / bounds[0] * 100 / grid_size))
    idx_y = str(int(coord[1] / bounds[1] * 100 / grid_size))
    return idx_x + idx_y

def calculate_takeover(planets):
    for planet in planets:
        if len(planet.ships) > 1:
            shipowners = {"p1": 0, "p2": 0, "mob": 0}
            shipcolors = {}
            for ship in planet.ships:
                # print ship.owner
                shipowners[ship.owner] += 1
                shipcolors[ship.owner] = ship.color
            highest = max(shipowners, key=shipowners.get)
            if highest != planet.owner:
                planet.hp -= 1
            elif planet.hp < planet.size:
                planet.hp += 1
            if planet.hp < 0:
                planets[planet.number - 1].owner = highest
                planets[planet.number - 1].hp = planet.size
                planets[planet.number - 1].color = shipcolors[highest]

def draw_fog():
    grid_symbols = [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" ] 
    grid_size = len(grid_symbols) - 1
    x_chunk = g.bounds[0] / grid_size
    y_chunk = g.bounds[1] / grid_size
    lit_grid = []
    def _get_surrounding_grids(ship):
        grids_to_light = []
        gx = grid_symbols[int(ship.x / x_chunk)]
        gy = grid_symbols[int(ship.y / y_chunk)]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk) - 1]
        gy = grid_symbols[int(ship.y / y_chunk)]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk) - 1]
        gy = grid_symbols[int(ship.y / y_chunk) - 1]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk)]
        gy = grid_symbols[int(ship.y / y_chunk) - 1]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk) + 1]
        gy = grid_symbols[int(ship.y / y_chunk)]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk) + 1]
        gy = grid_symbols[int(ship.y / y_chunk) + 1]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk)]
        gy = grid_symbols[int(ship.y / y_chunk) + 1]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk) + 1]
        gy = grid_symbols[int(ship.y / y_chunk) - 1]
        grids_to_light.append(gx+gy)
        gx = grid_symbols[int(ship.x / x_chunk) - 1]
        gy = grid_symbols[int(ship.y / y_chunk) + 1]
        grids_to_light.append(gx+gy)
        return grids_to_light
        
    for planet in g.planets:
        for ship in planet.ships:
            grids_to_light = _get_surrounding_grids(ship)
            for gr in grids_to_light:
                if gr not in lit_grid:
                    lit_grid.append(gr)
    # Draw black grid
    filler(0)
    for x in range(0, grid_size):
        for y in range(0, grid_size):
            blackgrid = grid_symbols[x] + grid_symbols[y]
            if blackgrid not in lit_grid:
                rect(x * x_chunk, y * y_chunk, x_chunk, y_chunk) 


def count_ships_planets(g):
    g.current_planets = { "p1": 0, "p2": 0, "mob": 0 }
    g.current_population = { "p1": 0, "p2": 0, "mob": 0 }
    for planet in g.planets:
        g.current_planets[planet.owner] += 1
        for ship in planet.ships:
            g.current_population[ship.owner] += 1
    for ship in g.ships:
        g.current_population[ship.owner] += 1

def calculate_stats(g):
    g.total_ship_count = { "p1": 0, "p2": 0, "mob": 0 }
    g.total_planet_count = { "p1": 0, "p2": 0, "mob": 0 }
    for planet in g.planets:
        g.total_planet_count[planet.owner] += 1
        for ship in planet.ships:
            g.total_ship_count[ship.owner] += 1
    for ship in g.ships:
        g.total_ship_count[ship.owner] += 1

def draw_debug(g):
    t = []
    t.append("Bounds: %s" % str(g.bounds))
    t.append("Step: %s" % str(g.step))
    t.append("Population Limits: %s" % str(g.population_limit))
    t.append("Ships: %s" % str(g.current_population))
    t.append("Planets: %s" % str(g.current_planets))
    
    # Draw the text
    textSize(12)
    fill(255, 255, 255, 100)
    x = 10
    y = 20
    for l in t:
        text(l, x, y)
        y += 15
    draw_grid(g.grid_size, g.bounds[0], g.bounds[1]) 
            
def draw_explosions(g):
    leftover_explosions = []
    for e in g.explosion:
        frames = 12
        x = e[0]
        y = e[1]
        r = float(e[2])
        opacity = 255 - int(r/frames*255.0)
        fill(random.randint(0,254), random.randint(0,254), random.randint(0,254), opacity )
        noStroke()
        rect(x-(r/2), y-(r/2), r*(random.random() + 1), r*(random.random() + 1))
        stroke(0)
        #rotate(0)
        r += 1
        if r < frames:
            leftover_explosions.append([x, y, r])
    g.explosion = leftover_explosions

def draw_grid(grid_size, boundx, boundy):
    stroker(255)
    stepx = int(boundx / grid_size)
    stepy = int(boundy / grid_size)
    for num in xrange(0,grid_size):
        # Vertical lines at each horizontal step
        x1 = num * stepx
        y1 = 0
        x2 = x1
        y2 = boundy
        line(x1, y1, x2, y2)
        # Horizontal lines at each vertical step
        x1 = 0
        y1 = num * stepy
        x2 = boundx
        y2 = y1
        line(x1, y1, x2, y2)
        

def endgame(g):
    if g.current_planets['p1'] == 0 or g.current_planets['p2'] == 0:
        textSize(g.bounds[0] / 6)
        if g.current_planets['p1'] == 0:
            msg = "YOU LOSE"
        else:
            msg = "YOU WIN!"
        g.gameover = True
        text(msg, g.bounds[0] / 6, g.bounds[1] / 3)

def draw_button(btn):
    stroke(255)
    strokeWeight(10)
    if btn.hover:
        fill(255, 255, 255, 150)
        rect(btn.x, btn.y, btn.width, btn.height)
        fill(0)
        textSize(btn.font_size)
        text(btn.msg, btn.x + (btn.width / 6), btn.y + (btn.height / 1.4) )
    else:
        fill(0, 0, 0, 0)
        rect(btn.x, btn.y, btn.width, btn.height)
        fill(255)
        textSize(btn.font_size)
        text(btn.msg, btn.x + (btn.width / 6), btn.y + (btn.height / 1.4) )

def update_menu(g):
    for button in g.menu_buttons:
        if mouseX >= button.x and mouseX <= (button.x + button.width) and mouseY >= button.y and mouseY <= (button.y + button.height):
            button.hover = True
        else:
            button.hover = False

def draw_menu(g):
    draw_background(g)
    x = 300
    y = 100
    count = 1
    fill(255, 255, 255, 255)
    textSize(90)
    text("Planetary Takeover", 100, 200)
    update_menu(g)
    for b in g.menu_buttons:
        draw_button(b)
    
def startgame(g):
    g.step = 0
    g.planets = build_planets(12, g.bounds)

def setup_menu(g):
    count = 1
    for b in g.menu_button_names:
        btn = Button()
        btn.msg = b
        btn.x = 300 
        btn.y = 100 + btn.height + (100 * count)
        count += 1
        g.menu_buttons.append(btn)
    
    p = Planet()
    p.color = (200, 50, 50)
    p.hp = 200
    p.x = 800
    p.y = 400
    p.size = 80
    p.ship_max = 8
    p.number = 1
    p.owner = "p1"
    p2 = Planet()
    p2.color = (50, 50, 200)
    p2.hp = 200
    p2.x = 750
    p2.y = 500
    p2.size = 65
    p2.ship_max = 5
    p2.number = 2
    p2.owner = "p2"
    p3 = Planet()
    p3.color = (255)
    p3.hp = 100
    p3.x = 150
    p3.y = 450
    p3.size = 100
    p3.ship_max = 10
    p3.owner = "mob"
    g.planets = [p, p2, p3]

def build_stars(g):
    for x in range(0, random.randint(20,550)):
        x = random.randint(50, (g.bounds[0] - 50))
        y = random.randint(50, (g.bounds[1] - 50))
        g.stars.append({'x': x, 'y': y, 'size': random.randint(1,5), 'id': random.randint(1,100000), 'offset': random.randint(0,100)})
        
def draw_stars(g):
    for star in g.stars:
        fill(255, 255, 255, random.randint(150,250))
        ellipse(star['x'], star['y'], star['size'], star['size'])
        
def draw_background(g):
    background(50)
    draw_stars(g)
    
def setup():
    size(1,1)
    global g
    g = GlobalVars()
    this.surface.setSize(g.bounds[0], g.bounds[1])
    frameRate(g.framerate)
    build_stars(g)
    setup_menu(g)
    
def draw():
    if g.state == "game":
        draw_background(g)
        g.step += 1
   
        calculate_takeover(g.planets)
        build_ships(g.planets)
        g.ships = remove_dead_ships(g.ships)
        calculate_damage(g.ships)
        count_ships_planets(g)

        #draw_fog()
        draw_ships_inflight(g.ships)
        draw_planets(g.planets)
        draw_ships(g.planets)
        draw_explosions(g)
        if g.p2 == "computer":
            p2_ai(g)
        calculate_stats(g)
        draw_debug(g)
        endgame(g)
    elif g.state == "menu":
        draw_menu(g)
        g.step += 1
        draw_planets(g.planets)
        build_ships(g.planets)
        draw_ships(g.planets)
        draw_explosions(g)
        g.ships = remove_dead_ships(g.ships)
        calculate_damage(g.ships)
        
