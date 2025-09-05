# Isaac Sim 5.0 + omni.replicator.core 1.12.x
# 仓库货架 + 托盘 + 随机箱子 + 随机灯光 + 相机扫视
# 导出：RGB + 语义分割（class）

import os, math, random
random.seed(2025)

HEADLESS = False
OUT_DIR = "/tmp/warehouse_randomization_out"
NUM_SCENES = 20
RESOLUTION = (1280, 720)

# 资产路径（请根据你安装的 Isaac 资产库调整为真实存在的 USD）
SHELF_USD  = "/home/vn/IsaacSim5.0/IsaacSimAssets/Assets/Isaac/5.0/Isaac/Environments/Simple_Warehouse/Props/SM_RackShelf_01.usd"      # 货架
PALLET_USD = "/home/vn/IsaacSim5.0/IsaacSimAssets/Assets/Isaac/5.0/Isaac/Props/Pallet/pallet.usd"          # 托盘
BOX_USDS   = [
    "/home/vn/IsaacSim5.0/IsaacSimAssets/Assets/Isaac/5.0/Isaac/Props/Pallet/o3dyn_pallet.usd",
    "/home/vn/IsaacSim5.0/IsaacSimAssets/Assets/Isaac/5.0/Isaac/Props/Dolly/dolly_physics.usd",
]

AREA_X, AREA_Y = (-8.0, 8.0), (-8.0, 8.0)
Z_FLOOR = 0.0

NUM_SHELVES = 4
NUM_PALLETS = 10
NUM_BOXES   = 60

from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": HEADLESS})

import omni.usd
from pxr import Usd, UsdGeom, Gf
import omni.replicator.core as rep
from omni.isaac.core.utils.stage import add_reference_to_stage

ctx = omni.usd.get_context()
stage = ctx.get_stage()
if not stage.GetPrimAtPath("/World"):
    stage.DefinePrim("/World", "Xform")

# 地面（占位）
if not stage.GetPrimAtPath("/World/GroundPlane"):
    ground = UsdGeom.Mesh.Define(stage, "/World/GroundPlane")
    xform = UsdGeom.XformCommonAPI(ground.GetPrim())
    xform.SetScale(Gf.Vec3f(100.0, 100.0, 1.0))
    xform.SetTranslate(Gf.Vec3d(0.0, 0.0, Z_FLOOR))

def add_ref(usdz_path: str, prim_path: str):
    add_reference_to_stage(usdz_path, prim_path)
    return stage.GetPrimAtPath(prim_path)

def set_pose(prim, t_xyz=(0,0,0), r_euler_deg=(0,0,0), s_xyz=(1,1,1)):
    x = UsdGeom.XformCommonAPI(prim)
    x.SetTranslate(Gf.Vec3d(*t_xyz))
    x.SetRotate(Gf.Vec3f(*r_euler_deg), UsdGeom.XformCommonAPI.RotationOrderXYZ)
    x.SetScale(Gf.Vec3f(*s_xyz))

def add_semantics_with_rep(prim_path: str, class_name: str):
    p = rep.get.prims(path_pattern=prim_path)   # 5.0/1.12.x 用 path_pattern
    if not p:
        print(f"[warn] prim not found for semantics: {prim_path}")
        return
    with p:
        rep.modify.semantics([("class", class_name)])

def rand_xy(margin=0.5):
    return (random.uniform(AREA_X[0]+margin, AREA_X[1]-margin),
            random.uniform(AREA_Y[0]+margin, AREA_Y[1]-margin))

# ===== 货架（两列） =====
shelf_paths = []
cols = 2
rows = max(1, NUM_SHELVES // cols)
col_x = [-5.5, 5.5]
row_y_span = 10.0

for ci in range(cols):
    for ri in range(rows):
        idx = ci * rows + ri
        if idx >= NUM_SHELVES:
            break
        prim_path = f"/World/Warehouse/Shelf_{idx:02d}"
        prim = add_ref(SHELF_USD, prim_path)
        y = (ri - (rows - 1) / 2.0) * (row_y_span / max(1, rows - 1)) if rows > 1 else 0.0
        set_pose(prim, (col_x[ci], y, Z_FLOOR), (0, 0, 0), (1, 1, 1))
        add_semantics_with_rep(prim_path, "shelf")
        shelf_paths.append(prim_path)

# ===== 托盘随机（记录中心坐标，后面直接用） =====
pallet_paths = []
pallet_centers = {}  # prim_path -> (x, y, z)
for i in range(NUM_PALLETS):
    prim_path = f"/World/Warehouse/Pallet_{i:03d}"
    prim = add_ref(PALLET_USD, prim_path)
    x, y = rand_xy(margin=1.5)
    yaw = random.uniform(-180.0, 180.0)
    set_pose(prim, (x, y, Z_FLOOR), (0, 0, yaw))
    add_semantics_with_rep(prim_path, "pallet")
    pallet_paths.append(prim_path)
    pallet_centers[prim_path] = (x, y, Z_FLOOR)  # <-- 关键：记录位置

# ===== 箱子随机（部分放托盘上） =====
box_paths = []
for i in range(NUM_BOXES):
    usd = random.choice(BOX_USDS)
    prim_path = f"/World/Warehouse/Box_{i:04d}"
    prim = add_ref(usd, prim_path)

    on_pallet = (random.random() < 0.7) and pallet_paths
    if on_pallet:
        base_path = random.choice(pallet_paths)
        px, py, pz = pallet_centers[base_path]  # 直接用记录的托盘中心
        x = px + random.uniform(-0.4, 0.4)
        y = py + random.uniform(-0.4, 0.4)
        z = Z_FLOOR + 0.15  # 简单估计托盘上表面高度
    else:
        x, y = rand_xy(margin=1.0)
        z = Z_FLOOR

    yaw = random.uniform(-180.0, 180.0)
    s  = random.uniform(0.8, 1.2)
    set_pose(prim, (x, y, z), (0, 0, yaw), (s, s, s))
    add_semantics_with_rep(prim_path, "box")
    box_paths.append(prim_path)

# ===== 随机灯光 =====
@rep.randomizer
def random_lights(k=4):
    lights = rep.create.light(
        light_type=rep.distribution.choice(["Sphere", "Rect", "Disk"]),
        intensity=rep.distribution.uniform(400, 2200),
        temperature=rep.distribution.uniform(3600, 6500),
        count=k,
    )
    with lights:
        rep.modify.pose(
            position=rep.distribution.uniform(
                (AREA_X[0], AREA_Y[0], 2.5), (AREA_X[1], AREA_Y[1], 6.0)
            )
        )
    return lights

# ===== 相机扫视 =====
camera = rep.create.camera()
render_product = rep.create.render_product(camera, RESOLUTION)

center = Gf.Vec3d(0.0, 0.0, 1.2)
radius = 12.0
heights = (2.0, 3.5)

def camera_pose_by_t(t: float):
    ang = 2 * math.pi * t
    x = center[0] + radius * math.cos(ang)
    y = center[1] + radius * math.sin(ang)
    z = random.uniform(*heights)
    yaw_deg   = math.degrees(math.atan2(center[1] - y, center[0] - x))
    pitch_deg = -10.0
    return (x, y, z), (pitch_deg, 0.0, yaw_deg)

@rep.randomizer
def camera_sweep(frame_idx, total=NUM_SCENES):
    t = (frame_idx % total) / float(total)
    (x, y, z), (rx, ry, rz) = camera_pose_by_t(t)
    with camera:
        rep.modify.pose(position=(x, y, z), rotation=(rx, ry, rz))
    return camera

# ===== Writer =====
os.makedirs(OUT_DIR, exist_ok=True)
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir=OUT_DIR,
    rgb=True,
    semantic_segmentation=True,  # class 分割
    # 需要再加：instance_segmentation=True, bounding_box_2d_tight=True, ...
)
writer.attach([render_product])

# ===== 触发 + 执行 =====
with rep.trigger.on_frame(num_frames=NUM_SCENES):
    random_lights(k=4)
    camera_sweep(frame_idx=rep.distribution.sequence(0, NUM_SCENES - 1))

rep.orchestrator.run_until_complete()

simulation_app.close()
print(f"[DONE] Images & labels saved to: {OUT_DIR}")
