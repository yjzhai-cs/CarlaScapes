
from path import Path

PROJECT_DIR = Path(__file__).parent.parent.abspath()

WorldConfig = {
    'world': {
        'weather': 1,
        'no_rendering': False,
        'sync_mode': True,
        'delta_seconds': 0.05,
    },
    'ego_veh': {

    }
}

RGBCameraConfig = {
    'img_width': '2048',
    'img_height': '1024',
    'fov': '70',
    'pos_x': 1.5,
    'pos_z': 2.4,
    'sensor_trick': 1.5,
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