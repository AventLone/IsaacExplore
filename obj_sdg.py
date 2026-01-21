from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": True})

from isaacsim.core.utils import stage, prims
from sdg import Randomizer, Generator

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

# while simu_app.is_running():
#     simu_app.update()

simu_app.close()

