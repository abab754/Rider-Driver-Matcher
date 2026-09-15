from pricing_service.pricing_pb2_grpc import PricingServiceStub
from pricing_service.pricing_pb2 import PriceRequest
import grpc
import os

PRICING_HOST = os.getenv("PRICING_HOST", "localhost:50051")
channel = grpc.insecure_channel(PRICING_HOST)
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