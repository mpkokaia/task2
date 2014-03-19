import cairo
import codecs
import dateutil.parser
import igraph
import numpy
import re

from pymongo import Connection
connection = Connection()
db = connection.urfu 

def getNetwork_hub():
	f = open('Clusters.txt')
	data_Clusters = f.readlines() 
	f.close()

	Cluster=[]
	for line in data_Clusters:
		line = line.strip()
		data = line.split(':')
                if len(data)==2:
			users = data[1].split(',')
			Cluster.append(data[0])
	f = open('hub.txt')
	data_hubs = f.readlines()
	f.close()
	hubs={}
	for line in data_hubs:
		line=line.strip()
		data = line.split(':')    
		users = data[1].split(',')
		hubs[data[0]]=users[:]
	nodes = Cluster+["" for i in hubs]
        param_hubs = ["cl"]*len(Cluster)+['hub']*len(hubs)
	nodeMap = dict([(v,i) for i,v in enumerate(nodes)])
        edges=[]
	for en,i in enumerate(hubs):
		for val in hubs[i]:
			edges.append((int(val), en+len(Cluster)))
	edges, weights = map(list, zip(*[[e, edges.count(e)] for e in set(edges)]))
	graph = igraph.Graph(edges)
	layout = graph.layout("drl")
	graph.es['weight'] = weights
	graph.vs['hubs'] = param_hubs
	graph.vs['label'] = nodes
	color_dict = {"cl": "red", "hub": "blue"}
	graph.vs["color"] = [color_dict[h] for h in graph.vs['hubs']]
	igraph.plot(graph,"social_network_hub.png", layout = layout, bbox = (7000, 7000), margin = 20)
	return graph

 
def project2D(layout, alpha, beta):
	c = numpy.matrix([[1, 0, 0], [0, numpy.cos(alpha), numpy.sin(alpha)], [0, -numpy.sin(alpha), numpy.cos(alpha)]])
	c = c * numpy.matrix([[numpy.cos(beta), 0, -numpy.sin(beta)], [0, 1, 0], [numpy.sin(beta), 0, numpy.cos(beta)]])
	b = numpy.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

	layout = numpy.matrix(layout)
	X = (b * (c * layout.transpose())).transpose()
	return [[X[i,0],X[i,1],X[i,2]] for i in range(X.shape[0])]
 
def drawGraph3D(graph, layout, angle, fileName):
	'''
	Draw a graph in 3D with the given layout, angle, and filename.
	'''
	graph.vs['degree'] = graph.degree()
	vertexRadius = 0.1 * (0.9 * 0.9) / numpy.sqrt(graph.vcount())
	graph.vs['x3'], graph.vs['y3'], graph.vs['z3'] = zip(*layout)
	
	
	layout2D = project2D(layout, angle[0], angle[1])
	graph.vs['x2'], graph.vs['y2'], graph.vs['z2'] = zip(*layout2D)
	minX, maxX = min(graph.vs['x2']), max(graph.vs['x2'])
	minY, maxY = min(graph.vs['y2']), max(graph.vs['y2'])
	minZ, maxZ = min(graph.vs['z2']), max(graph.vs['z2'])
	
	# Calculate the draw order.  This is important if we want this to look
	# realistically 3D.
	zVal, zOrder = zip(*sorted(zip(graph.vs['z3'], range(graph.vcount()))))
	
	# Setup the cairo surface
	surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 800)
	con = cairo.Context(surf)
	con.scale(1280.0, 800.0)
	
	# Draw the background
	con.set_source_rgba(0.0, 0.0, 0.0, 1.0)
	con.rectangle(0.0, 0.0, 1.0, 1.0)
	con.fill()
	
	# Draw the edges without respect to z-order but set their alpha along
	# a linear gradient to represent depth.
	for e in graph.get_edgelist():
		# Get the first vertex info
		v0 = graph.vs[e[0]]
		x0 = (v0['x2'] - minX) / (maxX - minX)
		y0 = (v0['y2'] - minY) / (maxY - minY)
		alpha0 = (v0['z2'] - minZ) / (maxZ - minZ)
		alpha0 = max(0.1, alpha0)
		
		v1 = graph.vs[e[1]]
		x1 = (v1['x2'] - minX) / (maxX - minX)
		y1 = (v1['y2'] - minY) / (maxY - minY)
		alpha1 = (v1['z2'] - minZ) / (maxZ - minZ)	
		alpha1 = max(0.1, alpha1)
		
		# Setup the pattern info
		pat = cairo.LinearGradient(x0, y0, x1, y1)
		pat.add_color_stop_rgba(0, 0, 1.0, 1.0,  alpha0 / 6.0)
		pat.add_color_stop_rgba(1, 0, 1.0, 1.0,  alpha1 / 6.0)
		con.set_source(pat)
		
		# Draw the line
		con.set_line_width(vertexRadius / 4.0)
		con.move_to(x0, y0)		
		con.line_to(x1, y1)
		con.stroke()
	
	for i in zOrder:
		v = graph.vs[i]
		alpha = (v['z2'] - minZ) / (maxZ - minZ)
		alpha = max(0.1, alpha)
		radius = vertexRadius
		x = (v['x2'] - minX) / (maxX - minX)
		y = (v['y2'] - minY) / (maxY - minY)
		
		pat = cairo.RadialGradient(x, y, radius / 4.0, x, y, radius)

                if graph.vs["hubs"][i]=='cl':
			pat.add_color_stop_rgba(0, alpha, 0, 0, 1)
                elif graph.vs["hubs"][i]=='hub':
			pat.add_color_stop_rgba(0, 0, alpha/1.5, 0, 1)
		pat.add_color_stop_rgba(1, 0, 0, 0, 1)
		con.set_source(pat)
	
		con.move_to(x, y)
		con.arc(x, y, radius, 0, 2 * numpy.pi)
		con.fill()
	
	surf.write_to_png(fileName)

def draw_graph(func, filename):
	graph = func()
	layout = graph.layout_kamada_kawai_3d()
	
	for frame in range(400):
		alpha = frame * numpy.pi / 200.
		beta = frame * numpy.pi / 150.
		drawGraph3D(graph, layout, (alpha, beta), filename + "/%08d.png" % (frame))
 
if __name__ == "__main__":
	draw_graph(getNetwork_hub, 'frames_hub')

