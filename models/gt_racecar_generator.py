"""Procedural, editable 3D GT racing car. Run: python gt_racecar_generator.py
Dependencies: numpy, trimesh. Coordinates in authoring are Z-up; exported GLB uses Y-up.
Original concept geometry. No copyrighted manufacturer logos.
"""
from collections import defaultdict
from pathlib import Path
import math
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

OUT=Path(__file__).with_name('gt_racecar_3d.glb')
parts=defaultdict(list)
COLORS={
'body':(31,35,40,255),'carbon':(13,16,21,255),'carbon2':(23,26,31,255),
'carbonlight':(42,46,52,255),'red':(190,24,32,255),'brightred':(238,40,46,255),
'glass':(20,32,43,255),'glass_light':(45,65,76,255),'headlight':(196,237,255,255),
'rearlight':(240,17,21,255),'metal':(112,118,125,255),'wheel':(30,32,37,255),
'rim':(76,81,90,255),'rubber':(12,13,16,255),'brake':(122,126,130,255),
'white':(238,237,230,255),'gold':(216,169,69,255),'black':(6,7,9,255)}

def add(mesh, mat):
    if mesh is None or len(mesh.faces)==0:return
    if not isinstance(mesh, trimesh.Trimesh): raise TypeError(type(mesh))
    parts[mat].append(mesh)

def box(mat,ext,center,rot_y=0):
    m=trimesh.creation.box(extents=ext)
    if rot_y: m.apply_transform(trimesh.transformations.rotation_matrix(rot_y,[0,1,0]))
    m.apply_translation(center)
    add(m,mat)

def triangle_mesh(mat, verts, faces, double=True):
    verts=np.array(verts,float);faces=np.array(faces,int)
    if double: faces=np.vstack([faces,faces[:,::-1]])
    add(trimesh.Trimesh(vertices=verts,faces=faces,process=False),mat)

def quad(mat,a,b,c,d,double=True):
    triangle_mesh(mat,[a,b,c,d],[[0,1,2],[0,2,3]],double)

def rod(mat,p1,p2,r=0.018,n=10):
    p1=np.asarray(p1,dtype=float);p2=np.asarray(p2,dtype=float)
    vec=p2-p1; length=float(np.linalg.norm(vec))
    if length<1e-7:return
    m=trimesh.creation.cylinder(radius=r,height=length,sections=n)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],vec))
    m.apply_translation((p1+p2)*.5)
    add(m,mat)

def ring_y(mat,xc,yc,zc,r_inner,r_outer,width=0.035,sections=48):
    vs=[]
    for yy,rr in [(yc-width/2,r_inner),(yc-width/2,r_outer),
                   (yc+width/2,r_outer),(yc+width/2,r_inner)]:
        for i in range(sections):
            t=2*math.pi*i/sections
            vs.append([xc+rr*math.cos(t),yy,zc+rr*math.sin(t)])
    fs=[]
    for j in range(4):
        nj=(j+1)%4
        for i in range(sections):
            k=(i+1)%sections
            a=j*sections+i;b=j*sections+k;c=nj*sections+k;d=nj*sections+i
            fs.extend([[a,b,c],[a,c,d]])
    triangle_mesh(mat,vs,fs,double=False)

def arc_arch(xc,side):
    y=side*1.012; zc=.39;r=.425
    for i in range(25):
        a=-.12+(math.pi+.24)*i/25
        b=-.12+(math.pi+.24)*(i+1)/25
        rod('carbon', [xc+r*math.cos(a),y,zc+r*math.sin(a)],
                       [xc+r*math.cos(b),y,zc+r*math.sin(b)], .026, 8)

def tire(xc,yc,zc):
    sections=48
    profile=[(.251,-.17),(.314,-.168),(.356,-.15),(.391,-.125),(.398,-.07),
             (.398,.07),(.391,.125),(.356,.15),(.314,.168),(.251,.17)]
    vs=[]
    for r,dy in profile:
        for j in range(sections):
            a=2*math.pi*j/sections
            vs.append([xc+r*math.cos(a),yc+dy,zc+r*math.sin(a)])
    fs=[]
    for k in range(len(profile)):
        nk=(k+1)%len(profile)
        for j in range(sections):
            j2=(j+1)%sections
            a=k*sections+j;b=k*sections+j2;c=nk*sections+j2;d=nk*sections+j
            fs.extend([[a,b,c],[a,c,d]])
    triangle_mesh('rubber',vs,fs,False)
    for dy in (-.085,.085):ring_y('black',xc,yc+dy,zc,.394,.402,.007,48)

def wheel(xc,side):
    yc=side*.92;zc=.39
    tire(xc,yc,zc)
    outside=yc+side*.183
    ring_y('metal',xc,outside-side*.023,zc,.22,.256,.025,48)
    ring_y('rim',xc,outside-side*.003,zc,.205,.247,.028,48)
    ring_y('carbonlight',xc,outside-side*.017,zc,.07,.090,.06,32)
    ring_y('brake',xc,outside-side*.092,zc,.045,.225,.021,48)
    for j in range(10):
        a=2*math.pi*j/10 + .08
        cx=xc+.146*math.cos(a); zz=zc+.146*math.sin(a)
        box('wheel',[.170,.028,.033],[cx,outside-side*.003,zz],-a)
    ring_y('metal',xc,outside+side*.01,zc,.0,.061,.035,32)
    for j in range(5):
        a=j*2*math.pi/5
        rod('gold',[xc+.074*math.cos(a),outside+side*.014,zc+.074*math.sin(a)],
                   [xc+.074*math.cos(a),outside+side*.027,zc+.074*math.sin(a)],.009,8)
    box('red',[.088,.044,.145],[xc+.183,outside-side*.112,zc+.088])
    arc_arch(xc,side)

stations=[(-2.50,.74,.76,.38),(-2.29,.88,.80,.38),(-1.89,.965,.85,.38),
          (-1.36,.985,.88,.40),(-.89,.90,.84,.41),(-.35,.87,.83,.42),
          (.28,.885,.84,.42),(.86,.978,.88,.41),(1.36,1.005,.84,.38),
          (1.90,.94,.76,.36),(2.35,.89,.69,.34),(2.53,.80,.64,.33)]

def cross_ring(x,w,top,bot):
    return [(x,0,top+.006), (x,.50*w,top-.006),(x,.82*w,top-.085),
            (x,.99*w,top-.19),(x,w,bot+.14),(x,.83*w,bot),
            (x,0,bot+.01),(x,-.83*w,bot),(x,-w,bot+.14),
            (x,-.99*w,top-.19),(x,-.82*w,top-.085),(x,-.50*w,top-.006)]
verts=[v for st in stations for v in cross_ring(*st)]
faces=[];n=12
for k in range(len(stations)-1):
    for j in range(n):
        a=k*n+j;b=k*n+(j+1)%n;c=(k+1)*n+(j+1)%n;d=(k+1)*n+j
        faces.extend([[a,b,c],[a,c,d]])
for j in range(1,n-1):
    faces.append([0,j+1,j]);i=(len(stations)-1)*n;faces.append([i,i+j,i+j+1])
triangle_mesh('body',verts,faces,double=False)

box('carbon',[.71,1.96,.062],[2.34,0,.319])
box('carbon2',[.12,2.09,.036],[2.61,0,.301])
box('carbon',[.62,1.88,.035],[-2.27,0,.317])
for yy in (-.78,-.47,-.17,.17,.47,.78):
    box('carbonlight',[.43,.025,.13],[-2.39,yy,.318])
for s in (-1,1):
    box('carbon',[3.63,.125,.107],[-.14,s*.925,.345])
    box('red',[2.04,.018,.022],[-.22,s*.999,.405])
    quad('carbonlight',[2.37,s*.80,.418],[2.49,s*1.05,.413],
                       [2.16,s*1.105,.353],[2.11,s*.965,.352])

cab=[(-1.19,.68,.88,.745),(-.72,.49,1.252,.745),
     (.21,.475,1.311,.745),(.85,.705,.92,.745)]
canopyv=[]
for x,w,zt,zb in cab:
    canopyv.extend([[x,-.715,zb],[x,-w,zt],[x,w,zt],[x,.715,zb]])
canopyf=[]
for i in range(len(cab)-1):
    for j in range(3):
        a=i*4+j;b=a+1;c=(i+1)*4+j+1;d=(i+1)*4+j
        canopyf.extend([[a,b,c],[a,c,d]])
for j in range(1,3):canopyf.append([j,0,j+1])
k=(len(cab)-1)*4
for j in range(1,3):canopyf.append([k,k+j,k+j+1])
triangle_mesh('glass',canopyv,canopyf,True)
quad('carbon',[ -.72,-.49,1.261],[.20,-.475,1.319],[.20,.475,1.319],[-.72,.49,1.261])
quad('glass_light',[.27,-.43,1.277],[.77,-.655,.959],[.77,.655,.959],[.27,.43,1.277])
for s in (-1,1):
    rod('carbonlight',[.22,s*.478,1.321],[.85,s*.711,.929],.020)
    rod('carbonlight',[-.71,s*.495,1.270],[-1.20,s*.704,.890],.025)
    rod('carbonlight',[-.71,s*.495,1.270],[.22,s*.478,1.321],.015)
    rod('carbonlight',[-.27,s*.496,1.286],[-.21,s*.715,.751],.017)
    rod('glass_light',[-.70,s*.69,.822],[.68,s*.69,.822],.009)
    rod('carbonlight',[.59,s*.70,.885],[.78,s*.89,.970],.022)
    box('carbonlight',[.19,.143,.086],[.79,s*.925,.984])
    box('red',[.115,.018,.014],[.81,s*1.001,1.000])

box('carbon2',[.48,.36,.075],[-.22,0,1.330])
quad('carbonlight',[-.10,-.12,1.375],[-.10,.12,1.375],[.03,.11,1.412],[.03,-.11,1.412])
for y in (-.57,-.43,-.29,.29,.43,.57):
    box('carbon',[.59,.057,.011],[-1.62,y,.856])
for s in (-1,1):
    quad('carbon',[1.10,s*.30,.851],[1.64,s*.39,.801],
                  [1.77,s*.50,.765],[1.18,s*.44,.853])
    for j in range(4):
        x=1.27+j*.115
        rod('carbonlight',[x,s*.31,.863-j*.009],[x+.07,s*.46,.842-j*.011],.008)

for s in (-1,1):
    ys=s*.43
    quad('red',[.94,ys-.065,.883],[.94,ys+.065,.883],
               [1.39,ys+.065,.846],[1.39,ys-.065,.846])
    quad('red',[1.39,ys-.07,.850],[1.39,ys+.07,.850],
               [1.92,ys+.062,.768],[1.92,ys-.062,.768])
    quad('brightred',[1.92,ys-.062,.773],[1.92,ys+.062,.773],
                     [2.39,ys+.048,.700],[2.39,ys-.048,.700])
    quad('red',[-.67,ys-.056,1.280],[-.67,ys+.056,1.280],
               [.16,ys+.056,1.332],[.16,ys-.056,1.332])

for s in (-1,1):
    box('carbonlight',[.068,.062,.42],[-2.06,s*.52,1.292],rot_y=-.12)
    rod('metal',[-2.11,s*.52,1.105],[-2.19,s*.52,1.495],.018)
profile=[(-2.47,1.545),(-2.35,1.585),(-2.07,1.592),(-1.96,1.555),(-2.03,1.525),(-2.35,1.518)]
wingv=[]
for y in (-1.105,1.105):wingv.extend([[x,y,z] for x,z in profile])
wingf=[];npf=len(profile)
for j in range(npf):
    k=(j+1)%npf;a=j;b=k;c=npf+k;d=npf+j
    wingf.extend([[a,b,c],[a,c,d]])
for j in range(1,npf-1):wingf.extend([[0,j,j+1],[npf,npf+j+1,npf+j]])
triangle_mesh('carbon',wingv,wingf,False)
for s in (-1,1):
    quad('carbon2',[-2.54,s*1.112,1.48],[-2.54,s*1.112,1.72],
                  [-1.96,s*1.112,1.675],[-1.98,s*1.112,1.51])
    quad('red',[-2.54,s*1.118,1.51],[-2.54,s*1.118,1.71],
               [-2.475,s*1.118,1.706],[-2.475,s*1.118,1.51])

quad('black',[2.524,-.57,.382],[2.533,-.57,.556],
             [2.533,.57,.556],[2.524,.57,.382])
for yy in np.linspace(-.52,.52,12):
    rod('carbonlight',[2.543,yy,.395],[2.543,yy,.555],.008)
for s in (-1,1):
    quad('headlight',[2.18,s*.52,.713],[2.38,s*.74,.643],
                     [2.49,s*.795,.586],[2.31,s*.57,.660])
    rod('headlight',[2.17,s*.50,.716],[2.43,s*.75,.632],.013)
    quad('black',[2.426,s*.79,.40],[2.41,s*.927,.473],
                 [2.27,s*.924,.546],[2.24,s*.78,.469])
    rod('red',[2.57,s*.38,.370],[2.57,s*.38,.435],.013)

for s in (-1,1):
    quad('rearlight',[-2.505,s*.39,.705],[-2.504,s*.77,.699],
                     [-2.506,s*.77,.65],[-2.506,s*.39,.651])
    ring_y('metal',-2.52,s*.53,.46,.051,.074,.06,24)
for yy in (-.35,.35):
    rod('black',[-2.56,yy,.408],[-2.44,yy,.408],.062,16)
    rod('metal',[-2.573,yy,.408],[-2.56,yy,.408],.055,16)

for s in (-1,1):
    y=s*.905
    quad('red',[-.92,y,.495],[-.73,y,.495],[-.16,y,.825],[-.35,y,.825])
    bx=-.46; bz=.685
    for xx in (bx-.079,bx+.079):box('white',[.029,.012,.197],[xx,y+s*.015,bz])
    for zz in (bz-.095,bz+.095):box('white',[.174,.012,.025],[bx,y+s*.015,zz])
    box('white',[.038,.013,.216],[-.20,y+s*.015,bz])
    box('white',[.115,.013,.024],[-.21,y+s*.015,bz-.10])
    quad('black',[-1.20,s*.962,.60],[-1.73,s*.972,.64],
                 [-1.65,s*.982,.814],[-1.23,s*.973,.800])
    for j in range(3):
        x=-1.35-.085*j
        rod('carbonlight',[x,s*.993,.628],[x,s*.994,.764],.009)
    ring_y('metal',-.78,s*.93,.796,.035,.049,.008,28)

for x in (-1.58,1.57):
    for side in (-1,1): wheel(x,side)

scene=trimesh.Scene()
for key, meshes in parts.items():
    merged=trimesh.util.concatenate(meshes)
    r,g,b,a=COLORS[key]
    factor=[r/255,g/255,b/255,a/255]
    metallic=.65 if key in ('body','metal','rim','brake','gold','wheel') else .13
    roughness=.27 if key in ('body','red','brightred','glass','glass_light') else .66
    if key in ('rubber','black'):roughness=.93;metallic=0
    if key in ('headlight','rearlight'):roughness=.16;metallic=0
    emission=[v*.55 for v in factor[:3]] if key in ('headlight','rearlight') else None
    mat=PBRMaterial(name=key,baseColorFactor=factor,metallicFactor=metallic,
                    roughnessFactor=roughness,emissiveFactor=emission, doubleSided=True)
    merged.visual=trimesh.visual.TextureVisuals(material=mat)
    merged.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    scene.add_geometry(merged,geom_name=key,node_name=key)
scene.export(str(OUT),file_type='glb')
print(f'Saved: {OUT} ({OUT.stat().st_size:,} bytes)')
print('Materials:',len(parts),'Source meshes:',sum(map(len,parts.values())),
      'Triangles:',sum(len(mesh.faces) for group in parts.values() for mesh in group))
check=trimesh.load(str(OUT),force='scene')
print('Verified:',len(check.geometry),'meshes',sum(len(m.faces) for m in check.geometry.values()),'triangles')
