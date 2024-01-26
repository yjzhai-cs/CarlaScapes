
import numpy as np
import carla
from .base import CarlaSensor

class SemanticCamera(CarlaSensor):
    """ Class for semantic camera. """

    def __init__(self, name, ss_cam_config, parent_actor=None):
        """ Constructor method. """
        super().__init__(name, parent_actor)
        self.data['timestamp'] = 0
        self.data['frame'] = 0
        self.data['ss_image'] = None
        self.data['labelIds_image'] = None

        carla_world = self._parent.get_world()
        ss_cam_bp = carla_world.get_blueprint_library().find(
            'sensor.camera.semantic_segmentation')
        ss_cam_bp.set_attribute('image_size_x', ss_cam_config['img_width'])
        ss_cam_bp.set_attribute('image_size_y', ss_cam_config['img_height'])
        ss_cam_bp.set_attribute('fov', ss_cam_config['fov'])

        self.sensor = carla_world.spawn_actor(ss_cam_bp,
                                              carla.Transform(
                                                  carla.Location(x=ss_cam_config['pos_x'], z=ss_cam_config['pos_z'])),
                                              attach_to=self._parent)

        self.sensor.listen(lambda image: self._queue.put(image))

    def update(self):
        """ Wait for semantic image and update data. """
        image = self._queue.get()

        # print('Semantic camera received at frame %06d.' % image.frame)

        self.data['timestamp'] = image.timestamp
        self.data['frame'] = image.frame


        np_img = np.frombuffer(image.raw_data, dtype=np.uint8)
        # Reshap to BGRA format
        np_img = np.reshape(np_img, (image.height, image.width, -1))
        # Semantic info is stored only in the R channel
        # Since np_img is from the buffer, which is reused by Carla
        # Making a copy makes sure ss_image is not subject to side-effect when the underlying buffer is modified
        self.data['labelIds_image'] = np_img[:, :, 2].copy()

        image.convert(carla.ColorConverter.CityScapesPalette)
        np_img = np.frombuffer(image.raw_data, dtype=np.uint8)
        np_img = np.reshape(np_img, (image.height, image.width, -1))
        self.data['ss_image'] = np_img[:, :, :3].copy()