import omni.replicator.core as rep
import omni
import os
import random
import omni.usd
from isaacsim.core.utils.stage import get_current_stage
from pxr import Gf

# from omni.replicator.core import AnnotatorRegistry, BackendDispatch, Writer, WriterRegistry

# class MyCustomWriter(Writer):
#     def __init__(self, output_dir, rgb=True, normals=False,):
#         self.version = "0.0.1"
#         self.backend = BackendDispatch({"paths": {"out_dir": output_dir}})
#         if rgb:
#             self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))
#         if normals:
#             self.annotators.append(AnnotatorRegistry.get_annotator("normals"))
#         self._frame_id = 0

#     def write(self, data: dict):
#         for annotator in data.keys():
#             # If there are multiple render products the data will be stored in subfolders
#             annotator_split = annotator.split("-")
#             render_product_path = ""
#             multi_render_prod = 0
#             if len(annotator_split) > 1:
#                 multi_render_prod = 1
#                 render_product_name = annotator_split[-1]
#                 render_product_path = f"{render_product_name}/"

#             # rgb
#             if annotator.startswith("rgb"):
#                 if multi_render_prod:
#                     render_product_path += "rgb/"
#                 filename = f"{render_product_path}rgb_{self._frame_id}.png"
#                 print(f"[{self._frame_id}] Writing {self.backend.output_dir}/{filename} ..")
#                 self.backend.write_image(filename, data[annotator])

#             # semantic_segmentation
#             if annotator.startswith("normals"):
#                 if multi_render_prod:
#                     render_product_path += "normals/"
#                 filename = f"{render_product_path}normals_{self._frame_id}.png"
#                 print(f"[{self._frame_id}] Writing {self.backend.output_dir}/{filename} ..")
#                 colored_data = ((data[annotator] * 0.5 + 0.5) * 255).astype(np.uint8)
#                 self.backend.write_image(filename, colored_data)

#         self._frame_id += 1

#     def on_final_frame(self):
#         self._frame_id = 0

# WriterRegistry.register(MyCustomWriter)

from .randomize import ObjRandomizer
import carb

class ObjBasedDateGenerator:
    def __init__(self, config: dict) -> None:

        # Disable capture on play and async rendering
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
        carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
        carb.settings.get_settings().set("/app/asyncRendering", False)
        
        rep.orchestrator.set_capture_on_play(False)
        rep.set_global_seed(66)
        rep.randomizer.register(self._randomizeCameraPose)

        self._randomized_obj = ObjRandomizer(config["obj_prim_path"])
        rep.randomizer.register(self._randomized_obj._randomizeObj)
        rep.randomizer.register(self._randObjMaterial)

        self._dome_light = rep.create.light(light_type="dome", position=(0, 0, 5))
        # rep.randomizer.register(self._rand_dome)
        rep.randomizer.register(ObjBasedDateGenerator._randomLight)

        # self._random_trigger = rep.trigger.on_frame(max_execs=config["frames_required"], interval=1, rt_subframes=8)
        self._obj_trigger = rep.trigger.on_frame(
            max_execs=config["frames_required"], interval=int(config["frames_required"] / 10), rt_subframes=16)
        self._camera_trigger = rep.trigger.on_frame(max_execs=config["frames_required"], interval=1, rt_subframes=16)
        self._light_trigger = rep.trigger.on_frame(
            max_execs=config["frames_required"], interval=int(config["frames_required"] / 20), rt_subframes=16)

        self._frames_required = config["frames_required"]
        self._camera_position_domain_lower = config["camera_position_domain_lower"]
        self._camera_position_domain_upper = config["camera_position_domain_upper"]


        self._camera = rep.create.camera(
            focus_distance=400.0, focal_length=15.0, clipping_range=(0.1, 10000000.0), name="DriverCam"
        )

        self._render_product = rep.create.render_product(camera=self._camera, resolution=(1024, 1024))

        self._writer = rep.writers.get("BasicWriter")
        # self._writer = rep.writers.get("PoseWriter")
        data_save_dir = os.path.join(os.getcwd(), "data/semantic_segmentation")
        self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        self._writer.attach(self._render_product, trigger=self._camera_trigger)

        self.is_finished = False

    @property
    def camera_position_domain(self):
        return [self._randomized_obj.obj_position - self._camera_position_domain_lower,
                self._randomized_obj.obj_position + self._camera_position_domain_upper]


    def _rand_dome(self):
        with self._dome_light:
            # rep.modify.pose(rotation=rep.distribution.uniform((0,-180,-180),(0,180,180)))
            # 随机 HDR 贴图（示例里直接用官方示例纹理，你也可换自己的 HDR 路径列表）
            # rep.modify.attribute("texture", rep.distribution.choice(rep.example.TEXTURES))
            # rep.modify.attribute("intensity", rep.distribution.uniform(0.1, 3.0))
            # rep.modify.attribute("exposure",  rep.distribution.uniform(-2.0, +2.0))
            rep.modify.attribute("intensity",   rep.distribution.uniform(300, 2000))
            rep.modify.attribute("temperature", rep.distribution.uniform(3000, 8000))
            rep.modify.attribute("color",       rep.distribution.uniform((0.7,0.7,0.7),(1,1,1)))
        return self._dome_light.node
    
    def _randObjMaterial(self):
        mats = rep.create.material_omnipbr(
            metallic=rep.distribution.uniform(0.0, 1.0),
            roughness=rep.distribution.uniform(0.0, 1.0),
            diffuse=rep.distribution.uniform((0, 0, 0), (1, 1, 1)),
            count=100,
        )
        with self._randomized_obj.rep_obj_prim:
            rep.randomizer.materials(mats)
        return self._randomized_obj.rep_obj_prim.node

    def _randomizeCameraPose(self) -> rep.scripts.utils.ReplicatorItem:
        with self._camera:
            rep.modify.pose(
                position=rep.distribution.uniform(*self.camera_position_domain),
                look_at=self._randomized_obj.rep_obj_prim
            )
        return self._camera.node

    @staticmethod 
    def _randomLight():
        lights = rep.create.light(
            light_type="Sphere",
            # light_type="Dome",
            # color=rep.distribution.uniform((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
            temperature=rep.distribution.uniform(3000, 8000),
            intensity=rep.distribution.uniform(10000, 300000),
            position=rep.distribution.uniform((-5, -5, 0.3), (5, 5, 6.0)),
            # scale=rep.distribution.uniform(1, 20),
            scale=1,
            count=1,
        )
        return lights.node
    
    def generate(self):
        with self._obj_trigger:
            rep.randomizer._randomizeObj()
            # rep.randomizer._randObjMaterial()
        with self._camera_trigger:
            rep.randomizer._randomizeCameraPose()   # ← 随机器调用“必须”放在 trigger 里
        with self._light_trigger:
            # rep.randomizer._rand_dome()
            rep.randomizer._randomLight()

        rep.orchestrator.run()
        rep.orchestrator.wait_until_complete()
        self._writer.detach()
        self._render_product.destroy()
        self.is_finished = True