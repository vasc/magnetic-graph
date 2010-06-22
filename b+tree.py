#!/usr/bin/python
# -*- coding: utf-8 -*-

from magneticgraph import Canvas, Point
import re
import random as r

graph_file = open("b+tree50.g", "r")

nodes = []
max_level = 0
for line in graph_file:
    match = re.match(r'(\s*)\| (\d+) \|( (\d) \|)?', line)
    node = {'level': len(match.group(1)), 'from': match.group(2)}
    if len(match.group(1)) > max_level: max_level = len(match.group(1))
    if not match.group(4) == None: node['to'] = match.group(4)
    else: node['to'] = '-'
    nodes.append(node)

width = 640
height = 320
canvas = Canvas(width, height, 0.1, 100)
    
#nodes.reverse()
node = nodes[0]
x = 1
y = 1
title = str(node['from'])
if 'to' in node: title += ' ' + str(node['to'])
master = Point(x, y, 100, title = title)
node_chain = [(node, master)]
canvas.points.append(master)
i = 1
for node in nodes[1:]:
    i+=1
    y = node['level']*(height-1)/max_level
    x = i*(width-1)/len(nodes)
    title = str(node['from'])
    if 'to' in node: title += ' ' + str(node['to'])
    p = Point(x, y, 100, title = title)
    canvas.points.append(p)
    if node['level'] > node_chain[-1:][0][0]['level']:
        canvas.link(p, node_chain[-1:][0][1])
    elif node['level'] <= node_chain[-1:][0][0]['level']:
        print node_chain
        while node['level'] <= node_chain[-1:][0][0]['level']: 
            node_chain = node_chain[:-1]
        canvas.link(p, node_chain[-1:][0][1])
    node_chain.append((node, p))

pixel_mov = 1.0
cm = canvas.center_of_mass()
odc = ((width/2)-cm[0])**2 + ((height/2)-cm[1])**2  
#canvas.show()
#canvas.visualize()
i = 0
while canvas.converge(pixel_mov, 3.0):
    print canvas.converge_time, 'animation/frame%05d' % i
    canvas.write_to_svg('animation/frame%05d' % i)
    i+=1
    cm = canvas.center_of_mass()
    ndc = ((width/2)-cm[0])**2 + ((height/2)-cm[1])**2
    if ndc > odc: 
        pixel_mov /= 2
        #print "pixels: %s (%s > %s)" % (dt, math.sqrt(ndc), math.sqrt(odc))
        if pixel_mov < 0.2 or canvas.converge_time > 300: break
    odc = ndc
        #break
print "converged in %ss of simulation time" % canvas.converge_time
canvas.show()
        

