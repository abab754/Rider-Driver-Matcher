## System Architecture

### Why gRPC over HTTP/REST for communication between Dispatch Service and Pricing Service
REST is good for client-facing communication. It's better to use gRPC when communicating internally between services. gRPC uses Protocol Buffers (binary serialization) and enforces a strict contract via `.proto` files, meaning both services agree on the exact schema at compile time. This results in faster communication and type safety compared to JSON over REST.

### Components
Client, Dispatch Service, Pricing Service, and SQLite database (MySQL in production).

### How they work with each other
1) Client sends a trip request to the Dispatch Service (REST)
2) Dispatch Service calls the Pricing Service via gRPC to get a price estimate
3) Dispatch Service returns the price to the Client (Rider)
4) Rider confirms the trip
5) Dispatch Service queries the database for the nearest available driver
6) Dispatch Service matches the driver to the trip and marks the driver as unavailable

### DB Schema
**Drivers:** id, name, latitude, longitude, is_available

**Riders:** id, name, latitude, longitude

**Trips:** id, rider_id, driver_id, status, price, pickup_lat, pickup_long, dropoff_lat, dropoff_long

Trip states: `REQUESTED → MATCHED → IN_PROGRESS → COMPLETED` (or `CANCELLED`)

### Endpoints
- `POST /drivers` — register a new driver
- `POST /riders` — register a new rider
- `POST /trips/request` — request a trip, returns price estimate
- `POST /trips/{id}/confirm` — confirm trip, matches nearest available driver
- `GET /trips/{id}` — get trip status
- `GET /health` — health check


## Sprint 2

### Haversine Distance
Because we are calculating the nearest drivers to the rider on the earth which is a sphere, we cannot simply calcualate the euclidean distance between the two. That would yield the wrong result. That's where the haversine distance comes in: it calculates the shortest distance between two points on a sphere given the latitudes and longitudes of the two points. 

## Sprint 3

### Getting 2 Services to talk to each other
As mentioned earlier, the dispatch service and the pricing service will be using gRPC to talk to each other. In this sprint, I defined a protobuf file with the message response and request as well as the GetPrice function.

The Pricing Service will expect a PriceRequest which has the pickup and dropoff coordinates. I also added a surge_multiplier prop for when the demand for drivers is high. That's for a later time though. 

After the pricing service gets the request, it'll call GetPrice and return a PriceResponse message which has the estimated price and the distance from the pickup location to the dropoff location. 

### Files added
1) pricing_service/server.py - starts a server
2) proto/pricing.proto - defines the message structs that the Pricing service takes and responds with
3) dispatch_service/pricing_client.py - connects to the pricing service's server and abstracts the getprice logic

### Files modified
1) dispatch_service/routes.py - modified the request trip endpoint
