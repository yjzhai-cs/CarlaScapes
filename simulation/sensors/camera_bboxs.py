
import carla
import numpy as np
from simulation.utils.writer import XMLWriter
from .base import CarlaSensor
from simulation.utils.util import build_projection_matrix, get_image_point

class RGBBboxsCamera(CarlaSensor):
    """
    Class for RGB camera and 2D Bounding Boxs.
    """
    def __init__(self, name, rgb_cam_config, parent_actor=None, world=None):
        super().__init__(name, parent_actor)

        self.data['timestamp'] = 0
        self.data['frame'] = 0
        self.data['rgb_image'] = None
        self.data['bboxs'] = None

        # Setting RGB camera
        self.carla_world = self._parent.get_world()
        self.rgb_cam_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        self.rgb_cam_bp.set_attribute('image_size_x', rgb_cam_config['img_width'])
        self.rgb_cam_bp.set_attribute('image_size_y', rgb_cam_config['img_height'])
        self.rgb_cam_bp.set_attribute('fov', rgb_cam_config['fov'])

        self.sensor = self.carla_world.spawn_actor(self.rgb_cam_bp,
                                              carla.Transform(carla.Location(x=rgb_cam_config['pos_x'], z=rgb_cam_config['pos_z'])),
                                              attach_to=self._parent)

        self.listener = self.sensor.listen(lambda image: self._queue.put(image))

        self.image_w = self.rgb_cam_bp.get_attribute("image_size_x").as_int()
        self.image_h = self.rgb_cam_bp.get_attribute("image_size_y").as_int()
        fov = self.rgb_cam_bp.get_attribute("fov").as_float()

        # Calculate the camera projection matrix to project from 3D -> 2D
        self.K = build_projection_matrix(self.image_w, self.image_h, fov)

    def bounding(self):
        # Get the camera matrix
        world_2_camera = np.array(self.sensor.get_transform().get_inverse_matrix())

        # Initialize the exporter
        writer = XMLWriter('', self.image_w, self.image_h)

        for npc in self.carla_world.get_actors().filter('*vehicle*'):  # vehicle

            # Filter out the ego vehicle
            if npc.id != self._parent.id:

                bb = npc.bounding_box
                dist = npc.get_transform().location.distance(self._parent.get_transform().location)

                # Filter for the vehicles within 500m
                if dist < 500:

                    # Calculate the dot product between the forward vector
                    # of the vehicle and the vector between the vehicle
                    # and the other vehicle. We threshold this dot product
                    # to limit to drawing bounding boxes IN FRONT OF THE CAMERA
                    forward_vec = self._parent.get_transform().get_forward_vector()
                    ray = npc.get_transform().location - self._parent.get_transform().location

                    if forward_vec.dot(ray) > 1:
                        p1 = get_image_point(bb.location, self.K, world_2_camera)
                        verts = [v for v in bb.get_world_vertices(npc.get_transform())]
                        x_max = -10000
                        x_min = 10000
                        y_max = -10000
                        y_min = 10000

                        for vert in verts:
                            p = get_image_point(vert, self.K, world_2_camera)
                            # Find the rightmost vertex
                            if p[0] > x_max:
                                x_max = p[0]
                            # Find the leftmost vertex
                            if p[0] < x_min:
                                x_min = p[0]
                            # Find the highest vertex
                            if p[1] > y_max:
                                y_max = p[1]
                            # Find the lowest  vertex
                            if p[1] < y_min:
                                y_min = p[1]

                        # Add the object to the frame (ensure it is inside the image)
                        if x_min > 0 and x_max < self.image_w and y_min > 0 and y_max < self.image_h:
                            writer.addObject('vehicle', x_min, y_min, x_max, y_max)

        self.data['bboxs'] = writer

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


