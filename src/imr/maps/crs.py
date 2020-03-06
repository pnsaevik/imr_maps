from osgeo import osr
import numpy as np


EPSG_CODES = dict(
    wgs84=4326,
    utm29n=32629,
    utm30n=32630,
    utm31n=32631,
    utm32n=32632,
    utm33n=32633,
    utm34n=32634,
    utm35n=32635,
    utm36n=32636,
    etrs89=4258,
    etrs89_utm29n=25829,
    etrs89_utm30n=25830,
    etrs89_utm31n=25831,
    etrs89_utm32n=25832,
    etrs89_utm33n=25833,
    etrs89_utm34n=25834,
    etrs89_utm35n=25835,
    etrs89_utm36n=25836,
)


class SpatialReference(osr.SpatialReference):
    @staticmethod
    def from_epsg(code):
        proj = SpatialReference()
        proj.ImportFromEPSG(code)
        return proj

    @staticmethod
    def from_wkt(wkt):
        proj = SpatialReference()
        proj.ImportFromWkt(wkt)
        return proj

    @staticmethod
    def from_grid_mapping(grid_mapping):
        return SpatialReference.from_wkt(grid_mapping.crs_wkt)

    @staticmethod
    def local(lon, lat):
        wkt = f"""
            PROJCS["Local ETRS89",
                GEOGCS["ETRS89",
                    DATUM["European_Terrestrial_Reference_System_1989",
                        SPHEROID["GRS 1980",6378137,298.257222101,
                            AUTHORITY["EPSG","7019"]],
                        AUTHORITY["EPSG","6258"]],
                    PRIMEM["Greenwich",0,
                        AUTHORITY["EPSG","8901"]],
                    UNIT["degree",0.01745329251994328,
                        AUTHORITY["EPSG","9122"]],
                    AUTHORITY["EPSG","4258"]],
                UNIT["metre",1,
                    AUTHORITY["EPSG","9001"]],
                PROJECTION["Transverse_Mercator"],
                PARAMETER["latitude_of_origin", {lat}],
                PARAMETER["central_meridian", {lon}],
                PARAMETER["scale_factor",1.0],
                PARAMETER["false_easting",0],
                PARAMETER["false_northing",0],
                AXIS["Easting",EAST],
                AXIS["Northing",NORTH]]
                """

        return SpatialReference.from_wkt(wkt)

    @staticmethod
    def nf160(named_area, metric_unit=False):
        params = {
            'A01': (18704, 10752, 160, 70, 'NF160_A01'),
            'A02': (19254, 10352, 160, 70, 'NF160_A02'),
            'A03': (19254, 9282, 160, 70, 'NF160_A03'),
            'A04': (18854, 8992, 160, 70, 'NF160_A04'),
            'A05': (18104, 8922, 160, 70, 'NF160_A05'),
            'A06': (16904, 8582, 160, 70, 'NF160_A06'),
            'A07': (16074, 9082, 160, 70, 'NF160_A07'),
            'A08': (14804, 8932, 160, 70, 'NF160_A08'),
            'A09': (14054, 8932, 160, 70, 'NF160_A09'),
            'A10': (12954, 8802, 160, 70, 'NF160_A10'),
            'A11': (11554, 8952, 160, 70, 'NF160_A11'),
            'A12': (10004, 9422, 160, 70, 'NF160_A12'),
            'A13': (8754, 10552, 160, 70, 'NF160_A13'),
        }
        return SpatialReference.nk800(*params[named_area], metric_unit=metric_unit)

    @staticmethod
    def nk800(xp=3991, yp=2230, dx=800, ylon=70, name='NK800', metric_unit=False):
        if metric_unit:
            unit_str = 'UNIT["metre",1,AUTHORITY["EPSG","9001"]]'
            dx_unit = dx
        else:
            unit_str = f'UNIT["Cells",{dx}]]'
            dx_unit = 1

        wkt = f"""PROJCS["{name}",
            GEOGCS["ETRS89",
                DATUM["European_Terrestrial_Reference_System_1989",
                    SPHEROID["GRS 1980",6378137,298.257222101,
                        AUTHORITY["EPSG","7019"]],
                    AUTHORITY["EPSG","6258"]],
                PRIMEM["Greenwich",0,
                    AUTHORITY["EPSG","8901"]],
                UNIT["degree",0.01745329251994328,
                    AUTHORITY["EPSG","9122"]],
                AUTHORITY["EPSG","4258"]],
            PROJECTION["Polar_Stereographic"],
            PARAMETER["latitude_of_origin",60],
            PARAMETER["central_meridian",{ylon}],
            PARAMETER["scale_factor",1],
            PARAMETER["false_easting",{xp * dx_unit}],
            PARAMETER["false_northing",{yp * dx_unit}],
            {unit_str}"""

        return SpatialReference.from_wkt(wkt)

    @staticmethod
    def transform(x, y, from_crs, to_crs):
        if len(y) == 0 and len(x) == 0:
            return np.array([x, y])

        ct = osr.CoordinateTransformation(from_crs, to_crs)

        points = np.array([x, y, np.zeros_like(x)]).T
        return np.array(ct.TransformPoints(points)).T[:2]
