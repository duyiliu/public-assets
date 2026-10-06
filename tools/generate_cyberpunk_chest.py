from pathlib import Path
import math
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "cyberpunk_chest_v2.glb"
OUT.parent.mkdir(parents=True, exist_ok=True)

def pbr(color, metallic=0.0, roughness=0.5, emissive=None):
    kwargs = {
        "baseColorFactor": np.array(color, dtype=np.uint8),
        "metallicFactor": float(metallic),
        "roughnessFactor": float(roughness),
    }
    try:
        if emissive is not None:
            kwargs["emissiveFactor"] = np.array(emissive, dtype=float)
        return trimesh.visual.material.PBRMaterial(**kwargs)
    except TypeError:
        kwargs.pop("emissiveFactor", None)
        material = trimesh.visual.material.PBRMaterial(**kwargs)
        if emissive is not None:
            try:
                material.emissiveFactor = np.array(emissive, dtype=float)
            except Exception:
                pass
        return material

M_DARK  = pbr([22, 25, 31, 255], metallic=0.88, roughness=0.28)
M_GUN   = pbr([56, 61, 70, 255], metallic=0.82, roughness=0.32)
M_STEEL = pbr([108, 112, 118, 255], metallic=0.92, roughness=0.22)
M_BLACK = pbr([7, 9, 12, 255], metallic=0.65, roughness=0.38)
M_CYAN  = pbr([0, 220, 255, 255], metallic=0.2, roughness=0.12, emissive=[0.0, 0.8, 1.0])
M_MAG   = pbr([255, 36, 190, 255], metallic=0.2, roughness=0.12, emissive=[1.0, 0.0, 0.55])

scene = trimesh.Scene()

def add(mesh, name, material):
    mesh.visual.material = material
    scene.add_geometry(mesh, node_name=name)
    return mesh

def box(name, size, pos, material, transform=None):
    mesh = trimesh.creation.box(extents=size)
    if transform is not None:
        mesh.apply_transform(transform)
    mesh.apply_translation(pos)
    return add(mesh, name, material)

def cyl(name, radius, height, pos, material, axis="z", sections=48):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == "x":
        mesh.apply_transform(rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == "y":
        mesh.apply_transform(rotation_matrix(math.pi / 2, [1, 0, 0]))
    mesh.apply_translation(pos)
    return add(mesh, name, material)

def ring(name, r1, r2, depth, pos, material, axis="y", sections=64):
    mesh = trimesh.creation.annulus(r_min=r1, r_max=r2, height=depth, sections=sections)
    if axis == "x":
        mesh.apply_transform(rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == "y":
        mesh.apply_transform(rotation_matrix(math.pi / 2, [1, 0, 0]))
    mesh.apply_translation(pos)
    return add(mesh, name, material)

# Main shell
box("LowerShell", [3.4, 2.0, 1.18], [0, 0, 0.62], M_DARK)
box("FrontInset", [2.7, 0.10, 0.72], [0, -1.055, 0.64], M_BLACK)
box("RearInset", [2.7, 0.10, 0.62], [0, 1.055, 0.60], M_BLACK)

for side in (-1, 1):
    x = side * 1.73
    box(f"SideArmor_{side}", [0.16, 1.62, 0.92], [x, 0, 0.67], M_GUN)
    box(f"SideRailTop_{side}", [0.12, 1.84, 0.12], [x, 0, 1.13], M_STEEL)
    box(f"SideRailBottom_{side}", [0.12, 1.84, 0.12], [x, 0, 0.20], M_STEEL)

for x in (-1.62, 1.62):
    for y in (-0.92, 0.92):
        box(f"Corner_{x}_{y}", [0.26, 0.26, 1.14], [x, y, 0.62], M_STEEL)
        box(f"CornerCap_{x}_{y}", [0.34, 0.34, 0.16], [x, y, 1.17], M_GUN)

for x in (-1.45, 1.45):
    for y in (-0.75, 0.75):
        box(f"Foot_{x}_{y}", [0.34, 0.34, 0.16], [x, y, 0.05], M_BLACK)

for x in (-0.72, 0.72):
    box(f"FrontPanel_{x}", [0.98, 0.12, 0.58], [x, -1.12, 0.59], M_GUN)
    for i in range(5):
        box(f"Vent_{x}_{i}", [0.72, 0.035, 0.038], [x, -1.195, 0.43 + i * 0.075], M_BLACK)

# Lock + neon
box("LockBase", [0.68, 0.22, 0.68], [0, -1.16, 0.70], M_STEEL)
ring("LockOuter", 0.20, 0.31, 0.16, [0, -1.30, 0.70], M_GUN, axis="y")
ring("LockGlowRing", 0.10, 0.19, 0.18, [0, -1.385, 0.70], M_CYAN, axis="y")
cyl("LockCore", 0.09, 0.20, [0, -1.40, 0.70], M_MAG, axis="y")
box("FrontCyanLeft", [0.05, 0.035, 0.56], [-1.17, -1.22, 0.68], M_CYAN)
box("FrontCyanRight", [0.05, 0.035, 0.56], [1.17, -1.22, 0.68], M_CYAN)
box("FrontMagenta", [1.55, 0.035, 0.055], [0, -1.22, 1.02], M_MAG)

# Side handles
for side in (-1, 1):
    x = side * 1.92
    box(f"HandleBracketA_{side}", [0.12, 0.20, 0.40], [x, -0.34, 0.56], M_STEEL)
    box(f"HandleBracketB_{side}", [0.12, 0.20, 0.40], [x, 0.34, 0.56], M_STEEL)
    cyl(f"HandleBar_{side}", 0.075, 0.68, [x, 0, 0.56], M_GUN, axis="y")

# Lid
lid_angle = math.radians(-10)
lid_pivot = [0, 0.86, 1.20]
lid_rot = rotation_matrix(lid_angle, [1, 0, 0], point=lid_pivot)

lid = trimesh.creation.box(extents=[3.46, 2.02, 0.62])
lid.apply_translation([0, 0.00, 1.53])
lid.apply_transform(lid_rot)
add(lid, "LidShell", M_DARK)

for x in (-1.05, 0, 1.05):
    top = trimesh.creation.box(extents=[0.90, 1.45, 0.10])
    top.apply_translation([x, 0.02, 1.86])
    top.apply_transform(lid_rot)
    add(top, f"TopPlate_{x}", M_GUN if x else M_BLACK)

emblem = trimesh.creation.cylinder(radius=0.30, height=0.07, sections=6)
emblem.apply_translation([0, -0.08, 1.94])
emblem.apply_transform(lid_rot)
add(emblem, "TopEmblem", M_CYAN)

for x in (-1.48, 1.48):
    rail = trimesh.creation.box(extents=[0.12, 1.70, 0.11])
    rail.apply_translation([x, 0.03, 1.88])
    rail.apply_transform(lid_rot)
    add(rail, f"TopRail_{x}", M_STEEL)

for x, material in [(-1.18, M_MAG), (1.18, M_CYAN)]:
    strip = trimesh.creation.box(extents=[0.055, 1.55, 0.07])
    strip.apply_translation([x, -0.02, 1.91])
    strip.apply_transform(lid_rot)
    add(strip, f"LidGlow_{x}", material)

for x in (-1.32, 1.32):
    clamp = trimesh.creation.box(extents=[0.32, 0.30, 0.24])
    clamp.apply_translation([x, -0.85, 1.65])
    clamp.apply_transform(lid_rot)
    add(clamp, f"Clamp_{x}", M_STEEL)

for x in (-1.05, 1.05):
    cyl(f"Hinge_{x}", 0.13, 0.46, [x, 1.10, 1.22], M_STEEL, axis="x")
    cyl(f"HingePin_{x}", 0.07, 0.56, [x, 1.10, 1.22], M_BLACK, axis="x")

for x in (-1.35, 1.35):
    box(f"RearLatch_{x}", [0.24, 0.10, 0.50], [x, 1.13, 0.70], M_STEEL)

for x in (-1.55, 1.55):
    box(f"NeonFoot_{x}", [0.16, 0.10, 0.10], [x, -0.92, 0.14], M_MAG if x < 0 else M_CYAN)

scene.metadata["name"] = "Cyberpunk Loot Chest v2"
scene.metadata["description"] = "Hard-surface cyberpunk chest with layered armor and emissive accents."

OUT.write_bytes(scene.export(file_type="glb"))
print(f"generated {OUT} ({OUT.stat().st_size} bytes, {len(scene.geometry)} geometry objects)")
