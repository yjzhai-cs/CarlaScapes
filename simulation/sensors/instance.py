
import numpy as np
import carla
from .base import CarlaSensor

class InstanceCamera(CarlaSensor):
    def __init__(self, name, in_cam_config, parent_actor=None):
        super().__init__(name, parent_actor)
        self.data['timestamp'] = 0
        self.data['frame'] = 0
        self.data['in_image'] = None

        carla_world = self._parent.get_world()
        in_cam_bp = carla_world.get_blueprint_library().find('sensor.camera.instance_segmentation')
        in_cam_bp.set_attribute('image_size_x', in_cam_config['img_width'])
        in_cam_bp.set_attribute('image_size_y', in_cam_config['img_height'])
        in_cam_bp.set_attribute('fov', in_cam_config['fov'])

        self.sensor = carla_world.spawn_actor(in_cam_bp,
                                              carla.Transform(carla.Location(x=in_cam_config['pos_x'], z=in_cam_config['pos_z'])),
                                              attach_to=self._parent)

        self.sensor.listen(lambda image: self._queue.put(image))

    def update(self):
        """ Wait for instance image and update data. """
        image = self._queue.get()

        # print('Instance camera received at frame %06d.' % image.frame)

        self.data['timestamp'] = image.timestamp
        self.data['frame'] = image.frame

        np_img = np.frombuffer(image.raw_data, dtype=np.uint8)
        # Reshape to BGRA format
        np_img = np.reshape(np_img, (image.height, image.width, -1))
        # Convert to RGB
        np_img = np_img[:, :, :3]
        # Since np_img is from the buffer, which is reused by Carla
        # Making a copy makes sure in_image is not subject to side-effect when the underlying buffer is modified
        self.data['in_image'] = np_img.copy()