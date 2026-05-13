from isaacsim.simulation_app import SimulationApp
simu_app = SimulationApp({"renderer": "RayTracedLighting", "headless": False})

import omni.replicator.core as rep
import os, carb.settings
from sdg import writers, randomizer, sample
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
        self._randomizer = randomizer.EventRandomizer(self._pac.PRIM_PATH)
        self._render_product = rep.create.render_product(camera=self._randomizer.camera, resolution=img_resolution)        

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        save_at = f"generated_data/{timestamp}" if save_path is None else f"{save_path}/{timestamp}"
        data_save_dir = os.path.join(os.getcwd(), save_at)

        self._writer = writers.CocoInstanceSegWriter(output_dir=data_save_dir)
        self._writer.attach(self._render_product, trigger=None)

    async def generate(self):
        

        await rep.orchestrator.step_async()
        self._writer.
        rep.orchestrator.run()
        rep.orchestrator.wait_until_complete()

        self._writer.detach()
        self._render_product.destroy()    # type: ignore


