"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)






def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    out=parser.parse_args().out;out.mkdir(parents=True,exist_ok=True)
    d=Drawing((0,-2.7,13.6,2.0))
    for key,x,label in [('a',1.7,'$S_{t_1}$\nearlier live state'),('b',6.8,'$S_{t_2}$\nlater live state'),('c',11.9,'$S_T$\nchallenge state')]:
        d.box(key,x,1,2.8,.9,label,size=8.5)
    d.edge('a','b','e','w');d.edge('b','c','e','w')
    d.text(4.25,1.35,'update',size=8);d.text(9.35,1.35,'update',size=8)
    for key,x,label in [('la',1.7,'$Z[I_1]$'),('lb',6.8,'$Z[I_2]$'),('target',11.9,'$Z=g(S_T)$')]:
        d.box(key,x,-1.1,2.8,.7,label,size=8.5)
    for a,b in [('a','la'),('b','lb'),('c','target')]:d.edge(a,b)
    d.text(3.15,0,'predict, then\nproject onto $I_1$',size=7.5,ha='left')
    d.text(8.25,0,'predict, then\nproject onto $I_2$',size=7.5,ha='left')
    d.edge('la','target','s','s',dashed=True,via=((1.7,-2.25),(11.9,-2.25)))
    d.line([d.point('lb','s'),(6.8,-2.25)],dashed=True)
    d.save(out,'predictable-target')
    d=Drawing((-.3,-3.6,14.6,3.0))
    d.box('old',1.1,1,2,.8,'$C_{j-1}$\nretained',size=8)
    d.box('fresh',1.1,-.4,2,.8,'$X_j$\npost-exposure',size=8)
    d.box('seed',1.1,-1.8,2,.8,'$D_j,\\mathsf{sid}_j$\npublic',size=8)
    d.box('ext',5.1,-.4,3,.9,'strong quantum-proof\nextractor',size=8)
    d.box('new',9.1,.4,2,.8,'$C_j$\nquarantined',size=8)
    d.box('coins',9.1,-1.2,2,.8,'$R_j$\nkey coins',size=8)
    d.box('key',12.7,-1.2,2.7,.9,'$\\mathsf{Key}$ and\nbase session',size=8)
    for a in ['old','fresh','seed']:d.edge(a,'ext','e','w')
    d.edge('ext','new','e','w');d.edge('ext','coins','e','w');d.edge('coins','key','e','w')
    d.edge('new','old','n','n',dashed=True,via=((9.1,2.1),(1.1,2.1)))
    d.text(5.1,2.6,'$W_j$: support $J_j$ before next update',size=8)
    d.arrow(d.point('key','s'),(12.7,-2.2),dashed=True)
    d.text(11.5,-2.85,'$Z_j$: causal factor $\\Gamma_j$\nterminal release of $S_j$ after decision',size=7.5)
    d.save(out,'entropy-ratchet')
if __name__=='__main__':main()
