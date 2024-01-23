
from src.util import get_args
from src.collector import DataCollector
from src.config import WEATHER_CONFIG

if __name__ == '__main__':
    args = get_args()
    DataCollector(
        ip=args.ip,
        port=args.port,
        map_name=args.map,
        is_large_map=args.large_map,
        weather_config = WEATHER_CONFIG if args.weather else None,
        is_sync_mode=args.sync,
        is_spectator=args.spectator,
        img_width=args.width,
        img_height=args.height
)
