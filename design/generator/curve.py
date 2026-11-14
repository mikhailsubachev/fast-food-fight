import math
CTRL=[(-4.5,2.6),(-1.8,2.45),(0.6,2.25),(3.0,2.6),(5.6,2.35),(7.6,2.7),(8.5,3.7),(7.9,4.8),(6.2,5.15),(4.2,4.85),(2.6,5.25),(2.1,6.3),(3.0,7.3),(5.0,7.65),(7.4,7.35),(9.9,7.5)]
def catmull(pts,n=14):
    out=[]
    P=[pts[0]]+pts+[pts[-1]]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        for k in range(n):
            t=k/n; t2=t*t; t3=t2*t
            out.append(tuple(0.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3) for j in (0,1)))
    out.append(pts[-1]); return out
CENTER=catmull(CTRL)
def halfw(i): return 0.52+0.07*math.sin(i*0.37)+0.04*math.sin(i*1.13+1)
def edges(scale=1.0):
    L=[];R=[]
    for i,p in enumerate(CENTER):
        a=CENTER[max(0,i-1)]; b=CENTER[min(len(CENTER)-1,i+1)]
        dx,dz=b[0]-a[0],b[1]-a[1]; l=math.hypot(dx,dz) or 1
        nx,nz=-dz/l,dx/l; w=halfw(i)*scale
        L.append((p[0]+nx*w,p[1]+nz*w)); R.append((p[0]-nx*w,p[1]-nz*w))
    return L,R
def nearest(x,z):
    return min(CENTER,key=lambda p:(p[0]-x)**2+(p[1]-z)**2)
def dist(x,z):
    p=nearest(x,z); return math.hypot(p[0]-x,p[1]-z)
