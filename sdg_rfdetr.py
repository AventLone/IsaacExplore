from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": True})

from omni.kit.async_engine import run_coroutine
from isaacsim.core.utils import stage as stage_utils, prims as prims_utils
from sdg import common
from sdg.instance_seg_sdg import SDG


FORK_CAMERA_HEIGHT = 0.75
CAMERA_HEIGHT_TRAIN, CAMERA_HEIGHT_VAL = 0.75, 1.0
CAMERA_RADIUSES_TRAIN = [2.2, 3.2, 4.2]
CAMERA_RADIUSES_VAL = [3.0]
PALLET_WITH_GOODS_COLUMNS = 10


created_stage = stage_utils.create_new_stage()
prims_utils.create_prim("/World")

environment_prim_path = "/World/Environment"
stage_utils.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
    prim_path=environment_prim_path
)
common.set_world_trasform(prim=environment_prim_path, translation=[-7.6, 4.85, 0.0], orientation=common.yaw2quat(90.0))

boxes_urls_and_weights = [
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxA_01.usd", 0.02),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01.usd", 0.06),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxC_01.usd", 0.12),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01.usd", 0.80),
]

sdg_train = SDG(obj_urls_dir="/home/avent/Desktop/pallets", 
                boxes_urls_and_weights=boxes_urls_and_weights,
                img_resolution=(504, 504), 
                stacking_cols=5, stacking_rows=6, 
                camera_height=CAMERA_HEIGHT_TRAIN, camera_orbit_radiuses=CAMERA_RADIUSES_TRAIN,
                pallet_with_goods_count=10,
                save_path="/home/avent/Desktop/generated_data/train")

# sdg_val = SDG(obj_urls_dir="/home/avent/Desktop/pallets", 
#                 boxes_urls_and_weights=boxes_urls_and_weights,
#                 img_resolution=(504, 504), 
#                 stacking_cols=3, stacking_rows=3, 
#                 camera_height=CAMERA_HEIGHT_VAL, camera_orbit_radiuses=CAMERA_RADIUSES_VAL,
#                 pallet_with_goods_count=2,
#                 save_path="/home/avent/Desktop/generated_data/valid")

simu_app.run_coroutine(sdg_train.generate(sample_interval=2))
# simu_app.run_coroutine(sdg_val.generate(sample_interval=5))
simu_app.close()
