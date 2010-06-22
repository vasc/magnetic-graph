#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import svg
import random as r
from threading import Thread
import pygame
import sys


class Canvas:
    def __init__(self, width, height, static_friction = .5, side_charge = 1):
        self.height = height
        self.width = width
        self.points = []
        self.static_friction = static_friction**2
        self.converge_time = 0
        self.side_charge = side_charge
        self.link_protons = []
        self.visualization = None

    def link(self, p1, p2, aq = 1, rq = None):
        if not p1 in self.points or not p2 in self.points:
            raise Exception('Points must be added before links')
        if rq == None: rq = (p1.q + p2.q) / 4
        x = (p1.x + p2.x) / 2
        y = (p1.y + p2.y) / 2
        proton = Point(x, y, rq, aq = aq)
        proton.atract = [p1, p2]
        self.link_protons.append(proton)

    def converge(self, mov = 3.0, max_dt = None):
        #dt2 = dt**2
        points = []
        points.extend(self.points)
        points.extend(self.link_protons)
        for p in points:
            p.clear_forces()
            p.fx += p.q*self.side_charge / p.x**2
            p.fx += -( p.q*self.side_charge / (self.width-p.x)**2 )
            p.fy += p.q*self.side_charge / p.y**2
            p.fy += -( p.q*self.side_charge / (self.height-p.y)**2 )

        #self.print_info()

        for pair in iterate_pairs(self.points):
            set_repulsive_forces(*pair)

        for p in self.link_protons:
            for other in points:
                if not other in p.atract: set_repulsive_forces(p, other)
            set_atractive_forces(p, p.atract[0])
            set_atractive_forces(p, p.atract[1])

        rfactor = r.randint(1, 20)
        dt2 = 1000
        for p in points:
            if p.over_static_friction(self.static_friction):
                temp_dt2 = mov/math.sqrt(p.fx**2+p.fy**2)
                if temp_dt2 < dt2 : dt2 = temp_dt2
        #print "displace in %ss" % math.sqrt(dt2)
        #if dt2 < 0.0004: return false

        if max_dt and max_dt**2 < dt2:
            dt2 = max_dt**2

        converging = False
        for p in points:
            #p.vx += p.fx * dt
            #p.vy += p.fy * dt
             if p.over_static_friction(self.static_friction):
                #if p.test(): print u"(%s, %s) + (%f%s, %f%s) @ %fs" % (p.x, p.y, abs(p.fx), (u'←', u'→')[p.fx>0], abs(p.fy), (u'↑', u'↓')[p.fy>0], math.sqrt(dt2))
                x = p.x + p.fx * dt2 
                y = p.y + p.fy * dt2
                p.ox = p.x
                p.oy = p.y
                p.x = x
                p.y = y
                #p.x += p.fx * dt2 
                #p.y += p.fy * dt2
                self.constraint_to_limits(p)
                converging = True
        self.converge_time += math.sqrt(dt2)
        return converging            

    def constraint_to_limits(self, p):
        if p.x <= 0: p.x = 1
        if p.x >= self.width: p.x = self.width - 1 
        if p.y <= 0: p.y = 1
        if p.y >= self.height: p.y = self.height - 1

    def print_info(self):
        for p in self.points: p.print_info()

    def center_of_mass(self):
        cx = 0;
        cy = 0;
        for p in self.points:
            cx += p.x
            cy += p.y
        cx /= len(self.points)
        cy /= len(self.points)
        return (cx, cy)

    def write_to_svg(self, filename):
        sc = svg.Scene(filename, height = self.height, width = self.width)
        sc.add(svg.Rectangle((0,0),self.height,self.width,(30,30,30)))
        #ax = reduce(lambda x, y: x+y, map(lambda x: p.x, self.points)) / len(self.points)
        #ay = reduce(lambda x, y: x+y, map(lambda x: p.y, self.points)) / len(self.points)
        for p in self.link_protons:
            sc.add(svg.Circle((p.x,p.y),3,(51,255,94)))
            #sc.add(svg.Circle((p.atract[0].x,p.atract[0].y),16,(51,255,94)))
            #sc.add(svg.Circle((p.atract[1].x,p.atract[1].y),16,(51,255,94)))
            sc.add(svg.QuadraticBezier((p.atract[0].x,p.atract[0].y), (p.atract[1].x,p.atract[1].y), (p.x,p.y), (249,249,249)))

        for p in self.points:
            sc.add(svg.Circle((p.x,p.y),16,(249,249,249), p.title))

        cm = self.center_of_mass()
        print cm
        sc.add(svg.Circle((cm[0],cm[1]),3,(255,51,94)))
        sc.write_svg()
        self.svg = sc

    def display_svg(self):
        self.svg.display(prog = "eog")

    def show(self):
        self.write_to_svg('canvas')
        self.display_svg()

    def visualize(self):
        if not self.visualize == None:
            self.visualize = {}
            v = self.visualize
            pygame.init()
            size = v['width'], v['height'] = self.width, self.height
            v['screen'] = pygame.display.set_mode(size)
            #t = Thread(target=self.update_visualization)
            #t.daemon = True
            #t.start()

    def update_visualization(self):
        v = self.visualize 
        node_image = pygame.image.load('node.png')
        node_rect = node_image.get_rect()     
        #while(True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        v['screen'].fill(pygame.Color(30,30,30, 255))
        for point in self.points:
            v['screen'].blit(node_image, node_rect.move(point.x, point.y))
            #pygame.draw.circle(v['screen'], pygame.Color(249,249,249, 255), (point.x, point.y), 16, 0)
        pygame.display.flip()
        

class Point:
    def __init__(self, x, y, q = 0, title = None, **kw):
        self.x = x
        self.ox = x
        self.y = y
        self.oy = y
        self.q = q
        self.fx = 0
        self.fy = 0
        self.vx = 0
        self.vy = 0
        self.history ={}
        self.atract = []
        self.title = title
        if 'aq' in kw: self.aq = kw['aq']

    def norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def onorm(self):
        return math.sqrt(self.ox**2 + self.oy**2)

    def magnitude(self):
        return self.fx**2 + self.fy**2

    def over_static_friction(self, static_friction):
        return static_friction < self.fx**2 + self.fy**2

    #def test(self):
    #    return (self.fx, self.fy) in self.history

    def clear_forces(self):
        #self.history[(self.fx, self.fy)] = TruePoint(x, y, 4000, title = '%s Node' % i)
        self.fx = 0
        self.fy = 0

    def print_info(self):
        print "x: %s + %sv + %sa" % (self.x, self.vx, self.fx)
        print "y: %s + %sv + %sa" % (self.y, self.vy, self.fy)
        print 


def iterate_pairs(lst):
    maxl = len(lst)
    for i in range(0, maxl):
        for j in range(i+1, maxl):
            yield (lst[i], lst[j])


def set_repulsive_forces(p1, p2):
    (dx, dy) = (abs(p1.x - p2.x), abs(p1.y - p2.y))
    #print "%sdx, %sdy => %sd" % (dx, dy, math.sqrt(dx**2 + dy**2))
    #h = math.sqrt(dx**2 + dy**2)
    h = math.sqrt(dx**2 + dy**2)
    if h == 0: (h, dx, dy) = (1, 1, 1)
    #fx = dx * (p1.q*p2.q) / (h2**3)
    #fy = dy * (p1.q*p2.q) / (h2**3)
    fx = dx * (p1.q*p2.q) / (h**3)
    fy = dy * (p1.q*p2.q) / (h**3)
    if p1.x < p2.x: 
        p1.fx += -fx
        p2.fx += fx
    else:
        p1.fx += fx
        p2.fx += -fx
    if p1.y < p2.y: 
        p1.fy += -fy
        p2.fy += fy
    else:
        p1.fy += fy
        p2.fy += -fy

def set_atractive_forces(pl, p):
    (dx, dy) = (abs(pl.x - p.x), abs(pl.y - p.y))
    h = math.sqrt(dx**2 + dy**2)
    if h == 0: (h, dx, dy) = (1, 1, 1)
    fx = dx * h / (pl.aq*p.q)
    fy = dy * h / (pl.aq*p.q)
    if pl.x > p.x: 
        pl.fx += -fx
        p.fx += fx
    else:
        pl.fx += fx
        p.fx += -fx
    if pl.y > p.y: 
        pl.fy += -fy
        p.fy += fy
    else:
        pl.fy += fy
        p.fy += -fy

def test(n = 5):
    canvas = Canvas(800, 800, 1, 4000)
    
    for i in range(n):
        x = r.randint(1, 799)
        y = r.randint(1, 799)
        p = Point(x, y, 4000, title = '%s Node' % i)
        canvas.points.append(p)

        cm = canvas.center_of_mass()
        odc = (400-cm[0])**2 + (400-cm[1])**2    

        #canvas.link(canvas.points[0], canvas.points[1])
        #canvas.link(canvas.points[1], canvas.points[2])
        #canvas.link(canvas.points[1], canvas.points[3])
        #canvas.link(canvas.points[4], canvas.points[0])
        for op in canvas.points[:-1]:
            if r.randint(0, 10) == 0:
                canvas.link(p, op, aq = .00025)

    
    dt = 400.0
    #count = 0
    while canvas.converge(dt):
        cm = canvas.center_of_mass()
        ndc = (240-cm[0])**2 + (400-cm[1])**2    
        if ndc > odc: 
            dt /= 2
            #print "pixels: %s (%s > %s)" % (dt, math.sqrt(ndc), math.sqrt(odc))
            if dt < 0.5 or canvas.converge_time > 300: break
        odc = ndc
        #break
    print "converged in %ss of simulation time" % canvas.converge_time
         
    #canvas.show()
    dt = 400.0
        #print '.run: %s' % i    (dx, dy) = (abs(p1.x - p2.x), abs(p1.y - p2.y))
    #print "%sdx, %sdy => %sd" % (dx, dy, math.sqrt(dx**2 + dy**2))
    #h = math.sqrt(dx**2 + dy**2)
    canvas.show()


def main():
    global canvas
    canvas = Canvas(200, 200)
    p1 = Point(20, 30, 200)
    p2 = Point(15, 50, 200)
    p3 = Point(20, 20, 200)
    p4 = Point(25, 60, 200)
    p5 = Point(30, 30, 200)
    p6 = Point(67, 44, 200)
    p7 = Point(27, 63, 200)
    p8 = Point(32, 37, 200)
    #p9 = Point(63, 49, 22)
    p9 = Point(160, 160, 200)
    canvas.points.append(p1)
    canvas.points.append(p2)
    canvas.points.append(p3)
    canvas.points.append(p4)
    canvas.points.append(p5)
    canvas.points.append(p6)
    canvas.points.append(p7)
    canvas.points.append(p8)
    canvas.points.append(p9)

def shift_to_center():
    global canvas
    expected_cm = (canvas.width/2, canvas.height/2)
    cm = canvas.center_of_mass()
    d = (expected_cm[0] - cm[0], expected_cm[1] - cm[1])
    for p in canvas.points:
        p.x += d[0]
        p.y += d[1]
        canvas.constraint_to_limits(p)
   



if __name__ == '__main__':
    main()
