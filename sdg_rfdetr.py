from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": False})

import omni.replicator.core as rep
import os, carb.settings
from sdg import writers, randomizer, sample
from omni.kit.async_engine import run_coroutine
from datetime import datetime

class Sampler:
    # Disable capture on play and async rendering
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
    carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
    carb.settings.get_settings().set("/app/asyncRendering", False)
    # Set DLSS to Quality mode (2) for best SDG results (Options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    def __init__(self, prim_paths: list[str], img_resolution=(1024, 1024), save_path=None) -> None:
        self._pac = sample.PermuAndCombi(prim_paths, wait_event=True)
        self._randomizer = randomizer.EventRandomizer(sample.PermuAndCombi.PRIM_PATH)
        self._render_product = rep.create.render_product(camera=self._randomizer.camera, resolution=img_resolution)        

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        save_at = f"generated_data/{timestamp}" if save_path is None else f"{save_path}/{timestamp}"
        data_save_dir = os.path.join(os.getcwd(), save_at)

        self._writer = writers.CocoInstanceSegWriter(output_dir=data_save_dir)
        self._writer.attach(self._render_product, trigger=self._randomizer.camera_trigger)

        cols, rows = 4, 5
        self._counts = cols * rows
        run_coroutine(self._pac.line_up(colomns=4, rows=5))

    async def generate(self):
        for _ in range(self._counts):
            await self._pac.run()
            for frame in range(self._randomizer.frames_generated):
                await rep.orchestrator.step_async(rt_subframes=8)
                self._randomizer.randomize_camera()
                if frame % 3 == 0:
                    self._randomizer.randomize_material()
                if frame % 10 == 0:
                    self._randomizer._randomize_light()

        await rep.orchestrator.wait_until_complete_async()

        self._writer.detach()
        self._render_product.destroy()    # type: ignore


from isaacsim.core.utils import stage, prims
from sdg import common

created_stage = stage.create_new_stage()
prims.create_prim("/World")

environment_prim_path = "/World/Environment"
stage.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Environments/warehouse_trailer.usd",
    prim_path=environment_prim_path
)
common.set_world_trasform(prim=environment_prim_path, translation=[-6.7, 5.5, 0.0], orientation=common.yaw2quat(180.0))


objs_prim_path = "/World/Obj"
stage.add_reference_to_stage(
    usd_path="/home/avent/Desktop/IsaacAssets/Collected_warehouse_trailer/Props/pallet_eu.usd",
    prim_path=objs_prim_path
)

boxes_urls_and_weights = [
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxA_01.usd", 0.02),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxB_01.usd", 0.06),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxC_01.usd", 0.12),
    ("/home/avent/Desktop/IsaacAssets/isaac-sim-assets-complete-5.1.0/Assets/Isaac/5.1/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01.usd", 0.80),
]

sampler = Sampler(prim_paths=[objs_prim_path], img_resolution=(504, 504), save_path="/home/avent/Desktop/generated_data")

simu_app.run_coroutine(sampler.generate())

while simu_app.is_running():
    simu_app.update()

simu_app.close()

