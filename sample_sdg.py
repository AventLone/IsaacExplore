from isaacsim.simulation_app import SimulationApp
# "RayTracedLighting" → RTX Real-Time
# "PathTracing" → Path Tracer
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": True})
# simu_app.run_coroutine()

from pathlib import Path
from sdg.sample import CircleSampler
from sdg import Sampler
from isaacsim.core.utils import stage, prims

def find_usds(dir: str) -> list[str]:
    folder = Path(dir)
    usd_files = []
    for usd_file in folder.rglob("*.usd"):
        usd_files.append(str(usd_file))
    return usd_files


created_stage = stage.create_new_stage()
prims.create_prim("/World")

stage.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
    prim_path="/World/Environment"
)
obj_prim_path = "/World/Obj"
stage.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Props/KKP.usd",
    prim_path=obj_prim_path
)

randomizer = CircleSampler(obj_prim_path)
generator = Sampler(randomizer, img_resolution=(504, 504), save_path="/home/avent/Desktop/generated_data")
generator.generate()
stage.close_stage()
simu_app.close()
