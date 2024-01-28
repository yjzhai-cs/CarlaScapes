
import carla

from .base import CarlaSensor
from simulation.utils.geo2location import Geo2Location

class GNSS(CarlaSensor):
    """
    Class for GNSS sensor.

    Carla uses left-handed coordinate system.
    Ref: https://subscription.packtpub.com/book/game_development/9781784394905/1/ch01lvl1sec18/the-2d-and-3d-coordinate-systems

    Why is my GPS data always close to 0？ #4806
    Ref: https://github.com/carla-simulator/carla/discussions/4806
    """

    def __init__(self, name, gnss_config, parent_actor=None):
        """ Constructor method. """
        super().__init__(name, parent_actor)
        self.data['timestamp'] = 0
        self.data['frame'] = 0
        self.data['latitude'] = 0.0
        self.data['longitude'] = 0.0
        self.data['altitude'] = 0.0
        self.data['x'] = 0.0
        self.data['y'] = 0.0
        self.data['z'] = 0.0

        carla_world = self._parent.get_world()
        gnss_bp = carla_world.get_blueprint_library().find('sensor.other.gnss')

        gnss_bp.set_attribute(
            'noise_alt_bias', gnss_config['noise_alt_bias'])
        gnss_bp.set_attribute('noise_alt_stddev',
                              gnss_config['noise_alt_stddev'])
        gnss_bp.set_attribute(
            'noise_lat_bias', gnss_config['noise_lat_bias'])
        gnss_bp.set_attribute('noise_lat_stddev',
                              gnss_config['noise_lat_stddev'])
        gnss_bp.set_attribute(
            'noise_lon_bias', gnss_config['noise_lon_bias'])
        gnss_bp.set_attribute('noise_lon_stddev',
                              gnss_config['noise_lon_stddev'])

        self.sensor = carla_world.spawn_actor(gnss_bp,
                                              carla.Transform(carla.Location(
                                                  x=gnss_config['pos_x'], z=0.0)),
                                              attach_to=self._parent)
        self.sensor.listen(lambda event: self._queue.put(event))

        # Object to transform from geo location to carla location
        self._geo2location = Geo2Location(carla_world.get_map())

    def update(self):
        """ Wait for GNSS measurement and update data. """
        # get() blocks the script so synchronization is guaranteed
        event = self._queue.get()

        # print('GNSS sensor received at frame %06d.' % event.frame)

        self.data['timestamp'] = event.timestamp
        self.data['frame'] = event.frame
        self.data['latitude'] = event.latitude
        self.data['longitude'] = event.longitude
        self.data['altitude'] = event.altitude

        # Get transform from geolocation to location
        location = self._geo2location.transform(
            carla.GeoLocation(self.data['latitude'], self.data['longitude'], self.data['altitude']))

        self.data['x'] = location.x
        self.data['y'] = location.y
        self.data['z'] = location.z