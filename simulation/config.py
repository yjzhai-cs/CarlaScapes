
from path import Path

PROJECT_DIR = Path(__file__).parent.parent.abspath()

WorldConfig = {
    'world': {
        'weather': 1,
        'no_rendering': False, # Activate no rendering mode
        'sync_mode': True,
        'delta_seconds': 0.05,
    },
    'ego_veh': {

    }
}

RGBCameraConfig = {
    'img_width': '2048', # image resolution (default: 2048x1024)
    'img_height': '1024', # image resolution (default: 2048x1024)
    'fov': '70',
    'pos_x': 1.5,
    'pos_z': 2.4,
    'sensor_trick': 1.5, # Sensor trick (default: 1.5)
}

GNSSConfig = {
    'noise_alt_bias': '0.0',
    'noise_alt_stddev': '0.0',
    'noise_lat_bias': '0.0',
    'noise_lat_stddev': '0.0',
    'noise_lon_bias': '0.0',
    'noise_lon_stddev': '0.0',
    'pos_x': 1.5,
    'sensor_trick': 1.5,
}

InstanceCameraConfig = {
    'img_width': '2048',
    'img_height': '1024',
    'fov': '70',
    'pos_x': 1.5,
    'pos_z': 2.4,
    'sensor_trick': 1.5,
}

SemanticCameraConfig = {
    'img_width': '2048',
    'img_height': '1024',
    'fov': '70',
    'pos_x': 1.5,
    'pos_z': 2.4,
    'sensor_trick': 1.5,
}

RecorderConfig = {
    'save_path': PROJECT_DIR / "outputs/",
    'capacity': 8,
}

GeneratorConfig = {
    'tm_port': 8000, # Port to communicate with TM (default: 8000)
    'distance_to_leading_vehicle': 2.5,
    'respawn_dormant_vehicles': True, # Automatically respawn dormant vehicles (only in large maps)
    'hybrid_physics_mode': True, # Activate hybrid mode for Traffic Manager
    'hybrid_physics_radius': 70.0,
    'random_device_seed': None,
    'sync_mode': True,
    'filterv': 'vehicle.*', # Filter vehicle model (default: "vehicle.*")
    'generationv': 'All', # restrict to certain vehicle generation (values: "1","2","All" - default: "All")
    'filterw': 'walker.pedestrian.*', # Filter pedestrian type (default: "walker.pedestrian.*")
    'generationw': '2', # restrict to certain pedestrian generation (values: "1","2","All" - default: "2")
    'safe': True, # Avoid spawning vehicles prone to accidents
    'number_of_vehicles': 20, # Number of vehicles (default: 20)
    'number_of_walkers': 100, # Number of walkers (default: 100)
    'hero': False, # Set one of the vehicles as hero
    'car_lights_on': False, # Enable automatic car light management
    'seedw': 0, # Set the seed for pedestrians module
    'percentagePedestriansRunning':0.25,
    'percentagePedestriansCrossing':0.15,
}