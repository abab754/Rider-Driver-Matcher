from fastapi import APIRouter, Depends, HTTPException
from dispatch_service.schemas import CreateDriver, DriverInfo, CreateRider, RiderInfo, TripRequest, TripResponse
from sqlalchemy.orm import Session                                                                    
from dispatch_service.database import get_db
from dispatch_service.models import Driver, Rider, Trip
from dispatch_service.matching import find_nearest_driver
from dispatch_service.pricing_client import get_price

router = APIRouter()

## Create a Driver
@router.post("/drivers")
def create_driver(driver: CreateDriver, db: Session = Depends(get_db)):
    ## Creates a sqlAlchemy Driver object with the pydantic driver's props
    db_driver = Driver(name=driver.name, latitude=driver.latitude, longitude=driver.longitude)

    ## Adds the db_driver to the database
    db.add(db_driver)
    db.commit()
    ## Refreshes the driver and returns an id with it
    db.refresh(db_driver)

    ## Stores the refreshed driver's props to returning_driver and returns
    return DriverInfo.model_validate(db_driver)

## Create a Rider
@router.post("/riders")
def create_rider(rider: CreateRider, db: Session = Depends(get_db)):
    db_rider = Rider(name=rider.name, latitude=rider.latitude, longitude=rider.longitude)

    db.add(db_rider)
    db.commit()
    db.refresh(db_rider)

    return RiderInfo.model_validate(db_rider)

## Requests a trip and stores it in the db
@router.post("/trips/request")
def request_trip(tripRequest: TripRequest, db: Session = Depends(get_db)):
    ## Query DB for rider with the requests rider_id
    rider = db.query(Rider).filter(Rider.id == tripRequest.rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    ## Creates a Trip with status == Requested
    db_trip = Trip(
        rider_id=tripRequest.rider_id, 
        status="REQUESTED", 
        pickup_lat=rider.latitude, 
        pickup_long=rider.longitude, 
        dropoff_lat=tripRequest.dropoff_lat, 
        dropoff_long=tripRequest.dropoff_long
    )

    available_drivers = db.query(Driver).filter(Driver.is_available == True).count()                                       
    active_trips = db.query(Trip).filter(Trip.status.in_(["REQUESTED", "MATCHED"])).count()                           
    surge = max(1.0, active_trips / max(available_drivers, 1)) 

    ## Calls get_price() from the pricing_client
    price, distance = get_price(
        db_trip.pickup_lat, 
        db_trip.pickup_long,
        db_trip.dropoff_lat,
        db_trip.dropoff_long,
        surge 
    )

    ## Updates the trip's price field before committing
    db_trip.price = price

    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    return TripResponse.model_validate(db_trip)

@router.post("/trips/{id}/confirm")
def confirm_trip(id: int, db: Session = Depends(get_db)):
    ## Get trip that we need to update
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.status != "REQUESTED":
        raise HTTPException(status_code=400, detail="Trip cannot be confirmed")
    
    ## get the nearest avail driver we found from dispatch service
    driver = find_nearest_driver(trip.pickup_lat, trip.pickup_long, db)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    ## set the trip's status = MATCHED
    trip.status = "MATCHED"

    ## Set the driver as the trip's driver
    trip.driver_id = driver.id

    ## set driver's status = Unavailable
    driver.is_available = False

    db.commit()
    db.refresh(trip)

    return TripResponse.model_validate(trip)

@router.get("/trips/{id}")
def get_trip(id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    return TripResponse.model_validate(trip)

@router.post("/trips/{id}/complete")
def complete_trip(id: int, db: Session = Depends(get_db)):
    ## Get trip that we need to update
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.status != "MATCHED":
        raise HTTPException(status_code=400, detail="Trip cannot be completed")

    trip.status = "COMPLETED"

    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_available = True

    db.commit()
    db.refresh(trip)

    return TripResponse.model_validate(trip)

@router.post("/trips/{id}/cancel")
def cancel_trip(id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.status not in ["REQUESTED", "MATCHED"]:
        raise HTTPException(status_code=400, detail="Trip cannot be cancelled")

    # If a driver was matched, free them up
    if trip.driver_id:
        driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        driver.is_available = True

    trip.status = "CANCELLED"

    db.commit()
    db.refresh(trip)

    return TripResponse.model_validate(trip)
