"""Validated geometry diagram builders. Coordinates and labels are tied to problem data."""
from __future__ import annotations
import math

def _geom(points, segments, caption, **extra):
    d={"type":"geometry","points":points,"segments":segments,"labels":list(points),"caption":caption}
    d.update(extra); return d

def triangle_3_4_5(a=3,b=4,labels=("A","B","C")):
    # Right angle at A; AB=b, AC=a, BC=sqrt(a²+b²).
    c=math.hypot(a,b)
    d=_geom({labels[0]:[0,0],labels[1]:[b,0],labels[2]:[0,a]},
      [[labels[0],labels[1]],[labels[1],labels[2]],[labels[2],labels[0]]],
      "Tam giác vuông tại A; hai cạnh góc vuông theo dữ kiện.", right_angle=labels[0],
      measurements=[{"from":labels[0],"to":labels[1],"text":str(b)}, {"from":labels[0],"to":labels[2],"text":str(a)}, {"from":labels[1],"to":labels[2],"text":str(int(c) if c.is_integer() else round(c,2))}])
    return d

def triangle_from_sides(a,b,c,labels=("A","B","C")):
    """Triangle with AB=c, AC=b, BC=a; reject impossible side triples."""
    if min(a,b,c)<=0 or max(a,b,c)>=sum(sorted((a,b,c))[:2]): raise ValueError("Invalid triangle side lengths")
    x=(b*b+c*c-a*a)/(2*c); y2=b*b-x*x
    if y2 <= 1e-9: raise ValueError("Degenerate triangle")
    y=math.sqrt(y2); A,B,C=labels
    return _geom({A:[0,0],B:[c,0],C:[x,y]},[[A,B],[B,C],[C,A]],"Tam giác được dựng từ ba cạnh thỏa mãn bất đẳng thức tam giác.",
      measurements=[{"from":A,"to":B,"text":str(c)},{"from":A,"to":C,"text":str(b)},{"from":B,"to":C,"text":str(a)}])

def rectangle(width,height,labels=("A","B","C","D")):
    if width<=0 or height<=0: raise ValueError("Rectangle dimensions must be positive")
    A,B,C,D=labels
    return _geom({A:[0,0],B:[width,0],C:[width,height],D:[0,height]},[[A,B],[B,C],[C,D],[D,A]],
      "Hình chữ nhật dựng theo đúng chiều dài và chiều rộng, giữ nguyên tỉ lệ kích thước.", right_angles=[A,B,C,D],
      aspect_ratio={"width": float(width), "height": float(height), "ratio": float(width)/float(height)},
      constraints=[{"type":"rectangle","vertices":[A,B,C,D]}, {"type":"side_ratio","from":A,"to":B,"other_from":B,"other_to":C,"ratio":float(width)/float(height)}],
      measurements=[{"from":A,"to":B,"text":str(width)},{"from":B,"to":C,"text":str(height)}])

def square(side,labels=("A","B","C","D")):
    return rectangle(side,side,labels)

def coordinate_rectangle(x1,y1,x2,y2):
    if x1==x2 or y1==y2: raise ValueError("Rectangle must have positive width and height")
    A,B,C,D="A","B","C","D"
    return _geom({A:[x1,y1],B:[x2,y1],C:[x2,y2],D:[x1,y2]},[[A,B],[B,C],[C,D],[D,A]],
      "Khu đất hình chữ nhật trên mặt phẳng tọa độ.", axes=True, right_angles=[A,B,C,D])

def circle(radius,center=(0,0),label="O",show_measurement=True):
    if radius<=0: raise ValueError("Circle radius must be positive")
    points={label:[center[0],center[1]],"R":[center[0]+radius,center[1]]}
    segments=[[label,"R"]] if show_measurement else []
    measurements=[{"from":label,"to":"R","text":str(radius)}] if show_measurement else []
    return {"type":"geometry","points":points,"segments":segments,
      "circles":[{"center":[center[0],center[1]],"radius":radius}],"labels":[label],"hide_labels":[] if show_measurement else ["R"],"measurements":measurements,"caption":"Đường tròn có bán kính đúng theo dữ kiện."}

def inscribed_rectangle(a,b,radius,labels=("A","B","C","D")):
    """Rectangle with half-width a and half-height b on a circle of radius sqrt(a²+b²)."""
    expected=math.hypot(a,b)
    if a<=0 or b<=0 or not math.isclose(expected,radius,rel_tol=1e-8,abs_tol=1e-8):
        raise ValueError("Inscribed rectangle requires radius²=a²+b²")
    A,B,C,D=labels; O="O"
    return _geom({A:[-a,-b],B:[a,-b],C:[a,b],D:[-a,b],O:[0,0]},
      [[A,B],[B,C],[C,D],[D,A],[A,C],[B,D]],
      "Hình chữ nhật nội tiếp; hai đường chéo là đường kính và bán kính khớp kích thước.",
      circles=[{"center":[0,0],"radius":radius}], circle_vertices=[A,B,C,D], measurements=[{"from":A,"to":B,"text":str(2*a)},{"from":B,"to":C,"text":str(2*b)},{"from":A,"to":C,"text":str(2*radius)}])

def inscribed_right_triangle(a,b,c,labels=("A","B","C")):
    """Right triangle with AC=a, BC=b, AB=c as diameter; requires a²+b²=c²."""
    if min(a,b,c)<=0 or not math.isclose(a*a+b*b,c*c,rel_tol=1e-8,abs_tol=1e-8):
        raise ValueError("Right triangle requires a²+b²=c²")
    # A=(-c/2,0), B=(c/2,0), C lies above AB; distances AC=a, BC=b.
    x=(a*a-b*b)/(2*c); y=math.sqrt(max(0,a*a-(x+c/2)**2))
    A,B,C=labels
    return _geom({A:[-c/2,0],B:[c/2,0],C:[x,y],"O":[0,0]},[[A,B],[B,C],[C,A]],
      "Tam giác vuông nội tiếp; cạnh AB là đường kính, góc C vuông.", right_angle=C, circles=[{"center":[0,0],"radius":c/2}],
      circle_vertices=[A,B,C], measurements=[{"from":A,"to":C,"text":str(a)},{"from":B,"to":C,"text":str(b)},{"from":A,"to":B,"text":str(c)}])

def polygon(points,caption="Đa giác hình học"):
    labels=list(points)
    if len(labels)<3: raise ValueError("Polygon needs at least three vertices")
    return _geom(points,[[labels[i],labels[(i+1)%len(labels)]] for i in range(len(labels))],caption)

def parallelogram(base,height,offset,labels=("A","B","C","D")):
    if base<=0 or height<=0 or offset<=0 or offset>=base: raise ValueError("Invalid parallelogram dimensions")
    A,B,C,D=labels
    return _geom({A:[0,0],B:[base,0],C:[base+offset,height],D:[offset,height]},[[A,B],[B,C],[C,D],[D,A]],"Hình bình hành dựng theo đáy, chiều cao và độ lệch.")

def trapezoid(bottom,top,height,offset=0,labels=("A","B","C","D")):
    if min(bottom,top,height)<=0: raise ValueError("Invalid trapezoid dimensions")
    A,B,C,D=labels
    return _geom({A:[0,0],B:[bottom,0],C:[offset+top,height],D:[offset,height]},[[A,B],[B,C],[C,D],[D,A]],"Hình thang với hai đáy song song.")

def triangle_with_base_height(base,height,labels=("A","B","C")):
    if base<=0 or height<=0: raise ValueError("Triangle dimensions must be positive")
    A,B,C=labels; foot=base*0.62
    return _geom({A:[0,0],B:[base,0],C:[foot,height],"H":[foot,0]},[[C,"H"],["H",B],[A,"H"],[B,C],[C,A]],
      "Tam giác có đáy và đường cao CH vuông góc với AB; kích thước được dựng theo dữ kiện.", right_angle="H", altitudes=[["C","H"]], dashed_segments=[["C","H"]], measurements=[{"from":A,"to":B,"text":str(base)},{"from":"H","to":C,"text":str(height)}])

def circle_with_tangent(radius,center=(0,0),center_label="O",show_measurement=True):
    h,k=center; T=(h+radius,k); P=(h+radius,k+radius*0.8); O=center_label
    return _geom({O:[h,k],"T":[T[0],T[1]],"P":[P[0],P[1]]},[[O,"T"],["T","P"]],
      "Tiếp tuyến vuông góc với bán kính tại tiếp điểm.", circles=[{"center":[h,k],"radius":radius}], right_angle="T", measurements=[{"from":O,"to":"T","text":str(radius)}] if show_measurement else [])

def inscribed_square(radius,labels=("A","B","C","D")):
    half=radius/math.sqrt(2)
    return inscribed_rectangle(half,half,radius,labels)

def regular_polygon(sides,radius,center=(0,0),labels=None):
    if sides<3 or radius<=0: raise ValueError("Regular polygon needs at least 3 sides and positive radius")
    names=labels or tuple(chr(65+i) for i in range(sides))
    if len(names)!=sides: raise ValueError("Label count must match side count")
    points={name:[center[0]+radius*math.cos(2*math.pi*i/sides),center[1]+radius*math.sin(2*math.pi*i/sides)] for i,name in enumerate(names)}
    return _geom(points,[[names[i],names[(i+1)%sides]] for i in range(sides)],f"Đa giác đều {sides} cạnh, bán kính ngoại tiếp {radius:g}.",circles=[{"center":[center[0],center[1]],"radius":radius}])

def rhombus(diagonal1,diagonal2,labels=("A","B","C","D")):
    if min(diagonal1,diagonal2)<=0: raise ValueError("Rhombus diagonals must be positive")
    A,B,C,D=labels; x=diagonal1/2; y=diagonal2/2
    return _geom({A:[-x,0],B:[0,y],C:[x,0],D:[0,-y]},[[A,B],[B,C],[C,D],[D,A],[A,C],[B,D]],"Hình thoi với hai đường chéo vuông góc và cắt nhau tại trung điểm.")

def kite(diagonal1,diagonal2,offset=0,labels=("A","B","C","D")):
    if min(diagonal1,diagonal2)<=0 or abs(offset)>=diagonal1/2: raise ValueError("Invalid kite dimensions")
    A,B,C,D=labels; x=diagonal1/2; y=diagonal2/2
    return _geom({A:[0,y],B:[x,0],C:[0,-y],D:[-x+offset,0]},[[A,B],[B,C],[C,D],[D,A]],"Hình diều đối xứng theo đường chéo đứng.")

def pyramid_projection(labels=("S","A","B","C","D")):
    S,A,B,C,D=labels
    return _geom({S:[0,3],A:[-2,0],B:[0.2,-0.8],C:[2,0],D:[-0.2,0.8]},[[A,B],[B,C],[C,D],[D,A],[S,A],[S,B],[S,C],[S,D]],"Hình chiếu phẳng của hình chóp đáy tứ giác; nét khuất có thể được đánh dấu riêng.",hidden_segments=[[S,D]])

def triangular_prism_projection(labels=("A","B","C","A1","B1","C1")):
    A,B,C,A1,B1,C1=labels
    points={A:[-2,0],B:[0,-1],C:[-0.8,1.6],A1:[0,1],B1:[2,0],C1:[1.2,2.6]}
    return _geom(points,[[A,B],[B,C],[C,A],[A1,B1],[B1,C1],[C1,A1],[A,A1],[B,B1],[C,C1]],"Hình lăng trụ tam giác trong phép chiếu phẳng.")


def right_triangle_with_altitude(a, b, labels=("A", "B", "C")):
    """Right triangle ABC with right angle at A and altitude AH to hypotenuse BC.

    AB=a, AC=b; H is calculated by orthogonal projection, not placed by eye.
    """
    if a <= 0 or b <= 0:
        raise ValueError("Right-triangle legs must be positive")
    A, B, C = labels
    c2 = a*a + b*b
    c = math.sqrt(c2)
    H = [a*b*b/c2, a*a*b/c2]
    points = {A: [0.0, 0.0], B: [float(a), 0.0], C: [0.0, float(b)], "H": H}
    return _geom(points, [[A, B], [B, "H"], ["H", C], [C, A], [A, "H"]],
        "Tam giác vuông tại A; H là hình chiếu vuông góc của A lên cạnh huyền BC.",
        right_angle=A, altitudes=[[A, "H"]],
        measurements=[{"from": A, "to": B, "text": str(a)}, {"from": A, "to": C, "text": str(b)}],
        constraints=[{"type": "point_on_segment", "point": "H", "segment": [B, C]},
                     {"type": "right_triangle_altitude", "vertex": A, "foot": "H", "base": [B, C]}])


def external_tangents_to_circle(radius=1, labels=("A", "B", "P", "O")):
    """Exact diagram for two tangents from P=(2r,0) to a circle of radius r."""
    if radius <= 0:
        raise ValueError("Circle radius must be positive")
    A, B, P, O = labels
    r = float(radius)
    points = {O: [0.0, 0.0], P: [2*r, 0.0], A: [r/2, math.sqrt(3)*r/2], B: [r/2, -math.sqrt(3)*r/2]}
    return _geom(points, [[O, A], [O, B], [P, A], [P, B], [A, B]],
        "Hai tiếp tuyến từ P đến đường tròn; bán kính vuông góc tiếp tuyến tại tiếp điểm.",
        circles=[{"center": [0.0, 0.0], "radius": r}], circle_vertices=[A, B],
        tangent_constraints=[[O, A, P], [O, B, P]],
        measurements=[{"from": O, "to": A, "text": str(radius)}, {"from": O, "to": B, "text": str(radius)}])


def normalize_geometry_diagram(diagram):
    """Convert legacy compact diagram payloads into data-bound geometry primitives.

    This keeps older question banks working while preventing their generic SVG
    placeholders from ignoring dimensions and coordinates carried by a prompt.
    Unknown diagram types are left untouched for their dedicated renderer.
    """
    if not isinstance(diagram, dict):
        return diagram
    kind = diagram.get("type")
    try:
        if kind == "right_triangle":
            a, b = float(diagram["a"]), float(diagram["b"])
            return triangle_3_4_5(a, b, tuple(diagram.get("labels", ("A", "B", "C"))))
        if kind == "triangle_area":
            base, height = float(diagram["base"]), float(diagram["height"])
            if min(base, height) <= 0:
                raise ValueError("Triangle base and height must be positive")
            A, B, C, H = "A", "B", "C", "H"
            foot = base * 0.62
            return _geom({A: [0.0, 0.0], B: [base, 0.0], C: [foot, height], H: [foot, 0.0]},
                [[A, B], [B, C], [C, A], [C, H], [H, B]],
                "Tam giác có đáy và chiều cao đúng theo dữ kiện.", right_angle=H,
                altitudes=[[C, H]], dashed_segments=[[C, H]],
                measurements=[{"from": A, "to": B, "text": str(base)}, {"from": H, "to": C, "text": str(height)}],
                constraints=[{"type": "point_on_segment", "point": H, "segment": [A, B]},
                             {"type": "right_triangle_altitude", "vertex": C, "foot": H, "base": [A, B]}])
        if kind == "circle" and diagram.get("shape") == "diameter" and isinstance(diagram.get("points"), dict):
            radius = diagram.get("radius")
            if radius is not None and float(radius) > 0:
                points = {name: list(xy) for name, xy in diagram["points"].items()}
                center = points.get("O", [0.0, 0.0])
                diameter_points = [name for name in ("A", "B") if name in points]
                measurements = ([{"from": diameter_points[0], "to": diameter_points[1], "text": str(diagram.get("diameter"))}]
                                if len(diameter_points) == 2 and diagram.get("diameter") is not None else [])
                return _geom(points, diagram.get("segments", [["A", "B"]]),
                    diagram.get("caption", "Đường tròn và đường kính theo dữ kiện."),
                    circles=[{"center": center, "radius": float(radius)}],
                    circle_vertices=diameter_points, measurements=measurements, diagram_mode="exact_data")
        if kind == "circle" and not diagram.get("points") and diagram.get("radius", diagram.get("r")) is not None:
            return circle(float(diagram.get("radius", diagram.get("r"))))
        if kind == "circle_tangent" and diagram.get("radius", diagram.get("r")) is not None:
            return circle_with_tangent(float(diagram.get("radius", diagram.get("r"))))
        if kind == "pyramid" and not diagram.get("points"):
            schematic = pyramid_projection(tuple(diagram.get("labels", ("S", "A", "B", "C", "D"))))
            schematic["diagram_mode"] = "schematic_projection"
            schematic["caption"] = "Sơ đồ hình chóp minh họa; dùng các điều kiện ghi trong đề để suy luận."
            return schematic
        if kind == "points" and isinstance(diagram.get("a"), (list, tuple)) and isinstance(diagram.get("b"), (list, tuple)):
            a, b = diagram["a"], diagram["b"]
            if len(a) < 2 or len(b) < 2:
                raise ValueError("Coordinate points require x and y")
            return _geom({"A": [float(a[0]), float(a[1])], "B": [float(b[0]), float(b[1])]},
                [["A", "B"]], "Hai điểm được đặt theo đúng tọa độ đề bài.", axes=True,
                coordinates_2d={"A": [float(a[0]), float(a[1])], "B": [float(b[0]), float(b[1])]})
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        # The caller's validation gate will suppress malformed geometry rather than
        # silently replacing it with a plausible but unrelated illustration.
        return {"type": "geometry", "points": {}, "segments": [], "caption": "Không thể dựng hình từ dữ kiện hiện có.",
                "diagram_error": str(exc)}
    return diagram

def validate_geometry_diagram(diagram):
    """Return errors for malformed geometry or inconsistent right-angle/circle constraints."""
    errors=[]
    if not isinstance(diagram,dict) or diagram.get("type")!="geometry": return errors
    points=diagram.get("points",{})
    if not isinstance(points,dict): return ["points must be a mapping"]
    if not points and not diagram.get("circles"):
        return ["geometry diagram needs at least one point or circle"]
    for name,xy in points.items():
        if not isinstance(xy,(list,tuple)) or len(xy)<2:
            errors.append(f"point {name} must have x,y coordinates"); continue
        try:
            if not all(math.isfinite(float(v)) for v in xy[:2]):
                errors.append(f"point {name} has non-finite coordinates")
        except (TypeError, ValueError, OverflowError):
            errors.append(f"point {name} has non-numeric coordinates")
    for seg in diagram.get("segments",[]):
        if not isinstance(seg,(list,tuple)) or len(seg)!=2 or seg[0] not in points or seg[1] not in points:
            errors.append(f"invalid segment {seg}")
    # Explicit shape constraints are checked numerically before a diagram is sent to the UI.
    for constraint in diagram.get("constraints", []):
        kind = constraint.get("type") if isinstance(constraint, dict) else None
        if kind == "rectangle":
            names = constraint.get("vertices", [])
            if len(names) != 4 or any(n not in points for n in names):
                errors.append("rectangle constraint needs four existing vertices"); continue
            A, B, C, D = (points[n][:2] for n in names)
            def dot2(u, v): return u[0]*v[0] + u[1]*v[1]
            def sub2(u, v): return [u[0]-v[0], u[1]-v[1]]
            edges = [sub2(B,A), sub2(C,B), sub2(D,C), sub2(A,D)]
            if any(math.hypot(*e) <= 1e-12 for e in edges): errors.append("rectangle has a zero-length side")
            else:
                if abs(dot2(edges[0], edges[1])) > 1e-7*math.hypot(*edges[0])*math.hypot(*edges[1]): errors.append("rectangle adjacent sides are not perpendicular")
                if not (math.isclose(math.dist(A,B), math.dist(C,D), rel_tol=1e-7, abs_tol=1e-7) and math.isclose(math.dist(B,C), math.dist(D,A), rel_tol=1e-7, abs_tol=1e-7)): errors.append("rectangle opposite sides do not match")
        elif kind == "side_ratio":
            keys = (constraint.get("from"), constraint.get("to"), constraint.get("other_from"), constraint.get("other_to"))
            if any(k not in points for k in keys): errors.append("side ratio references missing points"); continue
            ratio = float(constraint.get("ratio", 0))
            a = math.dist(points[keys[0]][:2], points[keys[1]][:2]); b = math.dist(points[keys[2]][:2], points[keys[3]][:2])
            if ratio <= 0 or b <= 0 or not math.isclose(a/b, ratio, rel_tol=1e-7, abs_tol=1e-7): errors.append("side ratio does not match the requested proportion")
    for altitude in diagram.get("altitudes", []):
        if not isinstance(altitude, (list, tuple)) or len(altitude) != 2:
            errors.append("altitude must be [vertex, foot]"); continue
        vertex, foot = altitude
        if vertex not in points or foot not in points:
            errors.append("altitude endpoints must exist"); continue
        support = [s for s in diagram.get("segments", []) if foot in s and vertex not in s]
        u = [points[vertex][i] - points[foot][i] for i in range(2)]
        valid = False
        for seg in support:
            other = seg[1] if seg[0] == foot else seg[0]
            if other not in points: continue
            v = [points[other][i] - points[foot][i] for i in range(2)]
            dot = u[0]*v[0] + u[1]*v[1]
            if abs(dot) <= 1e-7 * max(1, math.hypot(*u)*math.hypot(*v)):
                valid = True; break
        if not valid: errors.append(f"altitude {vertex}{foot} is not perpendicular to its base")
    for c in diagram.get("circles",[]):
        radius=float(c.get("radius",0)); center=c.get("center",[0,0])
        if radius<=0 or not math.isfinite(radius): errors.append("circle radius must be positive and finite"); continue
        if len(center)<2 or not all(math.isfinite(float(v)) for v in center[:2]): errors.append("circle center is invalid"); continue
        for name,xy in points.items():
            if name in {"O","I"} and math.dist(xy[:2],center[:2])<1e-8: continue
            # Only validate points explicitly marked as circle vertices, not auxiliary outside points.
        for name in diagram.get("circle_vertices",[]):
            if name not in points or not math.isclose(math.dist(points[name][:2],center[:2]),radius,rel_tol=1e-7,abs_tol=1e-7):
                errors.append(f"point {name} does not lie on its declared circle")
    for vertex in ([diagram.get("right_angle")] if diagram.get("right_angle") else []) + list(diagram.get("right_angles",[])):
        adjacent=[]
        for seg in diagram.get("segments",[]):
            if vertex in seg:
                other=seg[1] if seg[0]==vertex else seg[0]
                if other in points and other!=vertex: adjacent.append(other)
        if len(adjacent)>=2:
            u=[points[adjacent[0]][i]-points[vertex][i] for i in range(2)]
            v=[points[adjacent[1]][i]-points[vertex][i] for i in range(2)]
            dot=u[0]*v[0]+u[1]*v[1]
            if abs(dot)>1e-6*max(1,math.hypot(*u)*math.hypot(*v)): errors.append(f"marked right angle at {vertex} is not perpendicular")
    for constraint in diagram.get("constraints", []):
        if not isinstance(constraint, dict):
            continue
        if constraint.get("type") == "point_on_segment":
            name = constraint.get("point"); seg = constraint.get("segment", [])
            if name not in points or len(seg) != 2 or any(n not in points for n in seg):
                errors.append("point-on-segment constraint references missing points"); continue
            P, A, B = points[name][:2], points[seg[0]][:2], points[seg[1]][:2]
            cross = (P[0]-A[0])*(B[1]-A[1])-(P[1]-A[1])*(B[0]-A[0])
            dot = (P[0]-A[0])*(P[0]-B[0])+(P[1]-A[1])*(P[1]-B[1])
            if abs(cross) > 1e-7*max(1, math.dist(A,B)**2) or dot > 1e-7:
                errors.append(f"point {name} is not on segment {seg[0]}{seg[1]}")
        elif constraint.get("type") == "right_triangle_altitude":
            v, foot = constraint.get("vertex"), constraint.get("foot")
            base = constraint.get("base", [])
            if v not in points or foot not in points or len(base) != 2 or any(n not in points for n in base):
                errors.append("right-triangle altitude constraint references missing points"); continue
            V, H, X, Y = points[v][:2], points[foot][:2], points[base[0]][:2], points[base[1]][:2]
            dot = (V[0]-H[0])*(Y[0]-X[0])+(V[1]-H[1])*(Y[1]-X[1])
            if abs(dot) > 1e-7*max(1, math.dist(V,H)*math.dist(X,Y)):
                errors.append(f"altitude {v}{foot} is not perpendicular to base {base}")
    for tangent in diagram.get("tangent_constraints", []):
        if not isinstance(tangent, (list, tuple)) or len(tangent) != 3 or any(n not in points for n in tangent):
            errors.append("tangent constraint references missing points"); continue
        center, touch, external = (points[n][:2] for n in tangent)
        u = [center[i]-touch[i] for i in range(2)]
        v = [external[i]-touch[i] for i in range(2)]
        dot = u[0]*v[0]+u[1]*v[1]
        if abs(dot) > 1e-7*max(1, math.hypot(*u)*math.hypot(*v)):
            errors.append(f"radius at {touch} is not perpendicular to tangent")
    return errors

def circle_with_diameter(radius,center=(0,0),center_label="O"):
    h,k=center; A=[h-radius,k]; B=[h+radius,k]
    return _geom({center_label:[h,k],"A":A,"B":B},[["A","B"]],"Đường kính đi qua tâm và có độ dài bằng hai lần bán kính.",circles=[{"center":[h,k],"radius":radius}],measurements=[{"from":"A","to":"B","text":str(2*radius)}])

def inscribed_triangle_by_angles(angle_a,angle_b,radius=5,labels=("A","B","C")):
    """Place a triangle with the supplied interior angles on a circumcircle."""
    angle_c=180-angle_a-angle_b
    if min(angle_a,angle_b,angle_c)<=0 or max(angle_a,angle_b,angle_c)>=180 or radius<=0:
        raise ValueError("Triangle angles must be positive and sum to 180 degrees")
    A,B,C=labels
    def pt(deg):
        rad=math.radians(deg)
        return [radius*math.cos(rad),radius*math.sin(rad)]
    # Arc AB opposite C is 2*C; the other arcs similarly encode A and B.
    points={A:pt(0),B:pt(2*angle_c),C:pt(2*(angle_c+angle_a)),"O":[0,0]}
    return _geom(points,[[A,B],[B,C],[C,A]],"Tam giác nội tiếp đường tròn với các góc phù hợp dữ kiện.",
      circles=[{"center":[0,0],"radius":radius}],circle_vertices=[A,B,C],angle_labels={A:angle_a,B:angle_b,C:angle_c})

def circle_with_central_angle(angle,radius=5):
    if not 0<angle<180 or radius<=0: raise ValueError("Central angle must be between 0 and 180 degrees")
    def pt(deg):
        rad=math.radians(deg)
        return [radius*math.cos(rad),radius*math.sin(rad)]
    return _geom({"O":[0,0],"A":pt(0),"B":pt(angle),"C":pt(angle/2+180)},
      [["O","A"],["O","B"],["A","B"],["A","C"],["B","C"]],
      "Góc ở tâm và góc nội tiếp cùng chắn cung AB.",circles=[{"center":[0,0],"radius":radius}],circle_vertices=["A","B","C"],angle_labels={"AOB":angle,"ACB":angle/2})

def triangle_from_angles(angle_a,angle_b,scale=5,labels=("A","B","C")):
    angle_c=180-angle_a-angle_b
    if min(angle_a,angle_b,angle_c)<=0 or scale<=0: raise ValueError("Triangle angles must be positive and sum to 180 degrees")
    A,B,C=labels; side_b=scale*math.sin(math.radians(angle_b))/math.sin(math.radians(angle_c))
    points={A:[0,0],B:[scale,0],C:[side_b*math.cos(math.radians(angle_a)),side_b*math.sin(math.radians(angle_a))]}
    return _geom(points,[[A,B],[B,C],[C,A]],"Tam giác dựng theo đúng ba góc đã cho.",angle_labels={A:angle_a,B:angle_b,C:angle_c})

def similar_triangles(small_side,scale,labels=("A","B","C","D","E","F")):
    if small_side<=0 or scale<=1: raise ValueError("Similarity scale must be greater than one")
    A,B,C,D,E,F=labels; h=small_side*0.75
    return _geom({A:[0,0],B:[small_side,0],C:[small_side*0.35,h],D:[small_side+2,0],E:[small_side+2+small_side*scale,0],F:[small_side+2+small_side*scale*0.35,h*scale]},
      [[A,B],[B,C],[C,A],[D,E],[E,F],[F,D]],"Hai tam giác đồng dạng với cạnh tương ứng theo tỉ số đã nêu.")

def circle_with_chord(radius,half_chord,distance,center=(0,0)):
    if radius<=0 or half_chord<=0 or distance<0 or not math.isclose(half_chord**2+distance**2,radius**2,rel_tol=1e-7,abs_tol=1e-7):
        raise ValueError("Chord, distance and radius must satisfy half_chord²+distance²=radius²")
    h,k=center; A=[h-half_chord,k+distance]; B=[h+half_chord,k+distance]; H=[h,k+distance]
    return _geom({"O":[h,k],"A":A,"B":B,"H":H},[["O","A"],["O","B"],["A","B"],["O","H"]],
      "Dây cung và khoảng cách từ tâm khớp chính xác với bán kính.",circles=[{"center":[h,k],"radius":radius}],circle_vertices=["A","B"],right_angle="H",
      measurements=[{"from":"A","to":"B","text":str(2*half_chord)},{"from":"O","to":"H","text":str(distance)}])

def coordinate_points(points,segments=None,caption="Hình tọa độ theo dữ kiện"):
    return _geom(points,segments or [],caption,axes=True)

def parallel_lines_transversal(angle_degrees=55):
    if not 0<angle_degrees<180: raise ValueError("Angle must be between 0 and 180 degrees")
    slope=math.tan(math.radians(angle_degrees)); x_top=3/(slope if abs(slope)>1e-6 else 1e-6)
    return _geom({"A":[-5,0],"B":[5,0],"C":[x_top-5,3],"D":[x_top+5,3],"P":[0,0],"Q":[x_top,3]},
      [["A","B"],["C","D"],["P","Q"]],"Hai đường thẳng song song bị cắt bởi một đường thẳng; góc ghi theo dữ kiện đề.",angle_labels={"P":angle_degrees})

def angle_bisector_triangle(side_ab,side_ac,ratio_m,ratio_n):
    if min(side_ab,side_ac,ratio_m,ratio_n)<=0 or ratio_m==ratio_n==0: raise ValueError("Invalid angle-bisector data")
    base=abs(side_ab-side_ac)+2
    if base>=side_ab+side_ac: base=(side_ab+side_ac)/2
    x=(side_ab**2+base**2-side_ac**2)/(2*base)
    y2=side_ab**2-x**2
    if y2<=0: raise ValueError("Side lengths do not form a triangle")
    y=math.sqrt(y2); d=base*ratio_m/(ratio_m+ratio_n)
    return _geom({"A":[x,y],"B":[0,0],"C":[base,0],"D":[d,0]},[["A","B"],["A","C"],["B","C"],["A","D"]],"Tam giác và tia phân giác được dựng từ độ dài cạnh cùng tỉ số BD:DC.")

def triangle_median_diagram(a,b):
    d=triangle_3_4_5(a,b); p=d["points"]; A,B,C="A","B","C"
    p["M"]=[(p[B][0]+p[C][0])/2,(p[B][1]+p[C][1])/2]
    d["segments"].append([A,"M"]); d["caption"]="Tam giác vuông và trung tuyến AM đến trung điểm cạnh huyền BC."
    return d

def cyclic_chords_diagram():
    names=("A","B","C","D","E","F","G","H")
    d=regular_polygon(8,5,labels=names)
    d["segments"] += [["A","E"],["C","G"]]
    d["caption"]="Hai dây cung cắt nhau bên trong đường tròn."
    return d


def graph_diagram(curves, x_range=(-5, 5), y_range=(-5, 5), caption="Đồ thị trên hệ trục tọa độ", marked_points=None, asymptotes=None, grid=True, x_label="x", y_label="y"):
    """Build a renderer-safe Cartesian graph from sampled numeric points.

    curves: [{label: str, points: [[x,y], ...], style?: str}]
    marked_points: [{x: number, y: number, label: str}]
    asymptotes: [{axis: 'x'|'y', value: number, label?: str}]
    """
    xmin, xmax = map(float, x_range); ymin, ymax = map(float, y_range)
    if not all(math.isfinite(v) for v in (xmin, xmax, ymin, ymax)) or xmin >= xmax or ymin >= ymax:
        raise ValueError("Graph ranges must be finite and increasing")
    clean_curves = []
    for curve in curves:
        pts = curve.get("points", [])
        clean = []
        for point in pts:
            if len(point) >= 2 and all(math.isfinite(float(v)) for v in point[:2]):
                x, y = float(point[0]), float(point[1])
                if xmin - 1e-8 <= x <= xmax + 1e-8:
                    clean.append([x, y])
        if len(clean) >= 2:
            clean_curves.append({"label": str(curve.get("label", "f(x)")), "points": clean, "style": str(curve.get("style", "solid"))})
    if not clean_curves and not marked_points:
        raise ValueError("A graph needs at least one curve or marked point")
    clean_marks = []
    for point in marked_points or []:
        x, y = float(point["x"]), float(point["y"])
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError("Marked point coordinates must be finite")
        clean_marks.append({"x": x, "y": y, "label": str(point.get("label", f"({x:g}; {y:g})"))})
    clean_asymptotes = []
    for item in asymptotes or []:
        axis, value = item.get("axis"), float(item.get("value", 0))
        if axis not in {"x", "y"} or not math.isfinite(value):
            raise ValueError("Asymptote must have axis x/y and finite value")
        clean_asymptotes.append({"axis": axis, "value": value, "label": str(item.get("label", ""))})
    return {"type": "graph", "x_range": [xmin, xmax], "y_range": [ymin, ymax],
            "curves": clean_curves, "marked_points": clean_marks, "asymptotes": clean_asymptotes,
            "grid": bool(grid), "x_label": str(x_label), "y_label": str(y_label), "caption": str(caption)}

def function_graph(function, x_range=(-5, 5), y_range=(-5, 5), label="y=f(x)", caption="Đồ thị hàm số", samples=121, marked_points=None):
    """Sample a trusted Python function into a graph diagram; no expressions are evaluated."""
    xmin, xmax = map(float, x_range)
    if samples < 2 or samples > 1001:
        raise ValueError("samples must be between 2 and 1001")
    points = []
    for i in range(samples):
        x = xmin + (xmax - xmin) * i / (samples - 1)
        try:
            y = float(function(x))
        except (ValueError, ZeroDivisionError, OverflowError):
            continue
        if math.isfinite(y): points.append([x, y])
    return graph_diagram([{"label": label, "points": points}], x_range, y_range, caption, marked_points=marked_points)

def line_graph(slope, intercept, x_range=(-5, 5), y_range=(-5, 5), label=None):
    return function_graph(lambda x: slope*x + intercept, x_range, y_range, label or f"y={slope:g}x+({intercept:g})", "Đồ thị hàm số bậc nhất", marked_points=[{"x": 0, "y": intercept, "label": f"(0; {intercept:g})"}] if y_range[0] <= intercept <= y_range[1] else None)

def quadratic_graph(a, b, c, x_range=(-5, 5), y_range=(-5, 10), label=None):
    if a == 0: raise ValueError("Quadratic coefficient a must be nonzero")
    vx = -b/(2*a); vy = a*vx*vx+b*vx+c
    marks = [{"x": vx, "y": vy, "label": f"I({vx:g}; {vy:g})"}] if x_range[0] <= vx <= x_range[1] and y_range[0] <= vy <= y_range[1] else []
    return function_graph(lambda x: a*x*x+b*x+c, x_range, y_range, label or f"y={a:g}x²+{b:g}x+{c:g}", "Đồ thị parabol của hàm số bậc hai", marked_points=marks)

def trigonometric_graph(kind="sin", x_range=(-2*math.pi, 2*math.pi), y_range=(-1.5, 1.5), samples=241):
    funcs = {"sin": math.sin, "cos": math.cos, "tan": math.tan}
    if kind not in funcs: raise ValueError("Supported trigonometric graph types: sin, cos, tan")
    # Break tan near its vertical asymptotes rather than drawing false connecting segments.
    if kind != "tan": return function_graph(funcs[kind], x_range, y_range, f"y={kind}(x)", f"Đồ thị hàm số y={kind}(x)", samples=samples)
    xmin, xmax = x_range; curves=[]; current=[]
    for i in range(samples):
        x=xmin+(xmax-xmin)*i/(samples-1); y=math.tan(x)
        if not math.isfinite(y) or abs(y)>max(abs(y_range[0]),abs(y_range[1]))*3:
            if len(current)>=2: curves.append({"label":"y=tan(x)","points":current})
            current=[]; continue
        current.append([x,y])
    if len(current)>=2: curves.append({"label":"y=tan(x)","points":current})
    return graph_diagram(curves,x_range,y_range,"Đồ thị hàm số y=tan(x)",asymptotes=[{"axis":"x","value":math.pi/2+k*math.pi,"label":""} for k in range(math.floor((xmin-math.pi/2)/math.pi),math.ceil((xmax-math.pi/2)/math.pi)+1) if xmin < math.pi/2+k*math.pi < xmax])

def exponential_graph(base=2, x_range=(-4, 4), y_range=(0, 10)):
    if base <= 0 or math.isclose(base, 1): raise ValueError("Exponential base must be positive and not 1")
    return function_graph(lambda x: base**x, x_range, y_range, f"y={base:g}ˣ", "Đồ thị hàm số mũ")

def logarithmic_graph(base=2, x_range=(-0.5, 8), y_range=(-4, 4)):
    if base <= 0 or math.isclose(base, 1): raise ValueError("Logarithm base must be positive and not 1")
    xmin, xmax = x_range
    if xmin >= xmax: raise ValueError("Invalid logarithm graph range")
    points=[]
    for i in range(241):
        x=xmin+(xmax-xmin)*i/240
        if x <= 0: continue
        y=math.log(x, base)
        if math.isfinite(y): points.append([x,y])
    return graph_diagram([{"label":f"y=log_{base:g}(x)","points":points}], x_range, y_range, "Đồ thị hàm số logarit", asymptotes=[{"axis":"x", "value":0, "label":"x=0"}])

def ellipse_graph(a=4, b=2, center=(0, 0), x_range=None, y_range=None):
    if a <= 0 or b <= 0: raise ValueError("Ellipse semi-axes must be positive")
    h, k = center; xr = x_range or (h-a-1, h+a+1); yr = y_range or (k-b-1, k+b+1)
    pts = [[h+a*math.cos(2*math.pi*i/240), k+b*math.sin(2*math.pi*i/240)] for i in range(241)]
    return graph_diagram([{"label":"Elip", "points":pts}], xr, yr, "Đồ thị elip theo các bán trục đã cho", marked_points=[{"x":h,"y":k,"label":"I"}])

def hyperbola_graph(a=2, b=1, center=(0, 0), orientation="horizontal", x_range=(-5, 5), y_range=(-5, 5)):
    if a <= 0 or b <= 0: raise ValueError("Hyperbola parameters must be positive")
    h, k = center; curves=[]
    for sign in (-1, 1):
        pts=[]
        for i in range(241):
            t=-2.5+5*i/240
            if orientation == "vertical":
                x=h+a*math.sinh(t); y=k+sign*b*math.cosh(t)
            else:
                x=h+sign*a*math.cosh(t); y=k+b*math.sinh(t)
            pts.append([x,y])
        curves.append({"label":"Hypebol", "points":pts})
    if orientation == "horizontal":
        for sign in (-1,1):
            curves.append({"label":"Tiệm cận", "style":"dashed", "points":[[x, k+sign*(b/a)*(x-h)] for x in [x_range[0]+(x_range[1]-x_range[0])*i/100 for i in range(101)]]})
    else:
        for sign in (-1,1):
            curves.append({"label":"Tiệm cận", "style":"dashed", "points":[[x, k+sign*(b/a)*(x-h)] for x in [x_range[0]+(x_range[1]-x_range[0])*i/100 for i in range(101)]]})
    return graph_diagram(curves, x_range, y_range, "Đồ thị hypebol; các nhánh và tiệm cận được biểu diễn bằng nét đứt", marked_points=[{"x":h,"y":k,"label":"I"}])

def isosceles_triangle_diagram():
    d=_geom({"A":[0,4],"B":[-3,0],"C":[3,0],"M":[0,0]},[["A","B"],["A","C"],["B","C"],["A","M"]],"Tam giác cân tại A; AM là trung tuyến xuống đáy BC.")
    return d

def parabola_diagram(p):
    if p<=0: raise ValueError("Parabola parameter p must be positive")
    samples=[(y*y/(4*p),y) for y in (-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6)]
    return _geom({"V":[0,0],"F":[p,0]},[],"Parabol y²=4px với đỉnh V và tiêu điểm F theo đúng tham số p.",polylines=[samples],axes=True)

def cube_projection(side=1,show_measurement=False,show_diagonal=False):
    if side<=0: raise ValueError("Cube side must be positive")
    s=float(side); dx=s*0.52; dy=s*0.38
    points={"A":[0,0],"B":[s,0],"C":[s+dx,dy],"D":[dx,dy],"A1":[0,s],"B1":[s,s],"C1":[s+dx,s+dy],"D1":[dx,s+dy]}
    segs=[["A","B"],["B","C"],["C","D"],["A1","B1"],["B1","C1"],["C1","D1"],["D1","A1"],["B","B1"],["C","C1"]]
    hidden=[["D","A"],["A","A1"],["D","D1"]]
    if show_diagonal: segs.append(["A","C1"])
    measurements=[{"from":"A","to":"B","text":str(side)}] if show_measurement else []
    return _geom(points,segs,"Hình chiếu song song của hình lập phương; độ dài cạnh được ghi khi đề cho.",hidden_segments=hidden,measurements=measurements)

def cylinder_projection(radius,height):
    if radius<=0 or height<=0: raise ValueError("Cylinder dimensions must be positive")
    rx=radius; ry=radius*0.32; y0=0; y1=height
    def ellipse(cx,cy): return [[cx+rx*math.cos(2*math.pi*i/48),cy+ry*math.sin(2*math.pi*i/48)] for i in range(49)]
    points={"O":[0,y0],"O1":[0,y1],"R":[radius,y0],"T":[radius,y1]}
    return _geom(points,[["O","R"],["O","O1"],["O1","T"]],"Hình trụ với bán kính đáy và chiều cao theo đề.",polylines=[ellipse(0,y0),ellipse(0,y1)],measurements=[{"from":"O","to":"R","text":str(radius)},{"from":"O","to":"O1","text":str(height)}])

def cone_projection(radius,height):
    if radius<=0 or height<=0: raise ValueError("Cone dimensions must be positive")
    rx=radius; ry=radius*0.32; y0=0; apex=[0,height]
    base=[[rx*math.cos(2*math.pi*i/48),y0+ry*math.sin(2*math.pi*i/48)] for i in range(49)]
    return _geom({"S":apex,"O":[0,0],"A":[radius,0],"B":[-radius,0]},[["S","A"],["S","B"],["O","S"],["O","A"]],"Hình nón với bán kính đáy và chiều cao theo đề.",polylines=[base],measurements=[{"from":"O","to":"A","text":str(radius)},{"from":"O","to":"S","text":str(height)}])

def sphere_projection(radius,center=(0,0,0),center_label="I"):
    if radius<=0: raise ValueError("Sphere radius must be positive")
    x,y,z=center
    return _geom({center_label:[x,y],"R":[x+radius,y]},[[center_label,"R"]],"Hình chiếu phẳng của mặt cầu; tâm và bán kính theo dữ kiện không gian.",circles=[{"center":[x,y],"radius":radius}],measurements=[{"from":center_label,"to":"R","text":str(radius)}])


def rectangular_prism_projection(length, width, height, labels=("A", "B", "C", "D", "A1", "B1", "C1", "D1"), show_measurements=True):
    """Build a dimension-aware oblique projection of a rectangular prism.

    The edge lengths are preserved in metadata; the drawing is a 2D projection,
    so depth edges are intentionally projected rather than represented as true
    2D distances.
    """
    if min(length, width, height) <= 0:
        raise ValueError("Prism dimensions must be positive")
    L, W, H = map(float, (length, width, height))
    A, B, C, D, A1, B1, C1, D1 = labels
    dx, dy = W * 0.52, W * 0.38
    points = {
        A: [0.0, 0.0], B: [L, 0.0], C: [L + dx, dy], D: [dx, dy],
        A1: [0.0, H], B1: [L, H], C1: [L + dx, H + dy], D1: [dx, H + dy],
    }
    # Preserve the exact three-dimensional vertices separately from their 2D projection.
    coordinates_3d = {
        A: [0.0, 0.0, 0.0], B: [L, 0.0, 0.0], C: [L, W, 0.0], D: [0.0, W, 0.0],
        A1: [0.0, 0.0, H], B1: [L, 0.0, H], C1: [L, W, H], D1: [0.0, W, H],
    }
    # Draw visible edges as solid and back-left edges as dashed, without duplicating them.
    segments = [[A,B],[B,C],[C,D],[A1,B1],[B1,C1],[C1,D1],[D1,A1],[A,A1],[B,B1],[C,C1]]
    hidden = [[D,A],[D,D1]]
    measurements = []
    if show_measurements:
        measurements = [
            {"from": A, "to": B, "text": str(length)},
            {"from": A, "to": A1, "text": str(height)},
            {"from": A, "to": D, "text": str(width)},
        ]
    return _geom(points, segments, "Hình hộp chữ nhật chiếu xiên; ba kích thước được lấy từ đề bài.",
        hidden_segments=hidden, measurements=measurements,
        solid_dimensions={"length": L, "width": W, "height": H}, coordinates_3d=coordinates_3d,
        projection="oblique", diagram_mode="schematic_projection",
        constraints=[{"type":"rectangular_prism","dimensions":[L,W,H]}])


def spatial_points_projection(points_3d, segments=None, caption="Các điểm Oxyz được chiếu xiên từ tọa độ đề bài"):
    """Project explicit Oxyz coordinates to a drawable 2D oblique view.

    Original coordinates remain attached so downstream tools can use the exact
    3D data. The projected picture is labelled schematic, never to scale in 2D.
    """
    if not isinstance(points_3d, dict) or not points_3d:
        raise ValueError("At least one 3D point is required")
    projected = {}
    exact = {}
    for name, xyz in points_3d.items():
        if not isinstance(xyz, (list, tuple)) or len(xyz) != 3:
            raise ValueError(f"Point {name} must have x,y,z coordinates")
        vals = [float(v) for v in xyz]
        if not all(math.isfinite(v) for v in vals):
            raise ValueError(f"Point {name} has non-finite coordinates")
        x, y, z = vals
        projected[name] = [x - 0.45*z, y + 0.45*z]
        exact[name] = vals
    segs = segments or []
    for seg in segs:
        if len(seg) != 2 or any(name not in projected for name in seg):
            raise ValueError(f"Invalid segment {seg}")
    return _geom(projected, segs, caption, axes=True, coordinates_3d=exact,
        projection="oblique", diagram_mode="schematic_projection",
        coordinate_warning="Tọa độ 3D là dữ kiện chính xác; hình 2D là phép chiếu minh họa, không dùng độ dài chiếu để suy luận.")


def regular_prism_projection(sides=5, radius=2, height=3, labels=None):
    """Dimension-aware right regular prism projection with exact 3D vertex metadata."""
    if not isinstance(sides, int) or sides < 3 or sides > 12:
        raise ValueError("Prism base must have 3 to 12 sides")
    if not math.isfinite(float(radius)) or not math.isfinite(float(height)) or radius <= 0 or height <= 0:
        raise ValueError("Prism radius and height must be positive finite numbers")
    r, h = float(radius), float(height)
    names = labels or ([chr(65+i) for i in range(sides)] + [chr(65+i)+"1" for i in range(sides)])
    if len(names) != 2*sides or len(set(names)) != len(names):
        raise ValueError("Need unique labels for all 2n prism vertices")
    base3 = [(r*math.cos(2*math.pi*i/sides), r*math.sin(2*math.pi*i/sides), 0.0) for i in range(sides)]
    top3 = [(x,y,h) for x,y,_ in base3]
    exact = {names[i]: list(base3[i]) for i in range(sides)}
    exact.update({names[sides+i]: list(top3[i]) for i in range(sides)})
    # Oblique projection: x' = x - 0.45y, y' = z + 0.45y.
    points = {k:[v[0]-0.45*v[1], v[2]+0.45*v[1]] for k,v in exact.items()}
    segments=[]; hidden=[]
    for i in range(sides):
        j=(i+1)%sides
        edge=[names[i],names[j]]
        top_edge=[names[sides+i],names[sides+j]]
        (hidden if math.sin(2*math.pi*(i+0.5)/sides) < -0.15 else segments).append(edge)
        segments.append(top_edge)
        segments.append([names[i],names[sides+i]])
    return _geom(points, segments, f"Lăng trụ đứng đáy đa giác đều {sides} cạnh; bán kính ngoại tiếp đáy {r:g}, chiều cao {h:g}. Phép chiếu xiên, không dùng độ dài chiếu để suy luận.", hidden_segments=hidden, coordinates_3d=exact, solid_dimensions={"base_sides":sides,"circumradius":r,"height":h}, projection="oblique", diagram_mode="schematic_projection", constraints=[{"type":"right_regular_prism","base_sides":sides,"height":h}])


def triangular_prism_by_dimensions(side_a=3, side_b=4, side_c=5, length=6, labels=("A","B","C","A1","B1","C1")):
    """Triangular prism with a triangle computed from its three side lengths."""
    a,b,c,L=map(float,(side_a,side_b,side_c,length))
    if min(a,b,c,L)<=0 or max(a,b,c) >= sum((a,b,c))-max(a,b,c):
        raise ValueError("Triangle sides must be positive and satisfy triangle inequality; length must be positive")
    # Place AB=c on x-axis; AC=b, BC=a.
    x=(b*b+c*c-a*a)/(2*c); y=math.sqrt(max(0.0,b*b-x*x))
    base=[(0.0,0.0,0.0),(c,0.0,0.0),(x,y,0.0)]
    top=[(px,py,L) for px,py,_ in base]
    names=list(labels)
    if len(names)!=6 or len(set(names))!=6: raise ValueError("Six unique vertex labels required")
    exact={names[i]:list(base[i]) for i in range(3)}; exact.update({names[i+3]:list(top[i]) for i in range(3)})
    points={k:[v[0]-0.45*v[1],v[2]+0.45*v[1]] for k,v in exact.items()}
    segments=[[names[0],names[1]],[names[1],names[2]],[names[2],names[0]], [names[3],names[4]],[names[4],names[5]],[names[5],names[3]], [names[0],names[3]],[names[1],names[4]],[names[2],names[5]]]
    return _geom(points,segments,"Lăng trụ tam giác dựng từ ba cạnh đáy và chiều dài lăng trụ.",coordinates_3d=exact,solid_dimensions={"triangle_sides":[a,b,c],"length":L},projection="oblique",diagram_mode="schematic_projection",constraints=[{"type":"triangular_prism","base_sides":[a,b,c],"length":L}])


def pyramid_by_base_height(sides=4, radius=2, height=3, labels=None):
    """Regular pyramid projection; base vertices and apex are computed, not hard-coded."""
    if not isinstance(sides,int) or sides < 3 or sides > 12: raise ValueError("Pyramid base must have 3 to 12 sides")
    if radius<=0 or height<=0 or not math.isfinite(float(radius)) or not math.isfinite(float(height)): raise ValueError("Radius and height must be positive finite numbers")
    r,h=float(radius),float(height)
    names=labels or [chr(65+i) for i in range(sides)] + ["S"]
    if len(names)!=sides+1 or len(set(names))!=len(names): raise ValueError("Need n unique base labels and one apex label")
    exact={names[i]:[r*math.cos(2*math.pi*i/sides),r*math.sin(2*math.pi*i/sides),0.0] for i in range(sides)}
    exact[names[-1]]=[0.0,0.0,h]
    points={k:[v[0]-0.45*v[1],v[2]+0.45*v[1]] for k,v in exact.items()}
    segments=[]; hidden=[]
    for i in range(sides):
        j=(i+1)%sides; edge=[names[i],names[j]]
        (hidden if math.sin(2*math.pi*(i+0.5)/sides)<-0.15 else segments).append(edge)
        segments.append([names[-1],names[i]])
    return _geom(points,segments,f"Hình chóp đều đáy {sides} cạnh, chiều cao {h:g}; hình chiếu xiên.",hidden_segments=hidden,coordinates_3d=exact,solid_dimensions={"base_sides":sides,"circumradius":r,"height":h},projection="oblique",diagram_mode="schematic_projection",constraints=[{"type":"regular_pyramid","base_sides":sides,"height":h}])
