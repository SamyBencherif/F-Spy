
from threading import Thread

WORKING = [200,200,0]

class button:
    
    def __init__(self, label, target):
        self.label = label
        self.url = None
        self.target = target
        self.pressed = False
        textSize(24)
        self.w = textWidth(label)+10
        self.h = 34
        self.x = 0
        self.y = 0
        self.color = [180,180,180]
        self.active = True
        self.labelOnly = False
    
    def setLabelOnly(self, v):
        self.labelOnly = v
        if v:
            self.color = [0,0,0]
    
    def setLabel(self, text):
        self.w = textWidth(text)+10
        self.label = text
    
    def draw(self):
        
        # readonly short-hands
        x = self.x
        y = self.y
        w = self.w
        h = self.h
        
        mouseOver = (x < mouseX < x+w) and (y < mouseY < y+h)
        
        if self.labelOnly:
            fill(0) # label only text defaults black
        else:
            fill(170) # button body defaults gray
        if self.active:
            if mouseOver and mousePressed:
                if self.pressed == False:
                    self.pressed = True
                if self.labelOnly:
                    fill(100)
                else:
                    fill(255)
            elif mouseOver:
                if self.labelOnly:
                    fill(50)
                else:
                    fill(200)
                
            if not mousePressed and self.pressed:
                # button release
                self.pressed = False
                self.target(self)
        else:
            fill(0)
        
        if not self.labelOnly:
            # highlight or darken
            noStroke()
            rect(x,y,w,h)
        
            # actual button
            stroke(30)
            strokeWeight(1)
            fill(self.color[0],self.color[1],self.color[2],140)
            rect(x,y,w,h)
        
        if not self.labelOnly: 
            fill(0)
            
        if self.labelOnly:
            fill(*self.color)
            
        noStroke()
        textAlign(LEFT, TOP)
        textSize(24)
        text(self.label, x+5, y+5)

class UI:
    
    def __init__(self):
        self.columns = [(0,0)]
        self.elements = []
    
    def remove(self, element):
        if not element in self.elements: return
        i = self.elements.index(element)
        # assuming all deleted elements are in column=0 (for this particular program)
        self.columns[1] = (0, self.columns[1][1]-element.h-5)
        del self.elements[i]
    
    def addRow(self, element, col=0):
        if col != 0:
            element.x = 5+self.columns[col-1][0]
        else:
            element.x = 5
        element.y = self.columns[col][1]+5
        colWidth = max(self.columns[col][0], element.x+element.w)
        self.columns[col] = (colWidth, element.y+element.h)
        self.elements.append(element)

    def addColumn(self, element):
        col = len(self.columns)
        self.columns.append((0,0))
        element.x = 5+self.columns[col-1][0]
        element.y = self.columns[col][1]+5
        colWidth = max(self.columns[col][0], element.x+element.w)
        self.columns[col] = (colWidth, element.y+element.h)
        self.elements.append(element)

    def getWidth(self):
        return int(self.columns[-1][0]+5)

    def draw(self):
        for element in self.elements:
            element.draw()

ui = UI()

# paths of folders to scan
folders = []

# filesystem buttons presented via ui
ui.navButtons = []
   
# paths of folders with detected change
changed = []

working = []

# the entire recursive tree
fs = {}

def stringhash(x):
    return hash(x)

def filehash(path):
    # this hash should depend on the file's contents, title, and metadata
    # instead, it is a quick hash of some values that correspond to access/modifcation time
    # as well as file size (for simplicity and speed)
    
    ui.progress += 1 / 100000 # just assume there's 100k files for the damn progress bar
    
    try:
        res = os.stat(path)
        h = stringhash(str(res.st_atime)+str(res.st_mtime)+str(res.st_ctime)+str(res.st_size))
        return h
    except:
        # return arbitrary static hash
        return hash(0)

def combinehash(x,y):
    return hash(x+y)

def track(path, hash):

    if path in fs.keys():
        if fs[os.path.abspath(path)] != hash:
            changed.append(os.path.abspath(path))

    fs.update({os.path.abspath(path):hash})

def updateButtonColors():
            
    for btn in ui.navButtons:
        if os.path.abspath(btn.url) in fs.keys():
            btn.color = [0,0,200]
        if os.path.abspath(btn.url) in changed:
            btn.color = [200,0,0]
        if btn.url in working:
            btn.color = WORKING
        
def genHash(path):
    
    # set "I'm working on it" color
    for btn in ui.navButtons:
        if btn.url in os.path.abspath(path):
            btn.color = WORKING
            working.append(btn.url)
    
    walker = os.walk(path)
    hash = stringhash(path)
    
    try:
        dirpath, dirnames, filenames = walker.send(None)
        hash = combinehash(hash, stringhash(dirpath))

        for f in filenames:
            # track the file
            fhash = filehash(dirpath+os.sep+f)
            track(dirpath+os.sep+f, fhash)
            
            # mix it into super-directory's hash
            hash = combinehash(hash, fhash)
            
        for d in dirnames:
            # track the directory
            dhash = genHash(dirpath+os.sep+d)
            track(dirpath+os.sep+d, dhash)
            
            # mix it into super-directory's hash
            hash = combinehash(hash, dhash)
    except StopIteration:
        pass
        
    # track the original directory and hash
    track(path, hash)
 
    # give immediate feedback in nav buttons
    for btn in ui.navButtons:
        if btn.url in fs.keys():
            btn.color = [0,0,200]
        if btn.url in changed:
            btn.color = [200,0,0]

    return hash
                
def scan():
    ui.btn_scan.active = False
    for folder in folders:
        folder.color = WORKING
        # create a hash for folder, which will be saved in fs
        genHash(folder.url)
        folder.color = [0,0,200]
        if os.path.abspath(folder.url) in changed:
            folder.color = [200,0,0]
    ui.btn_scan.active = True

def launch_scan(self):
    p = Thread(target=scan)
    p.start()
    
    # if scan takes less than 100ms, might as well block
    p.join(.1)

# meta function to rotate directory elements
def rotDir(n):
    def event(self):
        btns = sorted(ui.navButtons, key=lambda btn: btn.y)
        
        def forward():
            top = btns[0].y
            for i in range(1, len(btns)):
                btns[i-1].y = btns[i].y
            btns[-1].y = top
        
        def backward():
            bottom = btns[-1].y
            for i in range(len(btns)-1,0,-1):
                btns[i].y = btns[i-1].y
            btns[0].y = bottom
            
        if n==0: return
        if n<0: 
            backward()
            rotDir(n+1)(None)
        if n>0: 
            forward()
            rotDir(n-1)(None)
            
    return event
        
def navbtnclick(self):


    # continue on existing file explorer panel (same as scan button)
    ui.dirIndicator.setLabel("path: " + os.path.abspath(self.url))
    #ui.dirIndicator.active = True
    
    # get rid of existing folders
    for btn in ui.navButtons:
        ui.remove(btn)
    ui.navButtons = []
    
    # ../ btn
    btn = button('..', navbtnclick)
    btn.url = self.url + os.sep + '..'
    ui.navButtons.append(btn)
    ui.addRow(btn, col=1)
    
    # populate with subdirectories
    for fodir in sorted(os.listdir(self.url)):
        url = self.url+os.sep+fodir
        label = os.path.basename(url)
        if os.path.isdir(url):
            try:
                label += " (%i)" % len(os.listdir(url))
            except:
                label += " (?)"
        btn = button(label, navbtnclick)
        btn.url = url

        if not os.path.isdir(btn.url):
            btn.active = False
            btn.setLabelOnly(True)

        if btn.url in working:
            btn.color = WORKING
        if os.path.abspath(btn.url) in fs.keys():
            btn.color = [0,0,200]
        if os.path.abspath(btn.url) in changed:
            btn.color = [200,0,0]
            
        ui.navButtons.append(btn)
        ui.addRow(btn, col=1)

def rfolder_selected(selection):
    if (selection != None):
        btn = button(selection.getAbsolutePath(), navbtnclick)
        btn.url = btn.label
        ui.addRow(btn)
        folders.append(btn)

def add_rfolder(self):
    selectFolder("Select a folder to process:", "rfolder_selected");

def setup():
    ui.btn_addfolder = button("Add folder", add_rfolder)
    ui.addRow(ui.btn_addfolder)
    
    ui.btn_scan = button("Scan", launch_scan)
    ui.addColumn(ui.btn_scan)
    
    ui.addColumn(button('<<', rotDir(10)))
    ui.addColumn(button('<', rotDir(1)))
    ui.addColumn(button('>', rotDir(-1)))
    ui.addColumn(button('>>', rotDir(-10)))
    
    ui.dirIndicator = button('No Directory Selected', lambda k:None)
    ui.dirIndicator.active = False
    ui.dirIndicator.setLabelOnly(True)
    ui.addColumn(ui.dirIndicator)
    
    ui.progress = 0
    
    size(726, 420)
    this.getSurface().setResizable(True)

def draw():
    background(200)
    
    fill(255,0,0)
    rect(0,height-10,width*ui.progress,10)
    
    ui.draw()
