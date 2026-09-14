import math
from dispatch_service.models import Driver
import heapq
R = 6371

def find_nearest_driver(rider_lat, rider_long, db):
    drivers_list = db.query(Driver).filter(Driver.is_available == True).all()
    res = []
    for driver in drivers_list:
        d = haversine(rider_lat, rider_long, driver.latitude, driver.longitude)
        heapq.heappush(res, (d, driver.id, driver))

    return None if len(res) == 0 else res[0][2]


def haversine(rider_lat, rider_long, driver_lat, driver_long):
    rider_lat = math.radians(rider_lat)
    rider_long = math.radians(rider_long)
    driver_lat = math.radians(driver_lat)
    driver_long = math.radians(driver_long)

    delta_lat = driver_lat - rider_lat
    delta_long = driver_long - rider_long

    a = math.sin(delta_lat / 2) ** 2 + math.cos(rider_lat) * math.cos(driver_lat) * math.sin(delta_long/2) ** 2
    c = 2 * math.asin(min(1, math.sqrt(a)))
    d = R * c

    return d

