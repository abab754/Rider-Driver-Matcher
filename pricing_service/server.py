from pricing_pb2_grpc import PricingServiceServicer, add_PricingServiceServicer_to_server
from pricing_pb2 import PriceResponse
import math
import grpc
from concurrent import futures

## Constants
BASE_PRICE = 3.00
COST_PER_KM = 0.23
R = 6371

## Overrides the GetPrice method in PricingServiceServicer
class PricingServicer(PricingServiceServicer):
    def GetPrice(self, request, context):
        distance = haversine(request.pickup_lat, request.pickup_long, request.destination_lat, request.destination_long)

        price = BASE_PRICE + (COST_PER_KM * distance * request.surge_multiplier)
        return PriceResponse(price=price, distance=distance)

## Haversine Distance Formuala
def haversine(lat1, long1, lat2, long2):
    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)

    delta_lat = lat2 - lat1
    delta_long = long2 - long1

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_long/2) ** 2
    c = 2 * math.asin(min(1, math.sqrt(a)))
    d = R * c

    return d

def serve():
    # 1. Initialize a thread-pool backed server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 2. Bind the service implementation to the server
    add_PricingServiceServicer_to_server(PricingServicer(), server)
    
    # 3. Assign an address and port
    server.add_insecure_port('[::]:50051')
    print("Server started on port 50051...")
    
    # 4. Start serving requests
    server.start()
    
    # 5. Keep the main thread alive to continue serving
    server.wait_for_termination()

if __name__ == '__main__':
    serve()