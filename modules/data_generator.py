import omni.replicator.core as rep
import omni
import os
import random
import omni.usd
from isaacsim.core.utils.stage import get_current_stage
from pxr import Gf

stage = get_current_stage()
prim = stage.GetPrimAtPath("/World/AnyPrim")

class ObjBasedDateGenerator:
    def __init__(self, config: dict) -> None:
        
        rep.orchestrator.set_capture_on_play(False)
        rep.set_global_seed(66)
        # random

        self._frames_required = config["frames_required"]
        self._obj_prim_path = config["obj_prim_path"]
        self._camera_position_domain_lower = config["camera_position_domain_lower"]
        self._camera_position_domain_upper = config["camera_position_domain_upper"]

        stage = get_current_stage()
        self._obj_prim = stage.GetPrimAtPath(self._obj_prim_path)
        self._obj_position = omni.usd.get_world_transform_matrix(self._obj_prim).ExtractTranslation()

        # camera_prim_path = "/World/camera_data"
        # self._camera = rep.get.prim_at_path(camera_prim_path)
        self._camera = rep.create.camera()
        # if not self._camera:
        #     raise RuntimeError(f"Camera not found: {camera_prim_path}")

        # self.render_product = rep.create.render_product(camera="/World/camera_data/SG3S_ISX031C_GMSL2F_H190XA_01",
        #                                                 resolution=(1024, 1024))
        # self._render_product = rep.create.render_product(camera="/OmniverseKit_Persp", resolution=(1024, 1024))
        self._render_product = rep.create.render_product(camera=self._camera, resolution=(1024, 1024))

        self._writer = rep.writers.get("BasicWriter")
        data_save_dir = os.path.join(os.getcwd(), "data/semantic_segmentation")
        self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        self._writer.attach(self._render_product)

        self.is_finished = False

    # def __objPosition(self):
    # @property
    # def obj_postion(self):
    #     return omni.usd.get_world_transform_matrix(prim).ExtractTranslation()


    def __randomizeCameraPose(self):
        with self._camera:
            rep.modify.pose(
                # position=rep.distribution.uniform((-5, 5, 1), (-1, 15, 3)),
                position=rep.distribution.uniform(
                    self._obj_position - self._camera_position_domain_lower, 
                    self._obj_position + self._camera_position_domain_upper
                ),
                look_at=self._obj_prim_path
            )

    def generate(self):
        for _ in range(self._frames_required):
            self.__randomizeCameraPose()
            rep.orchestrator.step()

        self._writer.detach()
        self._render_product.destroy()
        rep.orchestrator.wait_until_complete()

        self.is_finished = True