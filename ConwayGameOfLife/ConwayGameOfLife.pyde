profiler = {}
import time
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

# def p_run(func, *args):
#     return func(*args)

class Globals():
    def __init__(self):
        self.squares = {}
        self.tick = 0
        self.play = False

def draw_buttons():
    stroke(100)
    fill(0)
    rect(0,0,200,50)
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
    text("Iterations per second: %d" % g.iterspersec, 210, 35, 20)

class Square():
    def __init__(self):
        self.on = False

def gen_id(x,y):
    return "%s:%s" % (str(x).zfill(3), str(y).zfill(3))

def generate_squares():
    for x in range(g.countW):
        for y in range(g.countH):
            s = Square()
            s.x = x * g.grid_size
            s.y = y * g.grid_size
            s.x2 = s.x + g.grid_size
            s.y2 = s.y + g.grid_size
            s.idx = x
            s.idy = y
            g.squares[gen_id(x,y)] = s


def draw_squares():
    for k, s in g.squares.items():
        if s.on:
            stroke(0)
            fill(255)
        else:
            stroke(10)
            fill(0)
        rect(s.x, s.y, g.grid_size, g.grid_size) 

def neighbors_on(sqr):
    # Check all your neighbors to see how many are on, return number
    #sqr_id_x = int(sqr.split(":")[0])
    #sqr_id_y = int(sqr.split(":")[1])
    sqr_id_x = sqr.idx
    sqr_id_y = sqr.idy
    neighbors = 0
    
    neighbor_keys = [ 
        gen_id(sqr_id_x-1,sqr_id_y-1), gen_id(sqr_id_x,sqr_id_y-1), gen_id(sqr_id_x+1,sqr_id_y-1),
        gen_id(sqr_id_x-1,sqr_id_y),                                gen_id(sqr_id_x+1,sqr_id_y),
        gen_id(sqr_id_x-1,sqr_id_y+1), gen_id(sqr_id_x,sqr_id_y+1), gen_id(sqr_id_x+1,sqr_id_y+1)
        ]
    for k in neighbor_keys:
        try:
            s = g.squares[k]
            if s.on:
                id_x = s.idx
                id_y = s.idy
                if id_x in [sqr_id_x - 1, sqr_id_x, sqr_id_x + 1] and id_y in [sqr_id_y - 1, sqr_id_y, sqr_id_y + 1]:
                    neighbors += 1
        except:
            pass    
    # # Way inefficient
    # for k, s in g.squares.items():
    #     if s.on:
    #         #id_x = int(k.split(":")[0])
    #         #id_y = int(k.split(":")[1])

    return neighbors

def iterateGame():
    # Rules
    #  If on box is touching 2-3 other "on" boxes, then stay alive
    #  If off box is touching 3 other "on" boxes, then become alive
    #  Otherwise die
    
    # Need to keep a list so we can do all the comparisons and THEN apply them
    turn_on = []
    turn_off = []
    for k, s in g.squares.items():
        if s.on:
            if p_run(neighbors_on,s) in [2,3]:
                turn_on.append(k)
            else:
                turn_off.append(k)
        else:
            if p_run(neighbors_on,s) == 3:
                turn_on.append(k)
    for k in turn_on:
        g.squares[k].on = True
    for k in turn_off:
        g.squares[k].on = False
            
                
def mouseClicked():
    speed_list = [ 1, 2, 4, 10, 15, 20, 30, 45, 60 ]
    if 10 <= mouseX <= 30 and 10 <= mouseY <= 40:
        print("Running Simulation.")
        g.play = True
    elif 40 <= mouseX <= 70 and 10 <= mouseY <= 40:
        print("Stopping Simulation.")
        g.play = False
    elif 90 <= mouseX <= 110 and 10 <= mouseY <= 40:
        print("Clearing Simulation.")
        g.play = False
        for k, s in g.squares.items():
            g.squares[k].on = False
    elif 120 <= mouseX <= 150 and 10 <= mouseY <= 40:
        idx = speed_list.index(g.iterspersec)
        if idx < len(speed_list)-1:
            g.iterspersec = speed_list[idx + 1]
    elif 160 <= mouseX <= 185 and 10 <= mouseY <= 40:
        idx = speed_list.index(g.iterspersec)
        if idx > 0:
            g.iterspersec = speed_list[idx - 1]


def setup():
    size(1000,800)
    frameRate(60)
    #fullScreen()
    global g
    g = Globals()
    g.grid_size = height / 40
    #g.grid_size = 10
    g.countH = int(height/g.grid_size)
    g.countW = int(width/g.grid_size)
    p_run(generate_squares)
    g.iterspersec = 1

def draw():
    g.tick += 1
    background(0)
    p_run(draw_squares)
    p_run(draw_buttons)
    if g.tick % int(60/g.iterspersec) == 0 and g.play == True:
        p_run(iterateGame)
    if DEBUG:
        if g.tick % 10 == 0:
            for k, v in profiler.items():
                print("%s: %s" % (k, v))
    if mousePressed:
        for k, s in g.squares.items():
            if s.x <= mouseX <= s.x2 and s.y <= mouseY <= s.y2:
                if mouseButton == LEFT:
                    s.on = True
                elif mouseButton == RIGHT:
                    s.on = False
                break
