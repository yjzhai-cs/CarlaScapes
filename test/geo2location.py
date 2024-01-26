
import carla
import numpy as np
import pymap3d as pm

latitude_of_test_point: float = 0.0010455182438988686
longitude_of_test_point: float = -0.0006708842681995106
altitude_of_test_point = 2.225923776626587

a = {"latitude": -0.0005609108267776719, "longitude": 0.001355871740938171, "altitude": 2.4085423946380615}


client = carla.Client('localhost', 2000)
client.set_timeout(50.0)

world = client.get_world()

# obtain CARLA map
map_carla = world.get_map()
map_carla_origin_geo = map_carla.transform_to_geolocation(carla.Location(0.0, 0.0, 0.0))

# Internally Carla performs geodetic (latitude, longitude, altitude) to Cartesian transformations which are not
# quite clear. The Carla documentation reveals that a Mercator projection might be used internally
# (see https://carla.org/Doxygen/html/df/ddb/GeoLocation_8cpp_source.html) however using this transformation did not
# yield the desired results. Therefore a geodetic to east-north-up (ENU) transformation is used
# (mentioned in https://github.com/carla-simulator/carla/issues/2737, implemented in helper function geo_carla2xyz_carla)
# for transforming the measurements of the CARLA GnssSensor to the local coordinate frame of Carla.
# The errors with respect to the ground truth (get_transform().location) are in the magnitude of millimeters which is
# quite high and cannot be explained by rounding errors.
#
# TODO: further investigations might be needed here. New release might solve this issue (see https://github.com/carla-simulator/carla/issues/1848)



def geo_carla2xyz_carla(lat, lon, alt):
    # transforms geodetic location from carla.GnssMeasurement to location in cartesian Carla map frame. However,
    # transformed location and ground truth deviate from each other (see above).

    # after this transformation of the latitude, GNSS projection and ego_vehicle.get_transform().location are "closer"
    lat = pm.geocentric2geodetic(lat, alt, pm.Ellipsoid('wgs84'), deg=True)

    x_enu, y_enu, z_enu = pm.geodetic2enu(lat, lon, alt, map_carla_origin_geo.latitude, map_carla_origin_geo.longitude, map_carla_origin_geo.altitude, pm.Ellipsoid('wgs84'), deg=True)

    # y-coordinate in Carla coordinate system is flipped (see https://github.com/carla-simulator/carla/issues/2737)
    return x_enu, -y_enu, z_enu


print(geo_carla2xyz_carla(latitude_of_test_point, longitude_of_test_point, altitude_of_test_point))
print(geo_carla2xyz_carla(a["latitude"], a["longitude"], a["altitude"]))



class Geo2Location(object):
    """
    Helper class for homogeneous transform from geolocation

    This class is used by GNSS class to transform from carla.GeoLocation to carla.Location.
    This transform is not provided by Carla, but it can be solved using 4 chosen points.
    Note that carla.Location is in the left-handed coordinate system.
    """

    def __init__(self, carla_map):
        """ Constructor method """
        self._map = carla_map
        # Pick 4 points of carla.Location
        loc1 = carla.Location(0, 0, 0)
        loc2 = carla.Location(1, 0, 0)
        loc3 = carla.Location(0, 1, 0)
        loc4 = carla.Location(0, 0, 1)
        # Get the corresponding carla.GeoLocation points using carla's transform_to_geolocation()
        geoloc1 = self._map.transform_to_geolocation(loc1)
        geoloc2 = self._map.transform_to_geolocation(loc2)
        geoloc3 = self._map.transform_to_geolocation(loc3)
        geoloc4 = self._map.transform_to_geolocation(loc4)
        # Solve the transform from geolocation to location (geolocation_to_location)
        l = np.array([[loc1.x, loc2.x, loc3.x, loc4.x],
                      [loc1.y, loc2.y, loc3.y, loc4.y],
                      [loc1.z, loc2.z, loc3.z, loc4.z],
                      [1, 1, 1, 1]], dtype=float)
        g = np.array([[geoloc1.latitude, geoloc2.latitude, geoloc3.latitude, geoloc4.latitude],
                      [geoloc1.longitude, geoloc2.longitude,
                          geoloc3.longitude, geoloc4.longitude],
                      [geoloc1.altitude, geoloc2.altitude,
                          geoloc3.altitude, geoloc4.altitude],
                      [1, 1, 1, 1]], dtype=float)
        # Tform = (G*L^-1)^-1
        self._tform = np.linalg.inv(g.dot(np.linalg.inv(l)))

    def transform(self, geolocation):
        """
        Transform from carla.GeoLocation to carla.Location (left_handed z-up).

        Numerical error may exist. Experiments show error is about under 1 cm in Town03.
        """
        geoloc = np.array(
            [geolocation.latitude, geolocation.longitude, geolocation.altitude, 1])
        loc = self._tform.dot(geoloc.T)
        return carla.Location(loc[0], loc[1], loc[2])

    def get_matrix(self):
        """ Get the 4-by-4 transform matrix """
        return self._tform


geo2location = Geo2Location(world.get_map())
location = geo2location.transform(
    carla.GeoLocation(a["latitude"], a["longitude"], a["altitude"]))
print(location)