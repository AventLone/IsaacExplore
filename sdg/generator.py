import omni.replicator.core as rep
import os, carb.settings
from datetime import datetime
from .randomizer_rep import Randomizer

import omni.replicator.core as rep
import os

import numpy as np
from omni.replicator.core import AnnotatorRegistry, BackendDispatch, Writer, WriterRegistry

class MyCustomWriter(Writer):
    def __init__(self, output_dir, rgb = True, semantic_segmentation = False):
        self.version = "0.0.1"
        self.backend = BackendDispatch({"paths": {"out_dir": output_dir}})
        self.annotators = []
        if rgb:
            self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))
        if semantic_segmentation:
            self.annotators.append(AnnotatorRegistry.get_annotator("normals"))

        self._frame_id = 1

    def write(self, data: dict[str, rep.annotators.Annotator]):
        for annotator in data.keys():
            # If there are multiple render products the data will be stored in subfolders
            annotator_split = annotator.split("-")
            render_product_path = ""
            multi_render_prod = 0
            if len(annotator_split) > 1:
                multi_render_prod = 1
                render_product_name = annotator_split[-1]
                render_product_path = f"{render_product_name}/"

            # rgb
            if annotator.startswith("rgb"):
                # if multi_render_prod:
                render_product_path += "rgb/"
                filename = f"{render_product_path}rgb_{self._frame_id}.png"
                print(f"[{self._frame_id}] Writing {self.backend.output_dir}/{filename} ..")
                self.backend.write_image(filename, data[annotator])

            # semantic_segmentation
            if annotator.startswith("normals"):
                # if multi_render_prod:
                render_product_path += "normals/"
                filename = f"{render_product_path}normals_{self._frame_id}.png"
                print(f"[{self._frame_id}] Writing {self.backend.output_dir}/{filename} ..")
                colored_data = ((data[annotator] * 0.5 + 0.5) * 255).astype(np.uint8)
                self.backend.write_image(filename, colored_data)

        self._frame_id += 1

    def on_final_frame(self):
        self._frame_id = 1

WriterRegistry.register(MyCustomWriter)

class MultiFolderWriter(rep.Writer):
    def __init__(self, output_dir, rgb=True, semantic_segmentation=True):
        self._output_dir = output_dir
        self._backend = rep.BackendDispatch({"paths": {"out_dir": output_dir}})
        self._frame_id = 1
        self.annotators = []

        # 1. Register required annotators
        if rgb:
            self.annotators.append(rep.annotators.get("rgb"))
            self.rgb_dir = os.path.join(output_dir, "rgb")
        if semantic_segmentation:
            self.semantic_seg_dir = os.path.join(output_dir, "semantic_seg")
            self.annotators.append(rep.annotators.get("semantic_segmentation"))

    def write(self, data):
        # 2. Define subdirectories
        # rgb_dir = os.path.join(self._output_dir, "rgb")
        # seg_dir = os.path.join(self._output_dir, "segmentation")

        # 3. Logic for saving each data type
        for annotator_name, annotator_data in data.items():
            if annotator_name == "rgb":
                file_path = f"{self.rgb_dir}/{self._frame_id}.png"
                self._backend.write_image(file_path, annotator_data)
            
            elif annotator_name == "semantic_segmentation":
                file_path = f"{self.semantic_seg_dir}/{self._frame_id}.png"
                # Access the data array from the segmentation dictionary
                self._backend.write_image(file_path, annotator_data["data"])

        self._frame_id += 1

# Register and use the writer
rep.writers.register_writer(MultiFolderWriter)  # type: ignore


class Generator:
    # Disable capture on play and async rendering
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
    carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
    carb.settings.get_settings().set("/app/asyncRendering", False)
    # Set DLSS to Quality mode (2) for best SDG results (Options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
    # carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)   # DLAA

    def __init__(self, randomizer: Randomizer, img_resolution=(1024, 1024), save_path=None) -> None:
        self._randomizer = randomizer
        self._render_product = rep.create.render_product(camera=self._randomizer.camera, resolution=img_resolution)
        # self._writer = rep.writers.get("BasicWriter")
        self._writer = rep.writers.get("MyCustomWriter")
        # self._writer.initialize(camera_params=True, bounding_box_3d=True)

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        save_at = f"generated_data/{timestamp}" if save_path is None else f"{save_path}/{timestamp}"
        data_save_dir = os.path.join(os.getcwd(), save_at)

        # self._writer.initialize(output_dir=data_save_dir, rgb=True, semantic_segmentation=True)
        self._writer.initialize(output_dir=data_save_dir, rgb=True, normals=True)
        self._writer.attach(self._render_product, trigger=self._randomizer.camera_trigger)

    def generate(self):
        self._randomizer.trigger_obj_pose()
        self._randomizer.trigger_camera()
        self._randomizer.trigger_light()

        rep.orchestrator.run()
        rep.orchestrator.wait_until_complete()

        self._writer.detach()
        self._render_product.destroy()    # type: ignore


