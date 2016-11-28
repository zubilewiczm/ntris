import pygame

def noop(*args, **kwargs):
    pass

def not_implemented(*args, **kwargs):
    raise NotImplementedError()

def rect_inflate(rect, x,y):
    return pygame.Rect(rect.left-x,rect.top-y,rect.width+2*x,rect.height+2*y)

def hsv(i,n, s,v):
    h = 360*i/n
    c = pygame.Color(255)
    c.hsva = h,s,v
    c.a = 255
    return c

class TimerTrigger:
    def __init__(self, trigger, freq, onset = 0.0, mod = None):
        self.trigger = trigger
        self.def_freq = freq
        self.freq = freq
        self.onset = onset
        self.mod = mod if mod else lambda x: self.def_freq
        self.time = 0.0
        self.set = False
        self.active = False
    
    def __bool__(self):
        return self.active
    
    def activate(self):
        self.active = True
        return self
    
    def deactivate(self):
        return self.pause().reset()
    
    def pause(self):
        self.active = False
        return self
    
    def tick(self, dt):
        if self.active:
            self.time+= dt
            if not self.set:
                if self.time > self.onset:
                    self.time-= self.onset
                    self.set = True
                    self.trigger()
            else:
                while self.time > self.freq:
                    self.time-= self.freq
                    self.freq = self.mod(self.freq)
                    self.trigger()
    
    def reset(self):
        self.freq = self.def_freq
        self.set = False
        self.time = 0.0
        return self

class NiceTimer(TimerTrigger):
    def __init__(self, trigger, freq, q=0.9, onset=None):
        self.q = q
        super().__init__(trigger, freq, onset if onset else freq*2,
                         lambda x : self.q * (x + self.def_freq*(1-self.q)/(2*self.q)))
    
    def change_freq(self, freq, q=None):
        self.def_freq = freq
        self.onset = 2*freq
        self.q = q if q else self.q
        return self
        
class NormalTimer(TimerTrigger):
    def __init__(self, trigger, freq):
        super().__init__(trigger, freq, freq)
    
    def change_freq(self, freq):
        self.def_freq = freq
        self.onset = freq
        return self