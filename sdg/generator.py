import omni.replicator.core as rep
import os, carb.settings
from datetime import datetime
from .randomizer_rep import Randomizer

import omni.replicator.core as rep
import os
from omni.replicator.core import BasicWriter


class Generator:
    # Disable capture on play and async rendering
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
    carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
    carb.settings.get_settings().set("/app/asyncRendering", False)
    # Set DLSS to Quality mode (2) for best SDG results (Options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
    # carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)   # DLAA

    def __init__(self, randomizer: Randomizer, annotation_typ: dict, img_resolution=(1024, 1024), save_path=None) -> None:
        self._randomizer = randomizer
        self._render_product = rep.create.render_product(camera=self._randomizer.camera, resolution=img_resolution)
        self._writer = rep.writers.get("BasicWriter")

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        save_at = f"generated_data/{timestamp}" if save_path is None else f"{save_path}/{timestamp}"
        data_save_dir = os.path.join(os.getcwd(), save_at)
        # self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        self._writer.initialize(output_dir=data_save_dir, rgb=True, **annotation_typ)
        self._writer.attach(self._render_product, trigger=self._randomizer.camera_trigger)

    def generate(self):
        self._randomizer.trigger_obj_pose()
        self._randomizer.trigger_obj_apperance()
        self._randomizer.trigger_camera()
        self._randomizer.trigger_light()

        rep.orchestrator.run()
        rep.orchestrator.wait_until_complete()

        self._writer.detach()
        self._render_product.destroy()    # type: ignore


