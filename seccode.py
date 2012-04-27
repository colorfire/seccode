#!/usr/bin/env python
#coding:utf-8

import Image,ImageFont,ImageDraw
import os,sys
from math import atan2,pi
import pickle

#import psyco
#psyco.full()

DURATION = 1000
DIAMETER = 20
COLORDIFF = 10
TEXTCOLOR = (128,128,128)
BACKGROUND = (255,255,255)
MODE = 'sample'
samples = None

def printframe(im,code=-1):
	frame = im.load()
	(w,h) = im.size
	for j in xrange(h):
		for i in xrange(w):
			if (code == -1 and frame[i,j] !=BACKGROUND) or (code != -1 and frame[i,j]==code) :
				print '*',
			else:
				print ' ',
		print

def printregion(region):
	frame = region.getdata()
	(w,h)=region.size
	for i in range(h):
		for j in range(w):
			if frame[i*w+j] != BACKGROUND:
				print '*',
			else:
				print ' ',
		print

def purify(region):
	frame = region.getdata()
	(w,h)=region.size
	for i in range(h):
		for j in range(w):
			if frame[i*w+j] != BACKGROUND and frame[i*w+j] != (0,0,0):
				region.putpixel( (j,i), TEXTCOLOR )
			else:
				region.putpixel( (j,i), BACKGROUND )
	return region

def isnoise(points):
	'''Determine if the points are noisy points'''
#	pts = []
#	for p in points:
#		cnt = 0
#		for x in range( p[0]-1,p[0]+2 ):
#			for y in range( p[1]-1,p[1]+2 ):
#				try:
#					if (x,y) in points:
#						cnt += 1
#				except:
#					pass
#		if cnt > 1:
#			pts.append( p )
#	points = pts

	if len(points)<=20:
		return True

	# center point
	left = 255
	right = 0
	upper = 255
	lower = 0
	center = [0,0]
	for point in points:
		center[0]+=point[0]
		center[1]+=point[1]
	center[0]/=len(points)
	center[1]/=len(points)
	
	distance = 0
	farpoints = 0
	for point in points:
		dd = (point[0]-center[0])*(point[0]-center[0])+(point[1]-center[1])*(point[1]-center[1])
		distance += dd
		if dd > DIAMETER*DIAMETER:
			farpoints += 1
		if point[0]<left:
			left = point[0]
		if point[0]>right:
			right = point[0]
		if point[1]<upper:
			upper = point[1]
		if point[1]>lower:
			lower = point[1]
	area = abs(left-right)*abs(upper-lower)

	if farpoints>=5 or ( farpoints>5 and (area==0 or 1.0*len(points)/area<0.2) ):
		return True
	else:
		return False

def samecolor(rgb1,rgb2):
	diff = 0
	for i in range(3):
		diff += abs(rgb1[i]-rgb2[i])
	if diff < COLORDIFF:
		return True
	else:
		return False

def totif(fname):
	im = getframe(fname)
	im.save(fname[:4]+'.tif','TIFF')
	

def getframe(fname):
	'''return w*h key frame without noise'''
	#open image
	im = Image.open(fname)
	frame = None
	bkframe = []
	im = im.convert('RGB')
	frame = im.load()

	# denoize1: bk compare
	(w,h) = im.size
	for k in range(len(bkframe)):
		for i in xrange(w):
			for j in xrange(h):
				if samecolor( bkframe[k][i,j] , frame[i,j] ):
					frame[i,j] = BACKGROUND
	#print
	#printframe(im)
	#raw_input()	

	# count same color
	d = {}
	for i in xrange(w):
		for j in xrange(h):
			k = frame[i,j]
			if d.has_key(k):
				d[k][0] += 1
				d[k].append((i,j))
			else:
				d[k] = [1,(i,j)]
	topd = sorted(d.items(),cmp=lambda x,y:cmp(y[1][0],x[1][0]))

	# denoize2: group similar color
	cgrp = {}
	for k in d.keys():
		cgrp[k] = k
	for k1 in cgrp.keys():
		for k2 in cgrp.keys():	
			if k1 != k2 and cgrp[k1] == k1 and samecolor(k1,k2):
				cgrp[k2]=k1
	d = {}
	for i in xrange(w):
		for j in xrange(h):
			k = frame[i,j]
			k = cgrp[k]
			if d.has_key(k):
				d[k][0] += 1
				d[k].append((i,j))
			else:
				d[k] = [1,(i,j)]
	topd = sorted(d.items(),cmp=lambda x,y:cmp(y[1][0],x[1][0]))

	for i in xrange(w):
		for j in xrange(h):
			frame[i,j]=BACKGROUND

	found = 0
	for (k,v) in topd[1:]:
		if not isnoise(v[1:]):
#		if True:
			for point in v[1:]:
				frame[point[0],point[1]]=k
			found += 1
#			print k,
#			printframe(im,k)
#			raw_input()
		if found == 4:
			break
	print

	# denoize again
	for i in xrange(w):
		for j in xrange(h):
			if frame[i,j] != BACKGROUND:
				count = 0
				for m in xrange( max(0,i-1), min(i+2,w) ):
					for n in xrange( max(0,j-1), min(j+2,h) ):
						if frame[m,n] != BACKGROUND:
							count += 1
				if count <= 1:
					frame[i,j] = BACKGROUND
	im = fillholes(im)
	return im

def loadsamples():
	pks = pickle.load(open('samples.pk','rb'))
	samples = {}
	for (pk,v) in pks.items():
		im = Image.new('RGB',pk[0])
		r = im.crop((0,0,pk[0][0],pk[0][1]))
		r.fromstring(pk[1])
		samples[r] = v
	return samples

def loadttf():
	files = [ 'ttf/'+x for x in os.listdir('ttf') ]
	fonts = []
	for f in files:
		fonts.append( ImageFont.truetype(f,32) )

	regions = []
	regionsv = []
	for font in fonts:
		im = Image.new( 'RGB', (1000,50), BACKGROUND )
		draw = ImageDraw.Draw(im)
		draw.text(  (0,0),"B C E F G H J K M P Q R T V W X Y 2 3 4 6 7 8 9"\
				,font=font,fill=TEXTCOLOR )
		regions.extend( imdiv(im) )
		regionsv.extend( 'B C E F G H J K M P Q R T V W X Y 2 3 4 6 7 8 9'.split(' ') )

	for i in xrange(len(regions)):
		regions[i] = docrop(regions[i])	
		printregion( regions[i] )

	kv = {}
	for i in range(len(regions)):
		kv[regions[i]] = regionsv[i]

	return kv

def distance(r1,r2):
	den1 = density(r1)
	den2 = density(r2)
	if 1.0*den1/den2>1:
		(den1,den2) = (den2,den1)
	r1 = r1.resize(r2.size)	
	d1 = r1.getdata()
	d2 = r2.getdata()
	same = [0,0]
	total = [0,0]
	for i in xrange(len(d1)):
		if d1[i] != BACKGROUND:
			total[0] += 1
			if d1[i] == d2[i]:
				same[0] += 1
		if d2[i] != BACKGROUND:
			total[1] += 1
			if d1[i] == d2[i]:
				same[1] += 1
	return 1 - 1.0*same[0]/total[0] * 1.0*same[1]/total[1] * 1.0*den1/den2

def match(region,samples):
	if samples == {}:
		return None
	dists = []
	for (k,v) in samples.items():
		dists.append( (distance(region,k),v) )
	dists.sort()
	if MODE == 'sample':
		return dists[0][1]
	else:
		i = 0
		while dists[i][1] in ['H','I']:
			i += 1
		return dists[i][1]
#	printregion( region )
#	printregion( samples[ dists[0][1] ] )

def fillholes(region):
	SCORE = 9
	if density(region) > 0.5:
		SCORE = 14
	(w,h) = region.size
	turn = 0
	while turn < 1:
		turn += 1
		for i in range(1,w-1):
			for j in range(1,h-1):
				if region.getpixel((i,j)) == BACKGROUND:
					score = 0
					for m in range(i-1,i+2):
						for n in range(j-1,j+2):
							if region.getpixel((m,n)) != BACKGROUND:
								if m == i or n == j:
									score += 3
								else:
									score += 1
					if score >= SCORE:
						region.putpixel((i,j),TEXTCOLOR)
	return region

def imdiv2(im):
	divs = {}
	frame = im.load()
	(w,h) = im.size
	for i in range(w):
		for j in range(h):
			color = frame[i,j]
			if color != BACKGROUND:
				if divs.has_key( color ):
					divs[ color ].append( (i,j) )
				else:
					divs[ color ] = [ (i,j) ]
	
	regions = []
	divs = [ (x[0],sorted(x[1],cmp=lambda x,y:cmp(x[1],y[1]))) for x in  divs.items() ]
	divs.sort(cmp=lambda x,y:cmp(x[1][0],y[1][0]))
	for (color,pts) in divs:
		xs = [ x[0] for x in pts ]
		ys = [ x[1] for x in pts ]
		box = ( min(xs), min(ys), min(max(xs)+1,w), min(max(ys)+1,h) )
		regions.append(im.crop(box))
	
	return regions

def imdiv(im):
	'''div and return pieces of pics'''
	frame = im.load()
	(w,h) = im.size
	horis =  []
	for i in range(w):
		for j in range(h):
			if frame[i,j] != BACKGROUND:
				horis.append(i)
				break
	horis2 = [max(horis[0]-2,0)]
	for i in range(1,len(horis)-1):
		if horis[i]!=horis[i+1]-1:
			horis2.append((horis[i]+horis[i+1])/2)
	horis2.append(min(horis[-1]+3,w))
	boxes=[]
	for i in range(len(horis2)-1):
		boxes.append( [horis2[i],0,horis2[i+1],h]  )
	for k in range(len(boxes)):
		verts = []
		for j in range(h):
			for i in range(boxes[k][0],boxes[k][2]):
				if frame[i,j] != BACKGROUND:
					verts.append(j)
		boxes[k][1] = max(verts[0]-2,0)
		boxes[k][3] = min(verts[-1]+3,h)
	if boxes == []:
		return None
	regions = []
	for box in boxes:
		regions.append( im.crop(box) )
	return regions

def getcrop(region):
	frame = region.getdata()
	(w,h)=region.size
	pts = []
	ptsi = []
	for i in range(h):
		for j in range(w):
			if frame[i*w+j] != BACKGROUND and frame[i*w+j] != (0,0,0):
				pts.append((i,j))
				ptsi.append((j,i))
	if pts == []:
		return [0,0,1,1]
	pp1 = min(pts)
	pp2 = max(pts)
	pp3 = min(ptsi)
	pp4 = max(ptsi)
	return [pp3[0],pp1[0],pp4[0]+1,pp2[0]+1]

def density(region):
	frame = region.getdata()
	(w,h) = region.size
	area_all = w*h
	area = 0
	for i in range(h):
		for j in range(w):
			if frame[i*w+j] != BACKGROUND and frame[i*w+j] != (0,0,0):
				area += 1
	return 1.0*area/area_all

def docrop(region):
	croppos = getcrop(region)
	newregion = region.crop(croppos)
	return newregion

def dorotate(region):
#	printregion(region)
	deg = 0
	maxdens = 0
	for i in range(-30,31):
		dens = density( docrop( region.rotate(i) ) )
		if dens > maxdens:
			deg = i
			maxdens = dens
#	printregion( doresize( region.rotate(deg) ) )
	return region.rotate(deg)

def normalize(im):
	# divide im
	regions = imdiv(im)
	if len(regions)!=4:
		regoins = imdiv2(im)

	for k in range(len(regions)):
		regions[k] = dorotate(regions[k])
		regions[k] = purify( docrop(regions[k]) )

	return regions

def train(im):
	global samples
	try:
		samples = pickle.load(open('samples.pk','rb'))
	except:
		samples = {}
		pickle.dump(samples,open('samples.pk','wb'))

	regions = normalize(im)
	for region in regions:
#		(w,h)=region.size
#		region = region.resize((w*.8,h*.8))
		printregion(region)
		smps = loadsamples()
		print match(region,smps).upper()
		print 'enter [0-9a-z] to add to library: '
		ans = raw_input()
		if len(ans) == 1:
			key = (region.size,region.tostring())
			samples[key] = ans[0]
			pickle.dump(samples,open('samples.pk','wb'))

def crackcode(im):
	global samples
	if not samples:
		samples = loadsamples()
	regions = normalize(im)
	s = []
	ans = []
	for r in regions:
		s.append(match(r,samples).upper())
	messup = ['TFY7','FE','38','72YT','CQGR6','G6C','XK','HK','89B','YV','VY']
	for i in range(len(s)):
		for mess in messup:
			if s[i] == mess[0]:
				s[i] = mess
	if len(s) != 4:
		return ['failed']
	else:
		for s1 in s[0]:
			for s2 in s[1]:
				for s3 in s[2]:
					for s4 in s[3]:
						t = s1+s2+s3+s4
						ans.append(t)
	return ans
	

if __name__ == '__main__':
	if len(sys.argv) == 2:
		if sys.argv[1].startswith('train'):
			trainfiles = os.listdir(sys.argv[1])
			trainfiles.sort()
			for trainfile in trainfiles:
				trainfile = sys.argv[1]+'/'+trainfile
				print trainfile
				im = getframe(trainfile)
				train(im)
	else:
		if MODE == 'sample':
			samples = loadsamples()
		else:
			samples = loadttf()
		results = {}
		for i in range(1,121):
			im = getframe('genimg.jpg')
			printframe(im)
			ans = crackcode(im)
			print ans
			ri = raw_input()
			if ri == '':
				continue
			if results.has_key( ri[0] ):
				results[ ri[0] ] += 1
			else:
				results[ ri[0] ] = 1
		print results
