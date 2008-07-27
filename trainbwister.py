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
BASE = 'base.png'

### END CONFIGURATION SECTION ###

TOPLEFT =((RESOLUTION[0]-SIZE[0])/2,(RESOLUTION[1]-SIZE[1])/2)

import time, sys, re
from random import randint
from pygame import display, image, key, Surface, mixer, event, mouse, font
from pygame import FULLSCREEN, KEYDOWN
from pygame.transform import scale

def selftests():
    die = None
    for f in IFS+SFS+[BASE]:
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
        self.fill = scale(image.load(BASE),SIZE).convert()
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
        surface.blit(self.fill,TOPLEFT)
        display.flip()
        time.sleep(TB_LENGTH)
        keypresses = []
        for e in event.get(KEYDOWN):
            keypresses += [e.dict['unicode']]
        if SPACE in keypresses:
            return None
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
        return True

def myrandom(l):
    result = []
    for i in range(0,N):
        result.append(l[randint(0,len(l)-1)])
    for i in range(0,MINTRIALS):
        if randint(0,1):
            result.append(result[-N])
        else:
            # be strict about probabilities
            myl = l[:]
            myl.pop(result[-N])
            result.append(myl[randint(0,len(myl)-1)])
    return result

def gentrials():
    trials = []
    iis = myrandom(range(0,len(IFS)-1))
    sis = myrandom(range(0,len(SFS)-1))
    for i,j,k in zip(iis,sis,range(0,len(iis))):
        if k < N:
            trials.append(Trial(IFS[i],SFS[j],False,False))
        else:
            nb = k - N
            trials.append(Trial(IFS[i],SFS[j],iis[k]==iis[nb],sis[k]==sis[nb]))
    return trials

def main():
    selftests()
    global N
    while 1:
        print "(Hint: while training, you can hit SPACE to abort)"
        print "Hit '"+KEYLEFT+"' if the",str(N)+". previous image is identical to the one shown"
        print "Hit '"+KEYRIGHT+"' if the",str(N)+". previous sound is identical to the one heard"
        while 1:
            print "Ready to train with N=%i?" %(N),
            spam = raw_input(" [Yes/No]? ")
            if re.match("y(es)?", spam, re.I):
                break
            elif re.match("n(o)?", spam, re.I):
                print "bye ._."
                sys.exit(1)
        display.init()
        display.set_mode(RESOLUTION, FULLSCREEN)
        font.init()
        mixer.init(44100)
        event.set_grab(True)
        mouse.set_visible(False)
        trials = gentrials()
        for trial in trials:
            if not trial.runtrial():
                break
        display.quit()
        vis = 0.0
        acu = 0.0
        for trial in trials:
            if trial.result[0]:
                vis+=1
            if trial.result[1]:
                acu+=1
        vp = (vis/(MINTRIALS+N))*100
        ap = (acu/(MINTRIALS+N))*100
        message = "percentage in visual modality:%i\npercentage in acoustic modality:%i\n" %(int(vp),int(ap))
        print message
        if vp >= UPPERTH and ap >= UPPERTH:
            N+=1
        elif (vp < LOWERTH or ap < LOWERTH) and N > 1:
            N-=1

if __name__ == "__main__":
    main()
