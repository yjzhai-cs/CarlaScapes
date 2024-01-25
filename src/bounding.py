
import numpy as np
from pascal_voc_writer import Writer
from .util import build_projection_matrix, get_image_point

class Bounding():
    def __init__(self, camera, camera_bp, world, ego_vehicle):
        self.camera = camera
        self.camera_bp = camera_bp
        self.world = world
        self.ego_vehicle = ego_vehicle

        # Get the attributes from the camera
        self.image_w = self.camera_bp.get_attribute("image_size_x").as_int()
        self.image_h = self.camera_bp.get_attribute("image_size_y").as_int()
        self.fov = self.camera_bp.get_attribute("fov").as_float()

        # Calculate the camera projection matrix to project from 3D -> 2D
        self.K = build_projection_matrix(self.image_w, self.image_h, self.fov)

    def bounding(self, save_path):
        # Get the camera matrix
        world_2_camera = np.array(self.camera.get_transform().get_inverse_matrix())

        # Initialize the exporter
        writer = Writer(save_path + '_img.png', self.image_w, self.image_h)

        for npc in self.world.get_actors().filter('*vehicle*'):

            # Filter out the ego vehicle
            if npc.id != self.ego_vehicle.id:

                bb = npc.bounding_box
                dist = npc.get_transform().location.distance(self.ego_vehicle.get_transform().location)

                # Filter for the vehicles within 50m
                if dist < 50:

                # Calculate the dot product between the forward vector
                # of the vehicle and the vector between the vehicle
                # and the other vehicle. We threshold this dot product
                # to limit to drawing bounding boxes IN FRONT OF THE CAMERA
                    forward_vec = self.ego_vehicle.get_transform().get_forward_vector()
                    ray = npc.get_transform().location - self.ego_vehicle.get_transform().location

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

            # Save the bounding boxes in the scene
        writer.save(save_path + '_bounding_box.xml')