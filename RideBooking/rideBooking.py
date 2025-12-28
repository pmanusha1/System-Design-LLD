from typing import List
from enum import Enum
from datetime import datetime
import uuid
import math

class VehicleType(Enum):
    CAR = "CAR"
    AUTO = "AUTO"
    BIKE = "BIKE"

class RideStatus(Enum):
    REQUESTED = "REQUESTED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class LocationService:
    def __init__(self):
        self.locations: List["Location"] = []
    
    def addLocation(self, location):
        self.locations.append(location)
    
    def getLocations(self):
        return self.locations
    
    def searchLocation(self, loc: str):
        return [l for l in self.locations if l.name.lower() == loc.lower()]

class Location:
    def __init__(self, name: str, x: float, y: float):
        self.name = name
        self.x = x
        self.y = y

class Vehicle:
    def __init__(self, id: str, vehicleType: VehicleType):
        self.id = id
        self.vehicleType = vehicleType

class User:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

class Driver:
    def __init__(self, id: str, name: str, vehicle: Vehicle, currentLocation: Location):
        self.id = id
        self.name = name
        self.vehicle = vehicle
        self.currentLocation = currentLocation
        self.available = True

class Ride:
    def __init__(self, user: User, driver: Driver, source: Location, destination: Location, fare: float):
        self.id = str(uuid.uuid4())
        self.user = user
        self.driver = driver
        self.source = source
        self.destination = destination
        self.fare = fare
        self.rideStatus = RideStatus.REQUESTED
        self.startTime = datetime.now()
    
    def completeRide(self):
        self.rideStatus = RideStatus.COMPLETED

class FareCalculator:
    Base_Rate = {
        VehicleType.BIKE: 5,
        VehicleType.AUTO: 10,
        VehicleType.CAR: 15
    }
    
    @staticmethod
    def calculateFare(source: Location, destination: Location, vehicleType: VehicleType):
        distance = math.sqrt(
            (source.x - destination.x) ** 2 + 
            (source.y - destination.y) ** 2
        )

        return distance * FareCalculator.Base_Rate[vehicleType]

class RideService:
    def bookRide(self, user: User, driver: Driver, source: Location, destination: Location, vehicleType: VehicleType):
        if not driver.available or driver.vehicle.vehicleType != vehicleType:
            return None
        
        fare = FareCalculator.calculateFare(source, destination, vehicleType)
        ride = Ride(user, driver, source, destination, fare)

        driver.available = False
        ride.rideStatus = RideStatus.CONFIRMED
        return ride

class Payment:
    def __init__(self, ride: Ride):
        self.id = str(uuid.uuid4())
        self.ride = ride
        self.paymentStatus = PaymentStatus.PENDING
    
    def makePayment(self):
        self.paymentStatus = PaymentStatus.COMPLETED
        self.ride.rideStatus = RideStatus.COMPLETED


user = User('123', 'manu')

source = Location('Home', 0, 0)
destination = Location('Office', 5, 5)

vehicle = Vehicle('2323', VehicleType.AUTO)
driver = Driver('23', 'driver', vehicle, source)

rideService = RideService()
ride = rideService.bookRide(user, driver, source, destination, vehicle.vehicleType)

if ride:
    ride.completeRide()
    payment = Payment(ride)
    payment.makePayment()

    print("Ride Fare:", ride.fare)
    print("Ride Status:", ride.rideStatus.value)
    print("Payment Status:", payment.paymentStatus.value)
else:
    print("Ride booking failed")
    