
import carla
import numpy as np

from .base import CarlaSensor

class RGBCamera(CarlaSensor):
    """
    Class for RGB camera.
    """
    def __init__(self, name, rgb_cam_config, parent_actor=None, world=None):
        super().__init__(name, parent_actor)

        self.data['timestamp'] = 0
        self.data['frame'] = 0
        self.data['rgb_image'] = None

        carla_world = self._parent.get_world()
        rgb_cam_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        rgb_cam_bp.set_attribute('image_size_x', rgb_cam_config['img_width'])
        rgb_cam_bp.set_attribute('image_size_y', rgb_cam_config['img_height'])
        rgb_cam_bp.set_attribute('fov', rgb_cam_config['fov'])

        self.sensor = carla_world.spawn_actor(rgb_cam_bp,
                                              carla.Transform(carla.Location(x=rgb_cam_config['pos_x'], z=rgb_cam_config['pos_z'])),
                                              attach_to=self._parent)

        self.listener = self.sensor.listen(lambda image: self._queue.put(image))

    def update(self):
        """ Wait for RGB image and update data. """
        image = self._queue.get()
        self.data['timestamp'] = image.timestamp
        self.data['frame'] = image.frame

        # print('RGB camera received at frame %06d.' % image.frame)

        np_img = np.frombuffer(image.raw_data, dtype=np.uint8)
        # Reshape to BGRA format
        np_img = np.reshape(np_img, (image.height, image.width, -1))
        # Convert to RGB
        np_img = np_img[:, :, :3]
        # Since np_img is from the buffer, which is reused by Carla
        # Making a copy makes sure rgb_image is not subject to side-effect when the underlying buffer is modified
        self.data['rgb_image'] = np_img.copy()