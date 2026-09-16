## System Architecture

### Why gRPC over HTTP/REST for communication between Dispatch Service and Pricing Service
REST is good for client-facing communication. It's better to use gRPC when communicating internally between services. gRPC uses Protocol Buffers (binary serialization) and enforces a strict contract via `.proto` files, meaning both services agree on the exact schema at compile time. This results in faster communication and type safety compared to JSON over REST.

### Components
Client, Dispatch Service, Pricing Service, and MySQL database (SQLite fallback for local dev).

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
- `POST /trips/{id}/complete` — complete a trip, free the driver
- `POST /trips/{id}/cancel` — cancel a trip
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


## Sprint 4

### Containerizing with Docker
Docker solves the "it works on my machine" problem by packaging each service with its dependencies into isolated containers. In this sprint, we containerized the dispatch and pricing services with their own Dockerfiles and added a `docker-compose.yml` to orchestrate all three containers (dispatch, pricing, MySQL). We also swapped SQLite for MySQL and moved credentials to a `.env` file.

### Testing
Tested that the entire system works by spinning up the containers and sending requests using thuderclient. 

## Sprint 5

### Kubernetes
Docker Compose runs everything on one machine. Kubernetes orchestrates containers and handles scaling, self-healing, and rolling deployments. In this sprint, I deployed all three services to a local K8s cluster (Docker Desktop).

**K8s resources created:**
- **Deployments** — define the desired state for each service (image, replicas, env vars). K8s ensures the specified number of pods are always running.
- **Services** — provide stable DNS names for pod-to-pod communication (`mysql:3306`, `pricing:50051`). Pods can die and restart with new IPs, but Services give a fixed endpoint.
- **ConfigMap** — stores non-sensitive config (DATABASE_URL, PRICING_HOST) for the dispatch service.
- **Secret** — stores MySQL credentials (base64 encoded).

In production, I'd use a managed K8s service (AWS EKS, Google GKE) and a managed database (AWS RDS) instead of running MySQL in a pod.

## Sprint 6

### Monitoring
Added observability to the dispatch service using Prometheus and Grafana.

**How it works:**
1. The dispatch service exposes a `/metrics` endpoint (via `prometheus-fastapi-instrumentator`) with data like request counts, latency histograms, and in-progress requests.
2. Prometheus scrapes `/metrics` every 15 seconds and stores the time-series data.
3. Grafana connects to Prometheus as a data source and visualizes the metrics in a dashboard.

**Dashboard panels:**
- **Request Rate** — `rate(http_requests_total[1m])` — requests per second, broken down by endpoint and status code
- **P95 Latency** — `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1m]))` — 95th percentile response time
- **Requests In Progress** — `http_requests_in_progress` — concurrent active requests

## Sprint 7

### Load Testing & Chaos Engineering
Proved the system handles load and recovers from failure.

**Load Testing with Locust:**
- Simulated 50 concurrent users, each creating a driver/rider and repeatedly requesting, confirming, and completing trips
- The full trip lifecycle (request → confirm → complete) runs in a loop, with drivers being freed up after each completed trip
- Observed ~23.8 req/s throughput with p95 latency under 500ms via Grafana

**Surge Pricing:**
- Implemented dynamic surge multiplier based on demand: `surge = active_trips / available_drivers`
- When demand exceeds supply, the pricing service returns higher prices — same concept as Uber's surge pricing

**Chaos Test — K8s Self-Healing:**
- While load was running, killed the dispatch pod with `kubectl delete pod`
- K8s detected the missing pod and automatically spun up a replacement within ~52 seconds
- Grafana dashboard captured the outage and recovery, proving the system is resilient to pod failures

**Endpoints added:**
- `POST /trips/{id}/complete` — completes a trip and frees the driver
- `POST /trips/{id}/cancel` — cancels a trip from REQUESTED or MATCHED state, frees driver if matched