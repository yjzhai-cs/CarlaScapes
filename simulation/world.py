import carla
import sys
import random

from simulation.utils.weather import find_weather_presets
from simulation.sensors import CarlaSensor
from simulation.generator.generator import get_actor_blueprints

class World(object):
    """ Class representing the simulation environment. """

    def __init__(self,
                 carla_world: carla.World,
                 traffic_manager: carla.TrafficManager,
                 config: dict,
                 spawn_point: carla.Transform = None):
        """
        Constructor method.

        If spawn_point not given, choose random spawn point recommended by the map.
        """
        self.carla_world = carla_world
        self.tm = traffic_manager
        self.spectator = carla_world.get_spectator()
        try:
            self.map = self.carla_world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print(
                '  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)
        self._weather_presets = find_weather_presets()
        self._weather_index = config['world']['weather']
        self.carla_world.set_weather(
            self._weather_presets[self._weather_index][0])
        self.ego_veh = None

        # Containers for managing carla sensors
        self.carla_sensors = {}
        # This dict will store references to all sensor's data container.
        # It is to facilitate the recording, so the recorder only needs to query this one-stop container.
        # When a CarlaSensor is added via add_carla_sensor(), its data container is registered automatically.
        # When sensor data are updated, the content in this dict is updated automatically since they are just pointers.
        self.all_sensor_data = {}

        # Start simuation
        self.restart(config, spawn_point)
        # Tick the world to bring the ego vehicle actor into effect
        self.carla_world.tick()

    def restart(self, config, spawn_point=None):
        """
        Start the simulation with the configuration arguments.

        It spawns the actors including ego vehicle and sensors. If the ego vehicle exists already,
        it respawns the vehicle either at the same location or at the designated location.
        """
        # Set up carla engine using config
        settings = self.carla_world.get_settings()
        settings.no_rendering_mode = config['world']['no_rendering']
        settings.synchronous_mode = config['world']['sync_mode']
        settings.fixed_delta_seconds = config['world']['delta_seconds']
        self.carla_world.apply_settings(settings)

        self.tm.set_synchronous_mode(config['world']['sync_mode'])

        # Spawn a car as the ego vehicle
        ego_veh_bp = self.carla_world.get_blueprint_library().filter('*vehicle*')[0]
        ego_veh_bp.set_attribute('role_name', 'hero')

        if self.ego_veh:
            if spawn_point is None:
                print("Respawning ego vehicle.")
                spawn_point = self.ego_veh.get_transform()
            else:
                print("Respawning ego vehicle at assigned point.")
            # Destroy previously spawned actors
            self.destroy()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.ego_veh = self.carla_world.try_spawn_actor(
                ego_veh_bp, spawn_point)
            if self.ego_veh is None:
                print('Chosen spawn point failed.')

        else:
            if spawn_point:
                print("Spawning new ego vehicle at assigned point.")
                spawn_point.location.z += 2.0
                self.ego_veh = self.carla_world.try_spawn_actor(
                    ego_veh_bp, spawn_point)

        while self.ego_veh is None:
            if not self.map.get_spawn_points():
                print('There are no spawn points available in your map/town.')
                sys.exit(1)
            print("Spawning new ego vehicle at a random point.")
            spawn_points = self.map.get_spawn_points()
            spawn_point = random.choice(
                spawn_points) if spawn_points else carla.Transform()
            self.ego_veh = self.carla_world.try_spawn_actor(
                ego_veh_bp, spawn_point)

        # Point the spectator to the ego vehicle
        self.see_ego_veh()

    def add_carla_sensor(self, carla_sensor: CarlaSensor):
        """
        Add a CarlaSensor.

        This sensor will be added to the carla_sensors list, and all_sensor_data will add a new key-value pair,
        where the key is the same as the carla_sensor's name and the value is the reference to carla_sensor's data.
        """
        if carla_sensor.name in self.carla_sensors.keys():
            raise RuntimeError(
                'Trying to add a CarlaSensor with a duplicate name.')

        # Add the CarlaSensor
        self.carla_sensors[carla_sensor.name] = carla_sensor
        # Register the CarlaSensor's data to all_sensor_data
        self.all_sensor_data[carla_sensor.name] = carla_sensor.data

    def set_ego_autopilot(self, active, autopilot_config=None):
        """
        Set traffic manager and register ego vehicle to it.

        This makes use of the traffic manager provided by Carla to control the ego vehicle.
        See https://carla.readthedocs.io/en/latest/adv_traffic_manager/ for more info.
        """
        if autopilot_config:
            self.tm.auto_lane_change(
                self.ego_veh, autopilot_config['auto_lane_change'])
            self.tm.ignore_lights_percentage(
                self.ego_veh, autopilot_config['ignore_lights_percentage'])
            self.tm.vehicle_percentage_speed_difference(
                self.ego_veh, autopilot_config['vehicle_percentage_speed_difference'])
        self.ego_veh.set_autopilot(active, self.tm.get_port())

    def force_lane_change(self, to_left):
        """
        Force ego vehicle to change the lane regardless collision with other vehicles.

        It only allows lane changes in the possible direction.
        Carla's traffic manager doesn't seem to always respect this command.

        Input:
            to_left: boolean to indicate the direction of lane change.
        """
        # carla uses true for right
        self.tm.force_lane_change(self.ego_veh, not to_left)


    def step_forward(self):
        """
        Tick carla world to take simulation one step forward.

        Output:
            bool to indicate if should keep running.
        """
        keep_running = True
        self.carla_world.tick()

        # Update CarlaSensors' data
        for carla_sensor in self.carla_sensors.values():
            carla_sensor.update()

        return keep_running

    def see_ego_veh(self, following_dist=5, height=5, tilt_ang=-30):
        """ Aim the spectator down to the ego vehicle. """
        spect_location = carla.Location(x=-following_dist)
        self.ego_veh.get_transform().transform(
            spect_location)  # it modifies passed-in location
        ego_rotation = self.ego_veh.get_transform().rotation
        self.spectator.set_transform(carla.Transform(spect_location + carla.Location(z=height),
                                                     carla.Rotation(pitch=tilt_ang, yaw=ego_rotation.yaw)))

    def allow_free_run(self):
        """ Allow carla engine to run asynchronously and freely. """
        settings = self.carla_world.get_settings()
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = 0.0
        self.carla_world.apply_settings(settings)

    def destroy(self):
        """ Destroy spawned actors in carla world. """
        if self.ego_veh:
            print("Destroying the ego vehicle.")
            self.ego_veh.destroy()
            self.ego_veh = None

        for carla_sensor in self.carla_sensors.values():
            carla_sensor.destroy()

        self.carla_sensors.clear()