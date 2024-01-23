
from path import Path

PROJECT_DIR = Path(__file__).parent.parent.abspath()
OUTPUT_PATH =  PROJECT_DIR / "outputs/"


WEATHER_CONFIG = {
    "cloudiness": 10.0,
    "precipitation": 10.0,
    "fog_density": 10.0
}