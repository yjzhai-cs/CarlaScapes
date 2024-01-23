import carla
import random
from typing import Dict

class EnvBase(object):
    def __init__(self,
                 ip: str = "localhost",
                 port: int = 2000,
                 map_name: str = "Town02",
                 is_large_map: bool = False,
                 weather_config: Dict[str, float] = None,
                 is_sync_mode: bool = True,
    ):

        self.ip = ip
        self.port = port
        self.map_name = map_name
        self.is_large_map = is_large_map
        self.weather_config = weather_config

        self.is_sync_mode = is_sync_mode

        self.actor_list = []
        self.sensor_list = []

    def build_client(self):
        """Build the client for the simulator."""
        try:
            self.client = carla.Client(self.ip, self.port)
            self.client.set_timeout(50.0)
        except RuntimeError:
            print('The client cannot connect to the server at %s:%s.' % (self.ip, self.port))
    def build_world(self):
        """Set the world for the simulator."""
        self.world = self.client.get_world()

        self.original_settings = self.world.get_settings()

        try:
            self.world = self.client.load_world(self.map_name)
        except RuntimeError:
            print(f'Loading world {self.map_name} failed, use Town10 instead.')
            self.client.set_timeout(50.0)

        settings = self.world.get_settings()
        if self.is_large_map:
            settings.tile_stream_distance = 2000

        # set synchorinized mode
        if self.is_sync_mode:
            settings.fixed_delta_seconds = 0.05 #20 fps, 5ms
            settings.synchronous_mode = True
            traffic_manager = self.client.get_trafficmanager()
            traffic_manager.set_synchronous_mode(True)
        self.world.apply_settings(settings)

        # Set weather for your world
        if self.weather_config is not None:
            weather = carla.WeatherParameters(**self.weather_config)
            self.world.set_weather(weather)

        self.blueprint_library = self.world.get_blueprint_library()

    def build_ego_vehicle(self):
        """Build the ego vehicle for the simulator."""
        ego_vehicle_bp = self.blueprint_library.filter('vehicle')[0]

        if self.is_large_map:
            ego_vehicle_bp.set_attribute('role_name', 'hero')

        transform = random.choice(self.world.get_map().get_spawn_points())
        self.ego_vehicle = self.world.spawn_actor(ego_vehicle_bp, transform)

        self.ego_vehicle.set_autopilot(True)

        self.actor_list.append(self.ego_vehicle)

    def build_env(self):
        self.build_client()
        self.build_world()
        self.build_ego_vehicle()

    def destroy(self):
        """Destroy the actors and sensors. Recovers the settings."""
        self.world.apply_settings(self.original_settings)
        print('Destroying actors')
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.actor_list])
        for sensor in self.sensor_list:
            sensor.destroy()
        print('Done.')


