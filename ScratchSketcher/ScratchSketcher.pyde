import os
import json
import sys

class Globals():
    def __init__(self):
        self.currentPrimaryColor = color(255, 255, 255)
        self.currentSecondaryColor = color(0,0,0)
        self.colors = []
        self.palette = PaletteBox()
        self.tick = 0
        
class ColorBox():
    # By making each color an object with a hitbox, I can use the same logic to check for stuff.
    def draw_colorbox(self):
        stroke(0)
        fill(self.c)
        rect(self.x, self.y, self.w, self.h, 7)
    def update(self):
        self.hitbox = [(self.x, self.y, self.h, self.w)]
    def __init__(self):
        self.x = 0
        self.y = 0
        self.h = height * 0.06
        self.w = width * 0.06
        self.c = color(0)
        self.update()

class Mouse():
    def update(self):
        self.hitbox = [(mouseX, mouseY, 1, 1)]
    def is_touching(self,obj):
        self.update()
        return isTouching(self, obj)
    def drawMouse(self):
        # ellipse(mouseX,mouseY,50,50)
        fill(g.currentPrimaryColor)
        stroke(g.currentSecondaryColor)
        square(mouseX + 10, mouseY + 15, 9)
        stroke(0)
        fill(255)
        triangle(mouseX, mouseY, mouseX+3, mouseY + 20, mouseX + 18, mouseY + 10)
    def __init__(self):
        self.x = mouseX
        self.y = mouseY
        self.hitbox = [(self.x, self.y, 1, 1)]

class PaletteBox():
    def __init__(self):
        self.leftBorderX = width * 0.5
        self.rightBorderX = width * 0.98
        self.topBorderY = height * 0.86
        self.midBorderY = height * 0.92
        self.botBorderY = height * 0.98

class Button():
    def set_font_type(self,font_name):
        if font_name in PFont.list():
            self._font = createFont(font_name, self.font_size, True)
            self._font_name = font_name
        else:
            print("ERROR: Font %s is not supported" % font_name)
            print(PFont.list())
            sys.exit(1)
    def set_font_size(self,font_size):
        self._font = createFont(self._font_name, font_size, True)
        self.font_size = font_size
        self.w = 30 + (font_size * 0.5) * len(self.name)
        self.h = font_size * 1.3
    def update(self):
        self.hitbox = [(self.x, self.y, self.h, self.w)]
    def draw(self):
        fill(255)
        stroke(0)
        rect(self.x, self.y, self.w, self.h, 10)
        stroke(0)
        fill(0)
        textFont(self._font)
        text(self.name, self.x + 10, self.y + (self.h/1.2))
    def click(self):
        print("button %s clicked!" % self.name)
    def __init__(self):
        self.x = 10
        self.y = 10
        self.action = "None"
        self.name = "Button"
        self._font_name = "Arial"
        self.font = self.set_font_type
        self.size = self.set_font_size
        self.font_size = 16
        self._font = createFont("Arial", self.font_size, True)
        self.w = 50
        self.h = 20
        self.hitbox = [(self.x, self.y, self.h, self.w)]

def list_images():
    images = []
    file_list = [ f for f in os.listdir(".") if os.path.isfile(os.path.join(".", f)) ]
    for f in file_list:
        if any(x in f for x in ["png", "jpg", "jpeg", "tiff", "gif", "bmp"]):
            images.append(f)
    return images
        
def drawPaintPalette():
    stroke(0)
    p = g.palette
    # Top
    line(p.leftBorderX, p.topBorderY, p.rightBorderX, p.topBorderY)
    # Middle Line
    line(p.leftBorderX, p.midBorderY, p.rightBorderX, p.midBorderY)
    # Bottom line
    line(p.leftBorderX, p.botBorderY, p.rightBorderX, p.botBorderY)
    # Left
    line(p.leftBorderX, p.topBorderY, p.leftBorderX, p.botBorderY)
    # Right
    line(p.rightBorderX, p.topBorderY, p.rightBorderX, p.botBorderY)
    for c in g.colors:
        c.draw_colorbox()
    
def generate_colors():    
    color_list = [
                  color(255,255,255), 
                  color(128,128,128),
                  color( 64, 64, 64),
                  color(  0,  0,  0), 
                  color(255,  0,  0), 
                  color(  0,255,  0), 
                  color(  0,  0,255),
                  color(255,255,  0),
                  color(255,  0,255),
                  color(  0,255,255),
                  color(128,255,255),
                  color(255,128,255),
                  color(255,255,128),
                  color( 64,255,255),
                  color(255, 64,255),
                  color(255,255, 64),
                  color(128,  0,  0),
                  color(  0,128,  0),
                  color(  0,  0,128),
                  color( 64,  0,  0),
                  color(  0, 64,  0),
                  color(  0,  0, 64),
                  ]    
    numColors = len(color_list)
    p = g.palette
    count = 0
    for c in color_list:
        boxHeight = p.midBorderY - p.topBorderY
        boxWidth = (width - p.leftBorderX) / (numColors/2)
        if count >= numColors / 2:
            y = p.midBorderY
            x = p.leftBorderX + (boxWidth * (count - (numColors/2)))
        else:
            y = p.topBorderY
            x = p.leftBorderX + (boxWidth * count)
        newC = ColorBox()
        newC.x = x
        newC.y = y
        newC.h = boxHeight
        newC.w = boxWidth
        newC.c = c
        newC.id = count
        g.colors.append(newC)
        count += 1



def isTouching(obj1, obj2):
    # Expects each object to have a hitbox tuple with 4 values
    # (x, y, height, width)
    all_hitboxes = obj1.hitbox + obj2.hitbox
    for hb in all_hitboxes:
        for hb2 in all_hitboxes:
            if hb != hb2:
                obj1_left = hb[0]
                obj1_right = hb[0] + hb[3]
                obj1_top = hb[1]
                obj1_bottom = hb[1] + hb[3]
                
                # Generate 4 x,y coords for each object using the hitbox values
                #  A B
                #  C D
                obj1_A = (obj1_left , obj1_top)
                obj1_B = (obj1_right, obj1_top)
                obj1_C = (obj1_left , obj1_bottom)
                obj1_D = (obj1_right, obj1_bottom)
                
                obj2_left = hb2[0]
                obj2_right = hb2[0] + hb2[3]
                obj2_top = hb2[1]
                obj2_bottom = hb2[1] + hb2[2]
                
                obj2_A = (obj2_left , obj2_top)
                obj2_B = (obj2_right, obj2_top)
                obj2_C = (obj2_left , obj2_bottom)
                obj2_D = (obj2_right, obj2_bottom)
            
                # See if any of OBJ1's points are within OBJ2's space
                if obj2_left <= obj1_A[0] <= obj2_right and obj2_top <= obj1_A[1] <= obj2_bottom:
                    return True
                if obj2_left <= obj1_B[0] <= obj2_right and obj2_top <= obj1_B[1] <= obj2_bottom:
                    return True
                if obj2_left <= obj1_C[0] <= obj2_right and obj2_top <= obj1_C[1] <= obj2_bottom:
                    return True
                if obj2_left <= obj1_D[0] <= obj2_right and obj2_top <= obj1_D[1] <= obj2_bottom:
                    return True
                # See if OBJ2's points are in OBJ1's space now
                if obj1_left <= obj2_A[0] <= obj1_right and obj1_top <= obj2_A[1] <= obj1_bottom:
                    return True
                if obj1_left <= obj2_B[0] <= obj1_right and obj1_top <= obj2_B[1] <= obj1_bottom:
                    return True
                if obj1_left <= obj2_C[0] <= obj1_right and obj1_top <= obj2_C[1] <= obj1_bottom:
                    return True
                if obj1_left <= obj2_D[0] <= obj1_right and obj1_top <= obj2_D[1] <= obj1_bottom:
                    return True
    return False
                
def drawPaintToolBox():
    pass
    
def drawPaintCanvas():
    pass

def drawPaint():
    drawPaintPalette()
    drawPaintToolBox()
    drawPaintCanvas()

def generateButtons():
    buttons = []
    fill(0)
    stroke(0)
    bsave = Button()
    bsave.name = "Save"
    bsave.x = 15
    bsave.y = height * 0.9
    bsave.font("Impact")
    bsave.size(25)
    bsave.update()
    buttons.append(bsave)
    bload = Button()
    bload.name = "Load"
    bload.x = 100
    bload.y = height * 0.9
    bload.font("Impact")
    bload.size(25)
    bload.update()
    buttons.append(bload)
    return buttons

def drawButtons():
    for button in g.buttons:
        button.draw()

def mouseClicked():
    for button in g.buttons:
        if g.mouse.is_touching(button):
            button.click()
    for c in g.colors:
        c.update()
        if g.mouse.is_touching(c):
            g.currentPrimaryColor = c.c

def setup():
    size(800,600)
    frameRate(60)
    global g
    g = Globals()
    g.mouse = Mouse()
    generate_colors()
    noCursor()
    g.buttons = generateButtons()
    g.image_list = list_images()
    
def draw():
    g.tick += 1
    background(200)
    drawPaint()
    drawButtons()
    g.mouse.drawMouse()
