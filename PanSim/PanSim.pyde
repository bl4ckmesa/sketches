profiler = {}
import time
import random
import copy
DEBUG=False

def p_run(func, *args):
    if DEBUG:
        start_time = time.time()
        value = func(*args)
        end_time = time.time()
        try:
            profile = profiler[func.func_name]
            new_average = ((profile["average_runtime"] * profile["runcount"]) + ((end_time - start_time)*1000)) / (profile["runcount"] + 1)
            profile["runcount"] += 1
            profile["average_runtime"] = new_average
        except:
            profile = { "runcount" : 1, "average_runtime" : (end_time - start_time) * 1000 }
        profiler[func.func_name] = profile
        return value
    else:
        return func(*args)

class Globals():
    def __init__(self):
        self.people = {}
        self.tick = 0
        self.play = True
        self.day = 0

def draw_buttons():
    stroke(100)
    fill(0)
    rect(0,0,width,50)
    if g.play:
        stroke(255)
        fill(255)
    else:
        stroke(255)
        fill(0)
    triangle(10, 10, 10, 40, 30, 25);
    if g.play:
        stroke(255)
        fill(0)
    else:
        stroke(255)
        fill(255)
    square(40, 10, 30)
    stroke(255)
    fill(0)
    circle(95,25,30)
    # Speed
    rect(120,20,30,10)
    rect(130,10,10,30)
    rect(160,20,30,10)
    textSize(24)
    fill(255)
    alive = 0
    dead = 0
    for k, p in g.people.items():
        if p.alive:
            alive += 1
        else:
            dead += 1
    text("Alive/Dead: %s/%s" % (alive, dead), 210, 35, 20)
    text("Grid Size: %d" % int(height / g.grid_multiplier), 500, 35, 20)
    text("Days: %d" % int(g.day), 700, 35, 20)

class Person():
    def __init__(self):
        self.alive = True
        self.health = 100
        self.recoverychance = 5
        self.incubation = False
        self.incubated_days = 0
        self.diseases = []
        self.immunities = []

class Virus():
    def __init__(self):
        self.contagion = 3
        self.mortality = 0.386
        self.incubation = 5
        self.recovery = 5
        self.generation = 1
        self.mutable = 1.0
        self.id = "fauci"

def gen_id(x,y):
    return "%s:%s" % (str(x).zfill(3), str(y).zfill(3))

def generate_people():
    #g.people = {}
    for x in range(100):
            for y in range(100):
                if y < g.countH and x < g.countW:
                    try:
                        s = g.people[gen_id(x,y)]
                    except:
                        s = Person()
                        s.recoverychance = random.randint(1,25)
                    s.x = x * g.grid_size
                    s.y = y * g.grid_size
                    s.x2 = s.x + g.grid_size
                    s.y2 = s.y + g.grid_size
                    s.idx = x
                    s.idy = y
                    g.people[gen_id(x,y)] = s
                else:
                    try:
                        del g.people[gen_id(x,y)]
                    except:
                        pass

def draw_people():
    for k, s in g.people.items():
        if s.alive:
            stroke((255 / 20 * s.recoverychance),(255 / 20 * s.recoverychance),255)
            fill(255, (255/100 * s.health), (255/100 * s.health))
        else:
            stroke(10)
            fill(0)
        rect(s.x, s.y, g.grid_size, g.grid_size)
        if len(s.diseases) > 0:
            for disease in s.diseases:
                textSize(g.grid_size/2)
                stroke(0)
                fill(0)
                text(str(disease.generation), s.x, s.y, 50, 50)

def neighbors_alive(sqr):
    # Check all your neighbors to see how many are on, return number
    sqr_id_x = sqr.idx
    sqr_id_y = sqr.idy
    neighbors = []
    neighbor_keys = [ 
        gen_id(sqr_id_x-1,sqr_id_y-1), gen_id(sqr_id_x,sqr_id_y-1), gen_id(sqr_id_x+1,sqr_id_y-1),
        gen_id(sqr_id_x-1,sqr_id_y),                                gen_id(sqr_id_x+1,sqr_id_y),
        gen_id(sqr_id_x-1,sqr_id_y+1), gen_id(sqr_id_x,sqr_id_y+1), gen_id(sqr_id_x+1,sqr_id_y+1)
        ]
    for k in neighbor_keys:
        try:
            s = g.people[k]
            if s.alive:
                id_x = s.idx
                id_y = s.idy
                if id_x in [sqr_id_x - 1, sqr_id_x, sqr_id_x + 1] and id_y in [sqr_id_y - 1, sqr_id_y, sqr_id_y + 1]:
                    neighbors.append(s)
        except:
            pass   
    return neighbors

def mutate(disease):
    disease.generation += 1
    # pick a mutation
    mutation = random.choice(["incubation","mortality","recovery","mutable"])
    print(mutation)
    if mutation == "incubation":
        disease.incubation += random.choice([-5,-4,-3,-2,-1,0,1,2,3,4,5])
        if disease.incubation <= 1:
            disease.incubation = 1
    elif mutation == "mortality":
        if [-1,1][random.randrange(2)] > 0:
            disease.mortality *= 0.66
        else:
            disease.mortality *= 1.5
    elif mutation == "recovery":
        disease.recovery += random.randint(-5,5)
        if disease.recovery <= 1:
            disease.recovery = 1
    elif mutation == "mutable":
        disease.mutable *= 2.0
    return disease


def infect(person,disease):
    if disease.id not in person.immunities and disease.id not in person.diseases:
        infected = random.randint(1, int(100 / disease.contagion))
        if infected == 1:
            
            mutated = True
            if random.randint(1,(100/disease.mutable)) == 1:
                newDisease = mutate(copy.deepcopy(disease))
                person.diseases.append(newDisease)
            else:
                person.diseases.append(disease)
            person.incubation = True
            person.incubated_days = 0

def recover(person,disease):
    chance = random.randint(1, int(100 / person.recoverychance))
    if chance == 1:
        return True
    else:
        return False
        
def iterateGame():
    # Rules
    #  If person is contaminated, examine its virus.  Try to infect neighbors based on
    #  - each virus it has
    #  - level of contagion
    g.day += 1
    for k, s in g.people.items():
        if s.alive and len(s.diseases) > 0:
            for disease in s.diseases:
                # Check for infecting new people
                for neighbor in neighbors_alive(s):
                    infect(neighbor,disease)                    
                if not s.incubation:
                    s.health -= disease.mortality
                else:
                    s.incubated_days += 1
                    if s.incubated_days >= disease.incubation:
                        s.incubation = False
                        s.incubated_days = 0
                if s.health <= 0:
                    s.alive = False
                else:
                    if recover(s,disease):
                        s.diseases.pop(s.diseases.index(disease))
                        s.immunities.append(disease.id)
                        s.incubated_days = 0 
                
def mouseClicked():
    speed_list = [ 1, 2, 4, 6, 8, 10, 15, 20, 30, 45, 60 ]
    if 10 <= mouseX <= 30 and 10 <= mouseY <= 40:
        print("Running Simulation.")
        g.play = True
    elif 40 <= mouseX <= 70 and 10 <= mouseY <= 40:
        print("Stopping Simulation.")
        g.play = False
    elif 90 <= mouseX <= 110 and 10 <= mouseY <= 40:
        print("Clearing Simulation.")
        g.play = False
        for k, s in g.people.items():
            g.people[k].alive = False
    elif 120 <= mouseX <= 150 and 10 <= mouseY <= 40:
        idx = speed_list.index(g.iterspersec)
        if idx < len(speed_list)-1:
            g.iterspersec = speed_list[idx + 1]
    elif 160 <= mouseX <= 185 and 10 <= mouseY <= 40:
        idx = speed_list.index(g.iterspersec)
        if idx > 0:
            g.iterspersec = speed_list[idx - 1]

def mouseWheel(event):
    if event.getCount() > 0:
        if g.grid_multiplier < 1000:
            g.grid_multiplier += 3
            p_run(reset_grid)
    else:
        if g.grid_multiplier > 2:
            g.grid_multiplier -= 3
            p_run(reset_grid)

def reset_grid():
    g.grid_size = height / g.grid_multiplier
    #g.grid_size = 10
    g.countH = int(height/g.grid_size)
    g.countW = int(width/g.grid_size)
    p_run(generate_people)
    
def setup():
    size(1000,800)
    frameRate(60)
    #fullScreen()
    global g
    g = Globals()
    g.grid_multiplier = 25
    p_run(reset_grid)
    g.iterspersec = 10

def draw():
    g.tick += 1
    background(0)
    p_run(draw_people)
    p_run(draw_buttons)
    if g.tick % int(60/g.iterspersec) == 0 and g.play == True:
        p_run(iterateGame)
    if DEBUG:
        if g.tick % 10 == 0:
            for k, v in profiler.items():
                print("%s: %s" % (k, v))
    if mousePressed:
        for k, s in g.people.items():
            if s.x <= mouseX <= s.x2 and s.y <= mouseY <= s.y2:
                if mouseButton == LEFT:
                    disease = Virus()
                    s.diseases.append(disease)
                elif mouseButton == RIGHT:
                    s.alive = False
                break
    if keyPressed:
        if key == "-":
            if g.grid_multiplier < 1000:
                g.grid_multiplier += 1
                p_run(reset_grid)
        if key == "+":
            if g.grid_multiplier > 2:
                g.grid_multiplier -= 1
                p_run(reset_grid)
