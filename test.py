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

from sdg.sample import PermuAndCombi
from isaacsim.core.utils import stage, prims
from sdg.randomizer.RVF import run_box_stacking_scenarios_async

# created_stage = stage.create_new_stage()
# prims.create_prim("/World")

# stage.add_reference_to_stage(
#     usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
#     prim_path="/World/Environment"
# )
# obj_prim_path = "/World/Obj"
# stage.add_reference_to_stage(
#     usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Props/pallet_eu.usd",
#     prim_path=obj_prim_path
# )

# pca = PermuAndCombi(obj_prim_path)
# pca.set_pose((-7.0, -11.0, 0.0), 90.0)
# simu_app.run_coroutine(pca.run(colomns=6, rows=6))
simu_app.run_coroutine(run_box_stacking_scenarios_async())

while simu_app.is_running():
    simu_app.update()

simu_app.close()