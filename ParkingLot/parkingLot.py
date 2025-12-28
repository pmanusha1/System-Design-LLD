from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime

@dataclass
class ParkingLot:
    name: str
    address: "Address"
    floors: List["ParkingFloor"]
    entryGates: List["EntryGate"]
    exitGates: List["ExitGate"]

@dataclass
class Address:
    street: str
    city: str
    state: str
    pincode: str

@dataclass
class ParkingFloor:
    floorId: int
    isFull: bool
    spots: List["ParkingSpot"]
    displayBoard: "DisplayBoard"

@dataclass
class DisplayBoard:
    freeSpotsAvailable: dict = field(default_factory=dict)

    def updateAvailablespots(self, floorId, count):
        self.freeSpotsAvailable[floorId] = count
    
    def getAvailableSpots(self, floorId):
        return self.freeSpotsAvailable.get(floorId, 0)


@dataclass
class ParkingSpot:
    spotId: int
    isFree: bool
    spotType: "SpotType"
    vehicle: Optional["Vehicle"]

class SpotType(Enum):
    twoWheeler = "twoWheeler"
    fourWheeler = "fourWheeler"

@dataclass
class Vehicle:
    vehicleId: int
    vehicleType: "VehicleType"
    parkingTicket: Optional["ParkingTicket"]
    paymentInfo: Optional["PaymentInfo"]

class VehicleType(Enum):
    twoWheeler = "twoWheeler"
    fourWheeler = "fourWheeler"

@dataclass
class ParkingTicket:
    ticketId: int
    vehicleId: int
    vehicleType: VehicleType
    floorId: int
    spotId: int
    spotTpye: SpotType
    entryTime: datetime
    exitTime: Optional[datetime]
    cost: int
    status: "TicketStatus"

    def updateCost(self, new_cost):
        self.cost = new_cost
    
    def updateExitTime(self, exittime):
        self.exitTime = exittime

class TicketStatus(Enum):
    active = "active"
    paid = "paid"
    lost = "lost"
    expired = "expired"


@dataclass
class Payment:
    def make_payment(self):
        pass

@dataclass
class PaymentInfo(Payment):
    paymentId: int
    amount: int
    ticket: ParkingTicket
    paymentStatus: "PaymentStatus"
    date: datetime

class PaymentStatus(Enum):
    success = "success"
    failed = "failed"
    canceled = "canceled"


@dataclass
class Gate:
    gateId: int
    attendant: "Attendant"

@dataclass
class EntryGate(Gate):
    pass

@dataclass
class ExitGate(Gate):
    pass


@dataclass
class Person:
    id: int
    name: str

@dataclass
class Admin(Person):
    def addFloor(self, parkingLot, floor):
        parkingLot.floors.append(floor)
    
    def addSpot(self, floor, spot):
        floor.spots.append(spot)
    
    def addEntryGate(self, parkingLot, gate):
        parkingLot.entryGates.append(gate)
    
    def addExitGate(self, parkingLot, gate):
        parkingLot.exitGates.append(gate)
    
    def addDisplayBoard(self, parkingLot, floorId, board):
        floor = next((f for f in parkingLot.floors if f.id == floorId), None)
        if floor is None:
            raise Exception(f"Floor with ID {floorId} not found")
        floor.displayBoard = board

@dataclass
class Attendant(Person):
    def processVehicleEntry(self, parkingLot, vehicle):
        for floor in parkingLot.floors:
            for spot in floor.spots:
                if spot.isFree and spot.spotType.value == vehicle.vehicleType.value:
                    spot.isFree = False
                    spot.vehicle = vehicle

                    ticket = ParkingTicket(
                        vehicle.vehicleId,
                        vehicle.vehicleId,
                        vehicle.vehicleType,
                        floor.floorId,
                        spot.spotId,
                        spot.spotType,
                        datetime.now(),
                        None,
                        0,
                        TicketStatus.active
                    )
                    vehicle.parkingTicket = ticket

                    free_count = sum(1 for s in floor.spots)
                    floor.displayBoard.updateAvailablespots(floor.floorId, free_count)

                    return ticket
        raise Exception("No parking spots available")

    def processPayment(self, vehicle):
        if not vehicle.parkingTicket:
            raise Exception("Vehicle has no active ticket")
        
        ticket = vehicle.parkingTicket

        exit_time = datetime.now()
        ticket.updateExitTime(exit_time)

        hours = (exit_time - ticket.entryTime).total_seconds() / 3600
        cost = max(10, int(hours * 10))

        ticket.updateCost(cost)

        payment_info = PaymentInfo(
            ticket.ticketId,
            cost,
            ticket,
            PaymentStatus.success,
            datetime.now()
        )

        vehicle.paymentInfo = payment_info
        return payment_info

@dataclass
class User(Person):
    def parkVehicle(self, attendant, vehicle, parkingLot):
        return attendant.processVehicleEntry(parkingLot, vehicle)

address = Address("Neknampur", "Hyderabad", "Telangana", "500089")
parkingLot = ParkingLot("Parking Lot", address, [], [], [])

board = DisplayBoard()

floor = ParkingFloor(123, False, [], board)

spot = ParkingSpot(1234, True, SpotType.twoWheeler, None)

a1 = Attendant(5679, "a1")
a2 = Attendant(67782, "a2")

entryGate = EntryGate(356, a1)
exitGate = ExitGate(656, a2)

admin = Admin(12, "Admin")
admin.addSpot(floor, spot)
admin.addFloor(parkingLot, floor)
admin.addEntryGate(parkingLot, entryGate)
admin.addExitGate(parkingLot, exitGate)

vehicle = Vehicle(555, VehicleType.twoWheeler, None, None)

user = User(212, "manu")
user.parkVehicle(a1, vehicle, parkingLot)

print("Vehicle Parked Successfully!")
print("Ticket Details:")
print("  Ticket ID:", vehicle.parkingTicket.ticketId)
print("  Floor:", vehicle.parkingTicket.floorId)
print("  Spot:", vehicle.parkingTicket.spotId)
print("  Entry Time:", vehicle.parkingTicket.entryTime)

print("\nDisplay Board:")
for floor in parkingLot.floors:
    print(f"  Floor {floor.floorId} → Free Spots:", floor.displayBoard.getAvailableSpots(floor.floorId))