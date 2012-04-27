import Image, ImageFont, ImageDraw
import pickle

DURATION = 1000
DIAMETER = 20
COLORDIFF = 10
TEXTCOLOR = (128,128,128)
BACKGROUND = (255,255,255)
MODE = 'sample'
samples = None

class Handle:
    
    def getImage(self,fname):
        im = Image.open(fname)
        return im
    
    def density(self,region):
        frame = region.getdata()
        (w,h) = region.size
        area_all = w*h
        area = 0
        for i in range(h):
            for j in range(w):
                if frame[i*w+j] != BACKGROUND and frame[i*w+j] != (0,0,0):
                    area += 1
        return 1.0*area/area_all    
    
    def purify(self,region):
        frame = region.getdata()
        (w,h)=region.size
        self.printregion(region)
        for i in range(h):
            for j in range(w):
                if frame[i*w+j] < (150,150,150):
                    region.putpixel( (j,i), TEXTCOLOR )
                else:
                    region.putpixel( (j,i), BACKGROUND )
        return region
        
    def imdiv(self,im):
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
    
    def getcrop(self, region):
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
    
    def docrop(self, region):
        croppos = self.getcrop(region)
        newregion = region.crop(croppos)
        return newregion
    
    def dorotate(self,region):
    #   printregion(region)
        deg = 0
        maxdens = 0
        for i in range(-30,31):
            dens = self.density(self.docrop(region.rotate(i)))
            if dens > maxdens:
                deg = i
                maxdens = dens
    #   printregion( doresize( region.rotate(deg) ) )
        return region.rotate(deg)
    
    def crackcode(self,regions):
        global samples
        if not samples:
            samples = self.loadsamples()
        #regions = normalize(im)
        s = []
        ans = []
        for r in regions:
            s.append(self.match(r,samples).upper())
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
    
    def match(self,region,samples):
        if samples == {}:
            return None
        dists = []
        for (k,v) in samples.items():
            dists.append( (self.distance(region,k),v) )
        dists.sort()
        if MODE == 'sample':
            return dists[0][1]
        else:
            i = 0
            while dists[i][1] in ['H','I']:
                i += 1
            return dists[i][1]
        
    def distance(self,r1,r2):
        den1 = self.density(r1)
        den2 = self.density(r2)
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
        
    def loadsamples(self):
        pks = pickle.load(open('samples.pk','rb'))
        samples = {}
        for (pk,v) in pks.items():
            im = Image.new('RGB',pk[0])
            r = im.crop((0,0,pk[0][0],pk[0][1]))
            r.fromstring(pk[1])
            samples[r] = v
        return samples
        
    def loadttf(self):
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
            #self.printregion( regions[i] )
    
        kv = {}
        for i in range(len(regions)):
            kv[regions[i]] = regionsv[i]
    
        return kv
    
    def imdiv2(self,im):
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
    
    def main(self):
        im = self.getImage('genimg.jpg')
        #im = self.purify(im)
        
        regions = self.imdiv(im)
        if len(regions)!=4:
            regoins = self.imdiv2(im)
        self.purify(regions[0])
        self.dorotate(regions[0])
        self.printregion(regions[0])
        print self.crackcode(regions)
    
    def printregion(self,region):
        frame = region.getdata()
        (w,h)=region.size
        f = file('testCode.txt','w')
        for i in range(h):
            for j in range(w):
                if frame[i*w+j] != BACKGROUND:
                    f.write('*')
                else:
                    f.write(' ')
            f.write('\n')
        f.close()

Handle().main()
