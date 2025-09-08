import omni.replicator.core as rep
import omni
import os
import random
import omni.usd
from isaacsim.core.utils.stage import get_current_stage
from pxr import Gf


class ObjBasedDateGenerator:
    def __init__(self, config: dict) -> None:
        
        rep.orchestrator.set_capture_on_play(False)
        rep.set_global_seed(66)
        rep.randomizer.register(self._randomizeCameraPose)

        self._random_trigger = rep.trigger.on_frame(max_execs=config["frames_required"], interval=1, rt_subframes=8)

        self._frames_required = config["frames_required"]
        self._obj_prim_path = config["obj_prim_path"]
        self._camera_position_domain_lower = config["camera_position_domain_lower"]
        self._camera_position_domain_upper = config["camera_position_domain_upper"]

        stage = get_current_stage()
        self._obj_prim = stage.GetPrimAtPath(self._obj_prim_path)
        self._obj_position = omni.usd.get_world_transform_matrix(self._obj_prim).ExtractTranslation()

        # camera_prim_path = "/World/camera_data"
        # self._camera = rep.get.prim_at_path(camera_prim_path)
        # self._camera = rep.create.camera()
        self._camera = rep.create.camera(
            focus_distance=400.0, focal_length=15.0, clipping_range=(0.1, 10000000.0), name="DriverCam"
        )
        self._render_product = rep.create.render_product(camera=self._camera, resolution=(1024, 1024))

        self._writer = rep.writers.get("BasicWriter")
        data_save_dir = os.path.join(os.getcwd(), "data/semantic_segmentation")
        self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        self._writer.attach(self._render_product, trigger=self._random_trigger)

        self.is_finished = False

        self._camera_position_domain = [self._obj_position - self._camera_position_domain_lower,
                                         self._obj_position + self._camera_position_domain_upper]

    def __setObjPosition(self):
        pass

    def _randomizeCameraPose(self) -> rep.scripts.utils.ReplicatorItem:
        with self._camera:
            rep.modify.pose(
                position=rep.distribution.uniform(
                    self._obj_position - self._camera_position_domain_lower, 
                    self._obj_position + self._camera_position_domain_upper
                ),
                look_at=self._obj_prim_path
            )
        return self._camera.node

    def generate(self):
        with self._random_trigger:
            rep.randomizer._randomizeCameraPose()   # ← 随机器调用“必须”放在 trigger 里

        rep.orchestrator.run()
        rep.orchestrator.wait_until_complete()
        self._writer.detach()
        self._render_product.destroy()
        self.is_finished = True