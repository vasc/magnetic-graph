#!/usr/bin/python
# -*- coding: utf-8 -*-

from magneticgraph import Canvas, Point
import re
import random as r
import sys
import math

if not len(sys.argv) == 2:
    print sys.argv
    print """Usage python graph_reshape.py filename
          filename - name of a file describing the 
          graph links, one link per line as:
          id1 id2"""
    sys.exit()

graph_file = open(sys.argv[1], "r")

nodes = {}
for line in graph_file:
    line = line.strip()
    match = re.match(r'([^\s])\s([^\s])', line)
    if not match: print "Malformed line: '%s'" % line
    node_from_id = match.group(1)
    node_to_id = match.group(2)
    for id in (node_from_id, node_to_id):
        if not id in nodes: nodes[id] = {'links': []}
    nodes[node_from_id]['links'].append(node_to_id)

width = 640
height = 320
canvas = Canvas(width, height, 0.1, 10000)
    
#nodes.reverse()
i = 0
for node in nodes:
    i+=1.0

    y = r.randint(1, height-1)#float((i % r)+1)/(r+1)*height
    x = r.randint(1, width-1)#float((i % r)+1)/(r+1)*width
    print x, y
    p = Point(x, y, 10000, title = node[:5])
    canvas.points.append(p)
    nodes[node]['p'] = p

for node in nodes:
    for dest in nodes[node]['links']:
        canvas.link(nodes[node]['p'], nodes[dest]['p'])

pixel_mov = 3.0
cm = canvas.center_of_mass()
odc = ((width/2)-cm[0])**2 + ((height/2)-cm[1])**2  
#canvas.show()
#canvas.visualize()
i = 0
while canvas.converge(pixel_mov, 3.0):
    #print canvas.converge_time, 'animation/frame%05d' % i
    #canvas.write_to_svg('animation/frame%05d' % i)
    i+=1
    cm = canvas.center_of_mass()
    ndc = ((width/2)-cm[0])**2 + ((height/2)-cm[1])**2
    if ndc > odc: 
        pixel_mov /= 1.25
        #print "pixels: %s (%s > %s)" % (dt, math.sqrt(ndc), math.sqrt(odc))
        if pixel_mov < 0.001 or canvas.converge_time > 300: break
    odc = ndc
        #break
print "converged in %ss of simulation time" % canvas.converge_time
canvas.show()
        

