## Sprint 1

### Why gRPC over HTTP/REST for communication between Dispatch service and Pricing Service
REST is good for client facing communication. It's better to use gRPC when communicating internally between services. This is because there is an agreed upon schema for form of communication between the services at compile time allowing for faster communication.  

### Components
We have our Client, Dispatch Service, Pricing Service, and our MySQL database.

### How they work with each other
1) Our Client will send a request to the Dispatch Service
2) The Dispatch Service will then query the Database for the nearest availlable driver
3) The Dispatch Service will then talk to the Pricing Service via gRPC 
4) The Dispatch service returns the driver details and the price to the Client(Rider)
5) The rider will either confirm or deny the ride

### DB Schema
Drivers, Riders, and Trips

Drivers:
Status - Available, Unavailable, Driving
Location

Riders:
Location

Trips:
Status - InProgress, Matched, Requested, Completed, Cancelled
Start_Location
End_Location
Duration

### Endpoints
Dispatch Service
GET /api/v1/driver -> find nearest availble driver
POST /api/v1/trips/request -> creates a trip with status initially set to Requested
