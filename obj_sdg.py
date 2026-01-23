from isaacsim.simulation_app import SimulationApp
# "RayTracedLighting" → RTX Real-Time
# "PathTracing" → Path Tracer
simu_app = SimulationApp({"renderer": "PathTracing", "headless": True})

from isaacsim.core.utils import stage, prims
from sdg import Randomizer, Generator
from pathlib import Path

def find_usds(dir: str) -> list[str]:
    folder = Path(dir)
    usd_files = []
    for usd_file in folder.rglob("*.usd"):
        usd_files.append(str(usd_file))
    return usd_files

created_stage = stage.create_new_stage()
prims.create_prim("/World")

stage.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/full_warehouse.usd",
    prim_path="/World/Environment"
)
obj_prim_path = "/World/Obj"
stage.add_reference_to_stage(
    usd_path="/home/avent/Desktop/SimReadyExplorer/Warehouse/02/common_assets/props/pallet_asm/pallet_asm.usd",
    prim_path=obj_prim_path
)

randomizer = Randomizer(obj_prim_path, 10)
generator = Generator(randomizer, save_path="/home/avent/Desktop/generated_data")
generator.generate()

stage.close_stage()

simu_app.close()

