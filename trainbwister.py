#!/usr/bin/env python

### BEGIN CONFIGURATION SECTION ###
# which RESOLUTION?
RESOLUTION = (1024,768)

# which SIZE of the visible area?
SIZE = (600,600)

# how many TRIALS per round (MINimum)
MINTRIALS = 20

# LENGTH of STimulus presentation in seconds
ST_LENGTH = 0.5

# LENGTH of Break between Trials in seconds
TB_LENGTH = 2.5

# which N-back initially?
N = 1

# sometimes the random distribution of stimuli results in a very low interaction on your part.
# in order to address this, do some ITERATIONS and take the maximum of all random distributions.
ITERATIONS = 15

# UPPER ThresHold, above which N is increased
UPPERTH = 90

# LOWER ThresHold, below which N is decreased
LOWERTH = 75

# SIZE of FONT
FONTSIZE = 20

KEYLEFT = "a"
KEYRIGHT = "o"
SPACE = " "
IFS = ['1.png','2.png','3.png','4.png','5.png','6.png','7.png','8.png']
SFS = ['1.ogg','2.ogg','3.ogg','4.ogg','5.ogg','6.ogg','7.ogg','8.ogg']

### END CONFIGURATION SECTION ###

TRIALS = MINTRIALS + N
TOPLEFT =((RESOLUTION[0]-SIZE[0])/2,(RESOLUTION[1]-SIZE[1])/2)

import time, sys
from random import randint
from pygame import display, image, key, Surface, mixer, event, mouse, font
from pygame import FULLSCREEN, KEYDOWN
from pygame.transform import scale

def selftests():
    die = None
    for f in IFS+SFS:
        try:
            open(f,"rb")
        except IOError, e:
            die = e
            print >> sys.stderr, "FATAL:",die
    if die:
        raise die

    if not len(IFS) == len(SFS):
        print >> sys.stderr, "FATAL: amount of stimuli for different modalities do not match!"
        sys.exit(1)

class Trial:
    def __init__(self,imagefile,soundfile,trgtimg,trgtsnd):
        self.image = scale(image.load(imagefile), SIZE).convert()
        self.sound = mixer.Sound(soundfile)
        self.trgtimg = trgtimg
        self.trgtsnd = trgtsnd
        self.result = [not(self.trgtimg),not(self.trgtsnd)]

    def runtrial(self):
        surface = display.get_surface()
        surface.fill((255,255,255))
        surface.blit(self.image,TOPLEFT)
        display.flip()
        self.sound.play()
        time.sleep(ST_LENGTH)
        surface.fill((255,255,255))
        display.flip()
        time.sleep(TB_LENGTH)
        keypresses = []
        for e in event.get(KEYDOWN):
            keypresses += [e.dict['unicode']]
        if unicode(KEYLEFT) in keypresses:
            if self.trgtimg:
                #print "user hit key \""+ KEYLEFT +"\" correctly"
                self.result[0] = True
            else:
                #print "user hit key \""+ KEYLEFT +"\" incorrectly"
                self.result[0] = False
        if unicode(KEYRIGHT) in keypresses:
            if self.trgtsnd:
                #print "user hit key \""+ KEYRIGHT +"\" correctly"
                self.result[1] = True
            else:
                #print "user hit key \""+ KEYRIGHT +"\" incorrectly"
                self.result[1] = False

def nfroml(n,l):
    if n > 0:
        return [l[randint(0,len(l)-1)]]+nfroml(n-1,l)
    else:
        return []

def nback(n,l):
    if n >= len(l):
        return 0
    elif l[0] == l[n]:
        return 1+nback(n,l[1:])
    else:
        return nback(n,l[1:])

def cheatshuffle(l):
    tmp1 = nfroml(TRIALS,l)
    positives1 = nback(N,tmp1)
    for i in range(0,ITERATIONS):
        tmp2 = nfroml(TRIALS,l)
        positives2 = nback(N,tmp2)
        if positives1 < positives2:
            #print positives1, "<", positives2
            tmp1 = tmp2
            positives1 = positives2
    return tmp1

def gentrials():
    trials = []
    iis = cheatshuffle(range(0,len(IFS)-1))
    sis = cheatshuffle(range(0,len(SFS)-1))
    for i,j,k in zip(iis,sis,range(0,len(iis)-1)):
        if k < N:
            trials.append(Trial(IFS[i],SFS[j],False,False))
        else:
            nb = k - N
            trials.append(Trial(IFS[i],SFS[j],iis[k]==iis[nb],sis[k]==sis[nb]))
    return trials

def qcont(string):
    event.clear()
    mf = font.Font(font.get_default_font(),FONTSIZE)
    foo = display.get_surface()
    foo.fill((0,0,0))
    foo.blit(mf.render(string,True,(0,255,0),(0,0,0)),TOPLEFT)
    display.flip()
    es = []
    while not es:
        for e in event.get(KEYDOWN):
            es += [e.dict['unicode']]
    if SPACE in es:
        return True
    else:
        return False
    
    

def main():
    selftests()
    global N
    while 1:
        display.init()
        display.set_mode(RESOLUTION, FULLSCREEN)
        font.init()
        mixer.init(44100)
        event.set_grab(True)
        mouse.set_visible(False)
        trials = gentrials()
        for trial in trials:
            trial.runtrial()
            print trial.result
        display.quit()
        vis = 0.0
        acu = 0.0
        for trial in trials:
            if trial.result[0]:
                vis+=1
            if trial.result[1]:
                acu+=1
        vp = (vis/TRIALS)*100
        ap = (acu/TRIALS)*100
        message = """percentage in visual modality:%i\n
        percentage in acoustic modality:%i\n""" %(int(vp),int(ap))
        print message
        if vp >= UPPERTH and ap >= UPPERTH:
            N+=1
        elif vp < LOWERTH or ap < LOWERTH and N > 1:
            N-=1

if __name__ == "__main__":
    main()
