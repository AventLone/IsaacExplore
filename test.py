# from pathlib import Path

# def find_usds(dir: str) -> list[str]:
#     folder = Path(dir)
#     usd_files = []
#     for usd_file in folder.rglob("*.usd"):
#         usd_files.append(str(usd_file))
#     return usd_files

# print(find_usds("/home/avent/Desktop/SimReadyExplorer/Industrial/Pallets"))


from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": False})

import random, pathlib
from sdg.sample import PermuAndCombi
from isaacsim.core.utils import stage, prims
from sdg.randomizer.RVF import example
from sdg.randomizer import stack_boxes_on_pallet_async
from sdg import common
from omni.kit.async_engine import run_coroutine

created_stage = stage.create_new_stage()
prims.create_prim("/World")

# environment_prim_path = "/World/Environment"
# stage.add_reference_to_stage(
#     usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
#     prim_path=environment_prim_path
# )
# common.set_world_trasform(prim=environment_prim_path, translation=[-6.7, 5.5, 0.0], orientation=common.yaw2quat(180.0))

def find_usds(dir: str) -> list[str]:
    folder = pathlib.Path(dir)
    usd_files = []
    for usd_file in folder.rglob("*.usd"):
        usd_files.append(str(usd_file))
    return usd_files

def load_usds(dir: str | list[str], objs_prim_path="/World/Objs") -> list[str]:
    """
    Load USDs from a folder into the stage
    """
    usd_file_paths = find_usds(dir) if type(dir) is str else dir
    obj_prim_paths = []
    idx = 0
    for file_path in usd_file_paths:
        idx += 1
        obj_prim_path = f"{objs_prim_path}/obj{idx}"
        obj_prim_paths.append(obj_prim_path)
        stage.add_reference_to_stage(usd_path=file_path, prim_path=obj_prim_path)
    return obj_prim_paths




objs_prim_path = "/World/Obj"
stage.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Props/pallet_eu.usd",
    # usd_path="/home/avent/Desktop/IsaacAssets/Props/KKP.usd",
    prim_path=objs_prim_path
)

# obj_prim_paths = load_usds(dir="jj")

boxes_urls_and_weights = [
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxA_01.usd", 0.02),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01.usd", 0.06),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxC_01.usd", 0.12),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01.usd", 0.80),
]
# simu_app.run_coroutine(pca.run(colomns=6, rows=6))
# simu_app.run_coroutine(pca.run_stack_boxes(colomns=6, boxes_urls_and_weights=boxes_urls_and_weights))
pca = PermuAndCombi([objs_prim_path])
simu_app.run_coroutine(pca.line_up(colomns=6, rows=6, gap=0, direction='x'))

# for col in pca.colomn_prims:
#     num_boxes = random.randint(10, 70)
#     run_coroutine(stack_boxes_on_pallet_async(pallet_prim=col,
#                                               boxes_urls_and_weights=boxes_urls_and_weights,
#                                               num_boxes=num_boxes, overhang=0.1))

# environment_url = "/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd"
# simu_app.run_coroutine(example())

while simu_app.is_running():
    simu_app.update()

simu_app.close()