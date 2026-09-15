from pricing_service.pricing_pb2_grpc import PricingServiceStub
from pricing_service.pricing_pb2 import PriceRequest
import grpc

channel = grpc.insecure_channel("localhost:50051")
pricing_stub = PricingServiceStub(channel)

def get_price(pickup_lat, pickup_long, destination_lat, destination_long, surge_multiplier):
    price_request = PriceRequest(
        pickup_lat=pickup_lat,
        pickup_long=pickup_long,
        destination_lat=destination_lat,
        destination_long=destination_long,
        surge_multiplier=surge_multiplier
    )
    response = pricing_stub.GetPrice(price_request)
    return response.price, response.distance