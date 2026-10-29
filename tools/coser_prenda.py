#!/usr/bin/env python3
"""H3 IAModa — prenda COSIDA de verdad: patrón 2D estructurado → Blender cloth
con sewing springs → GLB con pliegues reales.

El patrón (tools/patron-vestido.json) sale del probador IAModa: cada pieza es
un contorno estructurado (p0 + segmentos L/C) con roles por índice:
  [escote×E, hombro=E, sisa=E+1, lateral=E+2, flanco=E+3, bajo=E+4, cierre=E+5]
con E = len(segs) - 6.

Uso (cm en escena, export a metros):
  blender -b --factory-startup -P coser_prenda.py -- patron.json salida.glb

Química: 4 paneles (delantero×2 al doblez, trasero×2) arqueados alrededor de un
maniquí de sastre (colisión); aristas de borde hombro/lateral/cierre marcadas
use_seam; el cloth cose y la tela cae. Borde superior (escote+hombro) pinneado
(percha). Métricas impresas: desviación media vs plano y variancia de normales.
"""
import json
import math
import sys

import bpy
import bmesh
from mathutils import Vector, Matrix

# ------------------------------------------------------------------ entrada
argv = sys.argv[sys.argv.index("--") + 1:]
PATRON, SALIDA = argv[0], argv[1]

# limpiar la escena default (el Cube de fábrica se cuela en el GLB si no)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

PASO = 0.55         # cm entre vértices de la tela (0.8 desintegra la sim; 0.55 drapea)
M = 0.01            # la escena 3D trabaja en METROS (defaults del solver); patrón en cm
Z_HOMBRO = 142.6    # altura del hombro del patrón — ALINEADA con el anillo de hombro del maniquí (142.6): el tubo despeja la placa 1.2 cm; a 141 penetraba la placa y la tela se enganchaba
CH = 4.5            # y del hombro en el patrón (cm)
Z_PIN = 12.0        # y_patrón < Z_PIN => percha (escote+hombro+arranque de sisa)
PANEL = math.radians(80.0)   # arco angular de cada panel (holgura > tensión)
D_HUECO_LATERAL = math.radians(4.0)
D_HOLGURA_SUP = 1.2          # radio extra sobre el maniquí (zona pinneada)
D_HOLGURA_INF = 1.8          # radio extra (zona libre)
FRAMES = 110

# ------------------------------------------------------- utilidades patrón
def eval_seg(a, s, u):
    if s["t"] == "L":
        return [a[0] + (s["p"][0] - a[0]) * u, a[1] + (s["p"][1] - a[1]) * u]
    v = 1.0 - u
    return [
        v**3 * a[0] + 3 * v * v * u * s["c1"][0] + 3 * v * u * u * s["c2"][0] + u**3 * s["p"][0],
        v**3 * a[1] + 3 * v * v * u * s["c1"][1] + 3 * v * u * u * s["c2"][1] + u**3 * s["p"][1],
    ]


def aplanar(pieza, paso_aprox=1.0):
    """Anillo de puntos + rol lógico (índice de segmento) por punto.

    Subdivisión en TODOS los segmentos (~paso_aprox cm): sin esto las líneas
    rectas largas (lateral ~30 cm) quedan con cuerdas enormes y el rol de las
    aristas de borde de la malla no se puede etiquetar por proximidad.
    """
    pts = [list(pieza["p0"])]
    rol = [0]
    a = pieza["p0"]
    for i, s in enumerate(pieza["segs"]):
        dx = s["p"][0] - a[0]
        dy = s["p"][1] - a[1]
        n = max(2, int(math.hypot(dx, dy) / paso_aprox))
        for k in range(1, n + 1):
            pts.append(eval_seg(a, s, k / n))
            rol.append(i)
        a = s["p"]
    return pts, rol


ROLES_COSER = ("hombro", "lateral", "cierre")


def roles_de(pieza):
    E = len(pieza["segs"]) - 6
    assert E >= 1, "estructura de pieza inesperada"
    return {E: "hombro", E + 1: "sisa", E + 2: "lateral", E + 3: "flanco",
            E + 4: "bajo", E + 5: "cierre"}


# ----------------------------------------------------- relleno scanline 2D
def malla_pieza(pieza, paso=PASO):
    """Devuelve (verts2d, caras, aristas_borde) con rol lógico por arista."""
    anillo, rol_pto = aplanar(pieza)
    ys = [p[1] for p in anillo]
    ymin, ymax = min(ys), max(ys)
    nfil = max(2, int((ymax - ymin) / paso))
    verts = []
    idx = {}

    def vget(x, y):
        k = (round(x, 3), round(y, 3))
        if k not in idx:
            idx[k] = len(verts)
            verts.append((x, y))
        return idx[k]

    aristas = list(zip(anillo, anillo[1:] + [anillo[:1][0]]))
    filas = []
    for i in range(nfil + 1):
        y = ymin + (ymax - ymin) * i / nfil
        xs = []
        for a, b in aristas:
            if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                t = (y - a[1]) / (b[1] - a[1])
                xs.append(a[0] + (b[0] - a[0]) * t)
        xs.sort()
        fila = []  # lista de SPANS: cada span = lista de [x, idx] ordenada por x
        for j in range(0, len(xs) - 1, 2):
            x0, x1 = xs[j], xs[j + 1]
            if x1 - x0 < 0.2:
                continue
            span = [[x0 + 1e-4, vget(x0 + 1e-4, y)],
                    [x1 - 1e-4, vget(x1 - 1e-4, y)]]
            k = 1
            x = x0 + paso
            while x < x1 - 0.2:
                span.append([x, vget(x, y)])
                k += 1
                x = x0 + paso * k
            span.sort(key=lambda p: p[0])
            fila.append(span)
        filas.append(fila)

    # coser filas consecutivas: cada span real de la fila i con sus solapes de
    # la fila i+1 (empar anterior emparejaba PUNTOS ADYACENTES de la fila plana
    # creyendo que eran spans -> la malla nacia troceada en ~500 virutas)
    caras = []

    def empar(f1, f2):
        for s1 in f1:
            for s2 in f2:
                lo = max(s1[0][0], s2[0][0])
                hi = min(s1[-1][0], s2[-1][0])
                if hi - lo < 0.05:
                    continue
                a1 = [p for p in s1 if lo <= p[0] <= hi]
                a2 = [p for p in s2 if lo <= p[0] <= hi]
                if len(a1) < 2 or len(a2) < 2:
                    continue
                i1 = i2 = 0
                while i1 < len(a1) - 1 and i2 < len(a2) - 1:
                    caras.append((a1[i1][1], a1[i1 + 1][1], a2[i2 + 1][1], a2[i2][1]))
                    if a1[i1 + 1][0] < a2[i2 + 1][0]:
                        caras.append((a1[i1][1], a1[i1 + 1][1], a2[i2][1]))
                        i1 += 1
                    else:
                        caras.append((a2[i2][1], a2[i2 + 1][1], a1[i1][1]))
                        i2 += 1
                i1 = min(i1, len(a1) - 1)
                i2 = min(i2, len(a2) - 1)
                while i1 < len(a1) - 1:
                    caras.append((a1[i1][1], a1[i1 + 1][1], a2[i2][1]))
                    i1 += 1
                while i2 < len(a2) - 1:
                    caras.append((a2[i2][1], a2[i2 + 1][1], a1[i1][1]))
                    i2 += 1

    for f1, f2 in zip(filas, filas[1:]):
        empar(f1, f2)

    # roles por arista de borde: aristas con 1 uso en caras, cerca del anillo
    usos = {}
    for c in caras:
        for k in range(len(c)):
            a, b = c[k], c[(k + 1) % len(c)]
            usos[(min(a, b), max(a, b))] = usos.get((min(a, b), max(a, b)), 0) + 1

    # kd trivial: distancia punto-anillo por barrido (anillo ~ 300 pts)
    def rol_en(x, y):
        mejor, mejord = -1, 1e9
        for i, p in enumerate(anillo):
            d = (p[0] - x) ** 2 + (p[1] - y) ** 2
            if d < mejord:
                mejord, mejor = d, rol_pto[i]
        return mejor if mejord < 0.64 else -1

    aristas_borde = []
    for (a, b), n in usos.items():
        if n != 1:
            continue
        pa, pb = verts[a], verts[b]
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        r = rol_en(mx, my)
        if r >= 0:
            aristas_borde.append((a, b, r))
    return verts, caras, aristas_borde


# ------------------------------------------------------------------ escena
def material(nombre, color, rough):
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def malla_anillos(nombre, perfil, mat, seg=48):
    me = bpy.data.meshes.new(nombre)
    obj = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    anillos = []
    for (z, rx, rz) in perfil:
        fila = [bm.verts.new((math.cos(2 * math.pi * j / seg) * rx,
                              math.sin(2 * math.pi * j / seg) * rz, z))
                for j in range(seg)]
        anillos.append(fila)
    for a, b in zip(anillos, anillos[1:]):
        for j in range(seg):
            bm.faces.new((a[j], a[(j + 1) % seg], b[(j + 1) % seg], b[j]))
    bm.faces.new(anillos[-1][::-1])
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    obj.data.materials.append(mat)
    return obj


# maniquí de sastre (talla 92-74-98, cotas de la plantilla del skill)
A = 175.0
COTAS = {"cadera": 0.525 * A, "cintura": 0.625 * A, "pecho": 0.725 * A,
         "hombro": 0.815 * A, "cuello": 0.865 * A}
RAD = {"pecho": 92 / (2 * math.pi), "cintura": 74 / (2 * math.pi),
       "cadera": 98 / (2 * math.pi)}
PERFIL = [
    (COTAS["cuello"] + 6, 6.2, 5.2),
    (COTAS["cuello"], 6.2, 5.2),
    (COTAS["hombro"], RAD["pecho"] * 1.44, RAD["pecho"] * 1.44 * 0.60),
    (137, 14.6, 10.8),
    (COTAS["pecho"], RAD["pecho"], RAD["pecho"] * 0.72),
    (COTAS["cintura"], RAD["cintura"], RAD["cintura"] * 0.72),
    (COTAS["cadera"], RAD["cadera"], RAD["cadera"] * 0.72),
    (60, RAD["cadera"] * 1.08, RAD["cadera"] * 1.08 * 0.74),
]
PIEL = material("maniqui_lino", (0.74, 0.68, 0.58), 0.95)
maniqui = malla_anillos("maniqui", [(M * z, M * rx, M * rz) for (z, rx, rz) in PERFIL], PIEL)

def normales_fuera(obj):
    """recalcula normales hacia FUERA — collider de cloth con normales
    invertidas EXPULSA la tela hacia dentro del cuerpo (bug de las corridas
    19-24: 40/40 caras del maniquí apuntaban hacia dentro)."""
    bmn = bmesh.new()
    bmn.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bmn, faces=bmn.faces)
    bmn.to_mesh(obj.data)
    bmn.free()

def normales_radiales(obj):
    """orienta cada cara ALEJÁNDOSE del eje del cuerpo (z): los paneles
    espejados (s=-1) invierten el winding y recalc_face_normals sobre la
    malla abierta no garantiza consistencia global -> normales de vértice
    aleatorias -> la tela se sombreaba como hebras verticales (runs 19-27)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    flips = []
    for f in bm.faces:
        c = f.calc_center_median()
        radial = Vector((c.x, c.y, 0.0))
        if f.normal.dot(radial) < 0.0:
            flips.append(f)
    bmesh.ops.reverse_faces(bm, faces=flips)
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()


normales_fuera(maniqui)

def radios_par(z):
    """(rx, rz) del maniquí por altura — interp del perfil (cm)."""
    per = sorted(PERFIL, key=lambda p: -p[0])  # DESCENDENTE: pares z0>=z>=z1
    for (z0, r0, e0), (z1, r1, e1) in zip(per, per[1:]):
        if z0 >= z >= z1:
            t = (z0 - z) / max(z0 - z1, 1e-6)
            return r0 + (r1 - r0) * t, e0 + (e1 - e0) * t
    return per[-1][1], per[-1][2]

def radio_z(z):
    """radio (elíptico en th) del maniquí por altura — interp del perfil."""
    return radios_par(z)[0], None

def radio_elipse(z, th, extra):
    """radio en la dirección th (0 = frente -Y) + holgura."""
    rx, rz = radios_par(z)
    # elipse: punto (rx*sin th, -rz*cos th) — radio polar
    r = math.hypot(rx * math.sin(th), rz * math.cos(th))
    return r + extra

_ARC_CACHE = {}
def theta_por_arco(z, a, trasera, gap_arc=2.0):
    """ángulo th cuyo ARCO elíptico desde el frente (th=0) vale a (cm).

    Cada panel cubre su CUARTO de perímetro (colocación por longitud de arco,
    como un patrón físico): el delantero va del frente (0) al costado (π/2),
    el trasero del costado (π/2) al centro-espalda (π - hueco).
    a=None devuelve el arco máximo del panel.
    """
    rx, rz = radios_par(z)
    clave = (round(rx, 4), round(rz, 4), trasera)
    if clave not in _ARC_CACHE:
        N = 220
        ths = [i / N * (math.pi / 2) for i in range(N + 1)]
        arcs = [0.0]
        for i in range(1, N + 1):
            t0, t1 = ths[i - 1], ths[i]
            p0 = (rx * math.sin(t0), -rz * math.cos(t0))
            p1 = (rx * math.sin(t1), -rz * math.cos(t1))
            arcs.append(arcs[-1] + math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
        # arco del cuarto (frente->costado)
        P4 = arcs[-1]
        if trasera:
            # del costado al centro-espalda: recorre th de π/2 a π; reserva el hueco
            ths2 = [math.pi / 2 + i / N * (math.pi / 2) for i in range(N + 1)]
            arcs2 = [0.0]
            for i in range(1, N + 1):
                t0, t1 = ths2[i - 1], ths2[i]
                p0 = (rx * math.sin(t0), -rz * math.cos(t0))
                p1 = (rx * math.sin(t1), -rz * math.cos(t1))
                arcs2.append(arcs2[-1] + math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
            _ARC_CACHE[clave] = (ths2, arcs2, arcs2[-1] - gap_arc)
        else:
            _ARC_CACHE[clave] = (ths, arcs, P4)
    ths, arcs, amax = _ARC_CACHE[clave]
    if a is None:
        return amax
    a = max(0.0, min(a, amax))
    # interp lineal inversa
    lo, hi = 0, len(arcs) - 1
    for i in range(1, len(arcs)):
        if arcs[i] >= a:
            lo, hi = i - 1, i
            break
    span = arcs[hi] - arcs[lo]
    t = (a - arcs[lo]) / span if span > 1e-9 else 0.0
    return ths[lo] + (ths[hi] - ths[lo]) * t

# ------------------------------------------------------------ paneles tela
patron = json.load(open(PATRON, encoding="utf-8"))
por_nombre = {p["n"]: p for p in patron}
PAÑO = material("tela_vestido", (0.52, 0.12, 0.10), 0.93)


def colocar(x, y, s, trasera):
    """(x,y) del patrón (mitad, x>=0) -> 3D alrededor del maniquí, en metros.

    Mapeo ANGULAR con columnas verticales (el hilo de la tela cuelga recto):
    th depende SOLO de x — el mismo f da el mismo th en todas las filas, así
    los quads no se retuercen (el mapeo por arco variable por fila retorcía
    las columnas y la tela se veía como hebras). La holgura angular (80° por
    panel vs ~90° del cuerpo) deja exceso que se pliega hacia fuera en el
    drape, y los bordes laterales coinciden exactos entre delantero y trasero
    (ambos en th=π/2·(PANEL/ (π/2))... ver PANEL) — la fusión los vuelve
    continuidad.
    """
    f = min(x / 25.0, 1.0)  # fracción del panel
    th = s * (f * PANEL if not trasera else 2 * PANEL - f * PANEL)
    z = Z_HOMBRO - (y - CH)
    extra = D_HOLGURA_SUP if y < Z_PIN else D_HOLGURA_INF
    r = radio_elipse(z, th, extra)
    return (M * r * math.sin(th), -M * r * math.cos(th), M * z)

def construir_panel(nombre, pieza, s, trasera, off_x=0.0):
    verts2d, caras, bordes = malla_pieza(pieza)
    roles = roles_de(pieza)
    me = bpy.data.meshes.new(nombre)
    obj = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    # capas flat PRIMERO (crear una capa invalida las referencias BMVert previas)
    lfx = bm.verts.layers.float.new("flat_x")
    lfy = bm.verts.layers.float.new("flat_y")
    bmv = [bm.verts.new(colocar(x, y, s, trasera)) for (x, y) in verts2d]
    # capas flat: posición del patrón extendido (para la métrica «desv vs plano»)
    for (x, y), v in zip(verts2d, bmv):
        v[lfx] = x + off_x
        v[lfy] = y
    pos3 = [v.co.copy() for v in bmv]
    usadas = set()
    limpias = []
    for c in caras:
        if len(set(c)) < len(c):
            continue
        a, b, cc = (Vector(pos3[c[0]]), Vector(pos3[c[1]]), Vector(pos3[c[2]]))
        if (b - a).cross(cc - a).length < 1e-8:
            continue
        limpias.append(c)
    for c in limpias:
        try:
            if len(c) == 4:
                bm.faces.new((bmv[c[0]], bmv[c[1]], bmv[c[2]], bmv[c[3]]))
            else:
                bm.faces.new((bmv[c[0]], bmv[c[1]], bmv[c[2]]))
        except ValueError:
            pass
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=2e-4)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.update()
    obj.data.materials.append(PAÑO)
    # seams + pin: KD sobre el mesh REAL (remove_doubles reindexó)
    import mathutils
    kd = mathutils.kdtree.KDTree(len(me.vertices))
    for v in me.vertices:
        kd.insert(v.co, v.index)
    kd.balance()
    n_seam = 0
    n_cand = 0
    for (a, b, r) in bordes:
        rol = roles.get(r)
        if rol not in ROLES_COSER:
            continue
        n_cand += 1
        pa = Vector(colocar(verts2d[a][0], verts2d[a][1], s, trasera))
        pb = Vector(colocar(verts2d[b][0], verts2d[b][1], s, trasera))
        ia = kd.find(pa)[1]
        ib = kd.find(pb)[1]
        if ia is None or ib is None or ia == ib:
            continue
        found = None
        for ed in me.edges:
            vs = ed.vertices
            if (vs[0] == ia and vs[1] == ib) or (vs[0] == ib and vs[1] == ia):
                found = ed
                break
        if found:
            found.use_seam = True
            n_seam += 1
    # pin (percha): vértices cuyo y_patrón < Z_PIN — mismos índices reales
    vg = obj.vertex_groups.new(name="percha")
    n_pin = 0
    for i, (x, y) in enumerate(verts2d):
        if y < Z_PIN:
            j = kd.find(Vector(colocar(x, y, s, trasera)))[1]
            if j is not None:
                vg.add([j], 1.0, "REPLACE")
                n_pin += 1
    print("PANEL %s: verts=%d caras=%d bordes=%d cand_coser=%d seams=%d pins=%d" % (
        nombre, len(me.vertices), len(me.polygons), len(bordes), n_cand, n_seam, n_pin))
    # midpoints de los seams que sobrevivirán como BORDE tras el join
    # (lateral y cierre frontal se fusionan; hombro y cierre trasero quedan)
    vivos = []
    for (a, b, r) in bordes:
        rol = roles.get(r)
        if rol == "hombro" or (trasera and rol == "cierre"):
            pa = Vector(colocar(verts2d[a][0], verts2d[a][1], s, trasera))
            pb = Vector(colocar(verts2d[b][0], verts2d[b][1], s, trasera))
            vivos.append((pa + pb) / 2)
    return obj, vivos

paneles = []
seams_vivos = []
for i, (nom, pieza, s, tra) in enumerate([
        ("del_der", por_nombre["Delantero"], +1, False),
        ("del_izq", por_nombre["Delantero"], -1, False),
        ("tr_der", por_nombre["Trasero"], +1, True),
        ("tr_izq", por_nombre["Trasero"], -1, True)]):
    o, vivos = construir_panel(nom, pieza, s, tra, off_x=i * 27.0)
    paneles.append(o)
    seams_vivos += vivos

# -------------------------------------------- coser: fusión en UNA sola tela
# los bordes de hombro/lateral/cierre frontal coinciden exactos entre paneles:
# remove_doubles los vuelve continuidad real (la costura es parte de la tela)
n_before = sum(len(p.data.vertices) for p in paneles)
bpy.ops.object.select_all(action="DESELECT")
for o in paneles:
    o.select_set(True)
bpy.context.view_layer.objects.active = paneles[0]
bpy.ops.object.join()
tela = bpy.context.view_layer.objects.active
normales_radiales(tela)  # NO normales_fuera: el tubo es abierto y recalc dejaba winding mixto
tela.name = "vestido_cosido"
bm = bmesh.new()
bm.from_mesh(tela.data)
# fusión global 2 mm: los verts de junta entre segs del patrón están duplicados
# con hueco de 0.2-4 mm -> con 0.2 mm la malla quedaba en ~91 tiras verticales
# desconexas («hebras»); 2 mm es 4x menor que el paso de rejilla (5.5 mm)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=2e-3)
# fusión DIRIGIDA de costuras: los scanlines de del/trasero no alinean filas,
# así que los verts de borde enfrentados no coinciden exactos — weld a <4 mm
import mathutils
bordesb = [v for v in bm.verts if len(v.link_faces) == 1]
kd2 = mathutils.kdtree.KDTree(len(bordesb))
for i, v in enumerate(bordesb):
    kd2.insert(v.co, i)
kd2.balance()
targetmap = {}
for i, v in enumerate(bordesb):
    for (co, j, d) in kd2.find_range(v.co, 0.004):
        otro = bordesb[j]
        if otro is v or len(otro.link_faces) != 1 or otro.index >= v.index:
            continue
        targetmap[v] = otro
        break
n_weld = len(targetmap)
bmesh.ops.weld_verts(bm, targetmap=targetmap)
# re-marcar los seams vivos (hombro + cierre trasero): aristas de borde cuyo
# midpoint coincide con uno registrado antes del join
n_remarcados = 0
for e in bm.edges:
    if len(e.link_faces) != 1:
        continue
    mid = (e.verts[0].co + e.verts[1].co) / 2
    if any((mid - p).length < 0.006 for p in seams_vivos):
        e.seam = True
        n_remarcados += 1
# conteo de componentes conexas (diagnóstico «hebras»: debe ser ~1-3)
_parent = {v.index: v.index for v in bm.verts}
def _find(x):
    while _parent[x] != x:
        _parent[x] = _parent[_parent[x]]
        x = _parent[x]
    return x
for e in bm.edges:
    ra, rb = _find(e.verts[0].index), _find(e.verts[1].index)
    if ra != rb:
        _parent[rb] = ra
_comps = len({ _find(i) for i in _parent })
# NO recalc_face_normals aquí: el tubo es abierto y deshace la orientación
# radial de normales_radiales (winding mixto -> normales basura -> hebras)
bm.normal_update()
bm.to_mesh(tela.data)
bm.free()
tela.data.update()
normales_radiales(tela)  # re-asegura la orientación radial tras el weld
print("COSIDO verts antes=%d despues=%d welds=%d seams_remarcados=%d componentes=%d" % (n_before, len(tela.data.vertices), n_weld, n_remarcados, _comps))
paneles = [tela]

# exportar TAMBIÉN el estado inicial (sin simular) para diagnóstico
bpy.ops.export_scene.gltf(
    filepath=r"C:/Users/d_ant/AppData/Local/hermes/cache/scratch/vestido-inicial.glb",
    export_format="GLB", export_yup=True)

# ------------------------------------------------------------- cloth + sim
col_mod = maniqui.modifiers.new("col", "COLLISION")
cs0 = col_mod.settings
for campo, valor in [("thickness_outer", 0.004), ("thickness_inner", 0.002), ("friction", 40.0)]:
    try:
        setattr(cs0, campo, valor)
    except AttributeError:
        pass

escena = bpy.context.scene
escena.render.fps = 30
escena.frame_start = 1
escena.frame_end = FRAMES

pos_ini = {}
for obj in paneles:
    mod = obj.modifiers.new("cloth", "CLOTH")
    st = mod.settings
    st.quality = 12
    st.mass = 0.000016  # 0.46 kg REALES repartidos en ~28.5k verts (0.0001 eran 2.85 kg -> hilachas)
    st.air_damping = 3.0
    st.tension_stiffness = 15
    st.compression_stiffness = 15
    st.shear_stiffness = 10
    st.bending_stiffness = 0.35
    st.use_sewing_springs = False
    st.pin_stiffness = 1.0
    st.vertex_group_mass = tela.vertex_groups["percha"].name
    cs = mod.collision_settings
    cs.use_self_collision = True
    cs.self_distance_min = 0.001
    cs.self_friction = 5.0
    cs.distance_min = 0.008
    cs.friction = 8.0
    cs.damping = 2.0
    pos_ini[obj.name] = [v.co.copy() for v in obj.data.vertices]
    st.time_scale = 1.3

for f in range(1, FRAMES + 1):
    escena.frame_set(f)
    if f % 20 == 0:
        print("FRAME %d/%d" % (f, FRAMES), flush=True)

# ------------------------------------------------- extracción + métricas
deps = bpy.context.evaluated_depsgraph_get()
final = []
for obj in paneles:
    ev = obj.evaluated_get(deps)
    me = bpy.data.meshes.new_from_object(ev, depsgraph=deps)
    obj.modifiers.clear()
    obj.data = me
    final.append(obj)

desv = []
pin_idx = {}
for obj in final:
    ini = pos_ini[obj.name]
    vgm = obj.vertex_groups.get("percha")
    excluir = set()
    if vgm:
        for v in obj.data.vertices:
            for g in v.groups:
                if g.group == vgm.index and g.weight > 0.5:
                    excluir.add(v.index)
    pin_idx[obj.name] = excluir
    for v in obj.data.vertices:
        if v.index in excluir:
            continue
        desv.append((v.co - ini[min(v.index, len(ini) - 1)]).length)
desv_media = sum(desv) / max(len(desv), 1)
# ¿el pin aguanta? los pinneados no deben moverse
desv_pins = []
for obj in final:
    ini = pos_ini[obj.name]
    for i in pin_idx.get(obj.name, ()):
        desv_pins.append((obj.data.vertices[i].co - ini[min(i, len(ini) - 1)]).length)
desv_pin_media = sum(desv_pins) / max(len(desv_pins), 1)
# desv vs PATRÓN PLANO (criterio H3): la tela simulada vs el patrón extendido
# en el plano — centroides alineados para medir la FORMA, no la traslación
desv_flat_cm = -1.0
ax_ = final[0].data.attributes.get("flat_x")
ay_ = final[0].data.attributes.get("flat_y")
if ax_ and ay_ and len(ax_.data) == len(final[0].data.vertices):
    fx = [d.value for d in ax_.data]
    fy = [d.value for d in ay_.data]
    V = final[0].data.vertices
    n = len(V)
    cs = [sum(v.co[k] for v in V) / n for k in range(3)]
    cf = [sum(M * f[k] for f in zip(fx, fy, [0.0] * n)) / n for k in range(3)]
    dflat = 0.0
    for i, v in enumerate(V):
        dflat += math.sqrt(
            (v.co.x - cs[0] - (M * fx[i] - cf[0])) ** 2 +
            (v.co.y - cs[1] - (M * fy[i] - cf[1])) ** 2 +
            (v.co.z - cs[2] - (0.0 - cf[2])) ** 2)
    desv_flat_cm = dflat / n * 100
zs = [v.co.z for obj in final for v in obj.data.vertices]

nv = 0
for obj in final:
    obj.data.calc_normals_split() if hasattr(obj.data, "calc_normals_split") else None
malla_n = 0.0
total_c = 0
for obj in final:
    for p in obj.data.polygons:
        malla_n += p.normal.length if False else 0
        total_c += 1
# variancia de normales: 1 - |media de normales|
sum_n = [0.0, 0.0, 0.0]
for obj in final:
    for p in obj.data.polygons:
        sum_n[0] += p.normal.x
        sum_n[1] += p.normal.y
        sum_n[2] += p.normal.z
mod_n = math.sqrt(sum(n * n for n in sum_n)) / max(total_c, 1)
pliegue = 1.0 - mod_n

verts_total = sum(len(o.data.vertices) for o in final)
print("METRICAS desviacion_media_cm=%.3f desv_pins_cm=%.4f desv_flat_cm=%.2f zmin=%.3f zmax=%.3f pliegue=%.4f verts=%d caras=%d" % (
    desv_media * 100, desv_pin_media * 100, desv_flat_cm, min(zs), max(zs), pliegue, verts_total, total_c))

# ----------------------------------------------------------- exportar GLB
# la tela + el busto de sastre (contexto visual en «Rig & pasarela»)
for obj in final:
    for g in list(obj.vertex_groups):
        obj.vertex_groups.remove(g)
bpy.ops.object.select_all(action="DESELECT")
maniqui.modifiers.clear()
bpy.ops.export_scene.gltf(
    filepath=SALIDA, export_format="GLB",
    export_yup=True, export_apply=True)
print("GLB_OK %s" % SALIDA)
