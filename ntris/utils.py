# MIT License
# 
# Copyright (c) 2016 Marcin Zubilewicz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pygame

def noop(*args, **kwargs):
    pass

def not_implemented(*args, **kwargs):
    raise NotImplementedError()

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
        self._freq = freq
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
                    self.trigger(self)
            else:
                while self.time > self._freq:
                    self.time-= self._freq
                    self._freq = self.mod(self._freq)
                    self.trigger(self)
    
    def reset(self):
        self._freq = self.def_freq
        self.set = False
        self.time = 0.0
        return self
    
    def hook(self, trig):
        old = self.trigger
        def new(t):
            trig(t)
            old(t)
        self.trigger = new
        
    @property
    def freq(self):
        return self.def_freq
    
    @freq.setter
    def set_freq(self, freq):
        self.change_freq(freq)
    
    def change_freq(self, freq):
        self.def_freq = freq
        return self
    

class NiceTimer(TimerTrigger):
    def __init__(self, trigger, freq, q=0.9, onset=None):
        self.q = q
        super().__init__(trigger, freq, onset if onset else freq*2,
                         lambda x : self.q * (x + self.def_freq*(1-self.q)/(2*self.q)))
    
    def change_freq(self, freq, q=None):
        self.def_freq = freq
        self.q = q if q else self.q
        return self
        
class NormalTimer(TimerTrigger):
    def __init__(self, trigger, freq):
        super().__init__(trigger, freq, freq)
    
    def change_freq(self, freq):
        self.def_freq = freq
        self.onset = freq
        return self

class MultiShot(NormalTimer):
    def __init__(self, trigger, freq, n=1):
        self.max = n
        self.n = 0
        def real_trigger(t):
            if t.n < t.max:
                trigger(t)
                t.n+= 1
            else:
                t.deactivate()
        super().__init__(real_trigger, freq)

        
        
class TimedSet(set):
    def add(self, x, time, trigger=lambda t: None):
        t = time if isinstance(time, TimerTrigger) else MultiShot(trigger, time)
        t.activate()
        super().add((x,t))
        
    def tick(self, dt):
        s = set()
        for x,t in super().__iter__():
            if not t:
                s.add((x,t))
            else:
                t.tick(dt)
        for z in s:
            self.remove(z)
    
    def __iter__(self):
        for x,t in super().__iter__():
            if x is not None:
                yield x