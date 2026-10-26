"""Validate connector geometry and replay the actual final raster. Not aesthetic certification."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

POLICY = 1
SIZE = (1086, 1448)

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def record_path(folder, candidate):
    rel = candidate.resolve().relative_to(folder.resolve()).with_suffix("").as_posix().replace("/", "--")
    return folder / "production/connectors" / (rel + ".json")
def local(folder, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute(): raise ValueError("Connector paths must be topic-relative")
    path = (folder / rel).resolve(); path.relative_to(folder.resolve())
    if not path.is_file(): raise ValueError("Missing connector source: " + rel)
    return path

def point(p):
    return isinstance(p, (list, tuple)) and len(p) == 2 and all(type(v) in (int, float) and math.isfinite(v) for v in p) and 0 <= p[0] < SIZE[0] and 0 <= p[1] < SIZE[1]
def box(b):
    return isinstance(b, list) and len(b) == 4 and point(b[:2]) and point(b[2:]) and b[0] < b[2] and b[1] < b[3]
def inside(p, b, pad=0): return b[0]-pad <= p[0] <= b[2]+pad and b[1]-pad <= p[1] <= b[3]+pad
def edge_distance(p, b):
    if inside(p,b): return min(p[0]-b[0], b[2]-p[0], p[1]-b[1], b[3]-p[1])
    return math.hypot(max(b[0]-p[0],0,p[0]-b[2]), max(b[1]-p[1],0,p[1]-b[3]))
def curve(points, n=80):
    result=[]
    for i in range(n+1):
        t=i/n; u=1-t
        result.append(tuple(u**3*points[0][k]+3*u*u*t*points[1][k]+3*u*t*t*points[2][k]+t**3*points[3][k] for k in (0,1)))
    return result

def intersect(a,b,c,d):
    if max(a[0],b[0]) < min(c[0],d[0]) or max(c[0],d[0]) < min(a[0],b[0]) or max(a[1],b[1]) < min(c[1],d[1]) or max(c[1],d[1]) < min(a[1],b[1]): return False
    def cross(x,y,z): return (y[0]-x[0])*(z[1]-x[1])-(y[1]-x[1])*(z[0]-x[0])
    return cross(a,b,c)*cross(a,b,d) <= 0 and cross(c,d,a)*cross(c,d,b) <= 0

def validate(manifest, plan):
    branches=plan.get("branches",[])
    ids=[g["id"] for g in manifest["groups"]]
    if [b.get("group_id") for b in branches] != ids: raise ValueError("Exactly one ordered connector per map group is required")
    kind=plan.get("kind")
    if kind not in ("cover","practice"): raise ValueError("Connector plan needs kind cover/practice")
    subject=plan.get("subject_box")
    if not box(subject): raise ValueError("Declare the actual main subject_box")
    sources=[subject]
    if "title_box" in plan:
        if kind == "practice" or not box(plan["title_box"]): raise ValueError("Practice cannot anchor to a removed title; invalid title_box")
        sources.append(plan["title_box"])
    width=plan.get("width",4.3); color=plan.get("color",[235,99,88])
    if type(width) not in (int,float) or not 3 <= width <= 5.5: raise ValueError("Connector stroke must remain readable and consistent (3–5.5 px)")
    if not isinstance(color,list) or len(color)!=3 or any(type(c) is not int for c in color) or not (180<=color[0]<=245 and 45<=color[1]<=145 and 35<=color[2]<=140 and color[0]-color[1]>=65):
        raise ValueError("Use a visible coral connector, never white/transparent/invisible strokes")
    target_key="circle_center" if kind=="cover" else "target_center"
    curves=[]; targets=[]; protected=[]
    for b in branches:
        pts=b.get("points",[]); target=b.get(target_key); content=b.get("content_box")
        if len(pts)!=4 or not all(point(p) for p in pts) or not point(target): raise ValueError("Invalid curve points/destination")
        if not box(content): raise ValueError("Each group needs its actual protected text/illustration content_box")
        if not (content[0]-55<=target[0]<=content[2]+10 and content[1]-35<=target[1]<=content[3]+35): raise ValueError("Destination must be beside its own content group")
        if min(edge_distance(pts[0],s) for s in sources)>18: raise ValueError("Connector starts detached from main subject/title")
        if math.dist(pts[-1],target)>28: raise ValueError("Connector ends detached from destination")
        c=curve(pts); direct=math.dist(c[0],c[-1]); length=sum(math.dist(a,z) for a,z in zip(c,c[1:]))
        if direct<35 or length/direct>1.8: raise ValueError("Connector loops or detours excessively")
        if min(x for x,y in c)<min(c[0][0],c[-1][0])-80 or max(x for x,y in c)>max(c[0][0],c[-1][0])+25:
            raise ValueError("Connector makes a wide outer loop")
        dy=c[-1][1]-c[0][1]
        if abs(dy)>25 and any((z[1]-a[1])*(1 if dy>0 else -1)<-0.4 for a,z in zip(c,c[1:])):
            raise ValueError("Connector reverses vertical direction; use a smooth ordered arc")
        if abs(dy)<=25 and max(y for x,y in c)-min(y for x,y in c)>35: raise ValueError("Middle connector waves out of its row")
        for s in sources:
            if any(inside(p,s,-3) for p in c[8:]): raise ValueError("Connector runs through main subject/title")
        curves.append(c); targets.append(target); protected.append(content)
    if any(targets[i+1][1]-targets[i][1]<30 for i in range(len(targets)-1)): raise ValueError("Connector destinations must follow distinct top-to-bottom groups")
    for i,c in enumerate(curves):
        for p in c:
            if any(inside(p,b,width/2+3) for b in protected): raise ValueError("Connector crosses protected text/illustration; route through whitespace")
        for j in range(i):
            other=curves[j]
            for a,b in zip(c,c[1:]):
                for x,y in zip(other,other[1:]):
                    # A short common departure is allowed; crossings farther out are not.
                    if max(math.dist(a,c[0]),math.dist(b,c[0]),math.dist(x,other[0]),math.dist(y,other[0]))<24: continue
                    if intersect(a,b,x,y): raise ValueError("Connectors cross or overlap")
            for a in c:
                if math.dist(a,c[0])<24: continue
                if any(math.dist(x,other[0])>=24 and math.dist(a,x)<width+3 for x in other): raise ValueError("Connectors crowd together outside their departure points")
    return curves

def render(manifest, base, plan):
    curves=validate(manifest,plan)
    if base.size!=SIZE: raise ValueError("Connector base must be 1086x1448")
    base=base.convert("RGBA")
    # Retain old-circle guard for practice derived from a numbered cover.
    for center in plan.get("forbidden_circles",[]):
        if not point(center): raise ValueError("Invalid former-circle center")
        samples=[]
        for radius in (18,20,22):
            for k in range(72):
                a=2*math.pi*k/72; x=round(center[0]+radius*math.cos(a));y=round(center[1]+radius*math.sin(a))
                if 0<=x<SIZE[0] and 0<=y<SIZE[1]: samples.append(max(base.getpixel((x,y))[:3])<115)
        if samples and sum(samples)/len(samples)>.15: raise ValueError("Practice base still contains an old circle")
    scale=3; layer=Image.new("RGBA",(SIZE[0]*scale,SIZE[1]*scale));draw=ImageDraw.Draw(layer)
    for b in plan["branches"]:
        pts=curve(b["points"],200)
        draw.line([(round(x*scale),round(y*scale)) for x,y in pts],fill=tuple(plan.get("color",[235,99,88]))+(245,),width=round(plan.get("width",4.3)*scale),joint="curve")
    layer=layer.resize(SIZE,Image.Resampling.LANCZOS)
    result=Image.alpha_composite(base,layer).convert("RGB")
    for c in curves:
        visible=0; checked=0
        for x,y in c[6:-3]:
            p=(round(x),round(y));before=base.getpixel(p);after=result.getpixel(p)
            checked+=1;visible+=max(abs(before[k]-after[k]) for k in range(3))>35
        if not checked or visible/checked<.80: raise ValueError("Connector has insufficient visible new pixels; base may already contain lines or low contrast")
    return result

def write_record(folder, candidate, base, plan_file):
    sources={p.resolve().relative_to(folder.resolve()).as_posix():digest(p) for p in [folder/"manifest.json",base,plan_file]}
    value={"policy":POLICY,"candidate":candidate.resolve().relative_to(folder.resolve()).as_posix(),"candidate_sha256":digest(candidate),"base":base.resolve().relative_to(folder.resolve()).as_posix(),"plan":plan_file.resolve().relative_to(folder.resolve()).as_posix(),"sources_sha256":sources,"renderer_sha256":digest(Path(__file__))}
    path=record_path(folder,candidate);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")
    return path

def check(folder,candidate,kind):
    if kind not in ("cover","practice"): return []
    try:
        folder=folder.resolve();candidate=candidate.resolve()
        data=json.loads(record_path(folder,candidate).read_text(encoding="utf-8"))
        if data.get("policy")!=POLICY or data.get("candidate")!=candidate.relative_to(folder).as_posix() or data.get("candidate_sha256")!=digest(candidate) or data.get("renderer_sha256")!=digest(Path(__file__)):
            raise ValueError("Connector binding/renderer changed")
        base=local(folder,data["base"]);pf=local(folder,data["plan"])
        expected={p.relative_to(folder).as_posix():digest(p) for p in [folder/"manifest.json",base,pf]}
        if expected!=data["sources_sha256"]: raise ValueError("Connector base/plan/manifest changed")
        manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8-sig"));plan=json.loads(pf.read_text(encoding="utf-8-sig"))
        if plan.get("kind")!=kind: raise ValueError("Cover/practice connector plan mismatch")
        with Image.open(base) as im: replay=render(manifest,im,plan)
        with Image.open(candidate) as im:
            if im.size!=SIZE or ImageChops.difference(replay,im.convert("RGB")).getbbox(): raise ValueError("Final pixels differ from the validated connected raster")
    except (OSError,ValueError,KeyError,TypeError,IndexError,AttributeError) as exc:
        return [candidate.name+": connector check failed: "+str(exc)]
    return []
