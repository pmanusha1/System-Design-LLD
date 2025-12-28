from typing import List
from enum import Enum
from datetime import datetime
import uuid

class Address:
    def __init__(self, street: str, area: str, city: str, pincode: str):
        self.street = street
        self.area = area
        self.city = city
        self.pincode = pincode

class HotelBookingSystem:
    def __init__(self):
        self.hotels: List["Hotel"] = []
        self.bookings: List["Booking"] = []
    
    def addHotel(self, hotel):
        self.hotels.append(hotel)
    
    def getHotels(self):
        return self.hotels
    
    def addBooking(self, booking: "Booking"):
        self.bookings.append(booking)
    
    def getBookings(self):
        return self.bookings
    
    def cancelBooking(self, bookingId: str):
        booking = next((b for b in self.bookings if b.id == bookingId), None)
        if not booking:
            return None
        
        booking.bookingStatus = BookingStatus.CANCELED
        booking.room.roomStatus = RoomStatus.AVAILABLE

        if booking.payment and booking.payment.paymentStatus == PaymentStatus.COMPLETED:
            booking.payment.paymentStatus = PaymentStatus.REFUNDED
        return True
    
    def isRoomAvailable(self, room: "Room", checkIn: datetime, checkout: datetime):
        for booking in self.bookings:
            if booking.room == room and booking.bookingStatus != BookingStatus.CANCELED:
                if checkIn < booking.checkOut and checkout > booking.checkIn:
                    return False
        return True

class Hotel:
    def __init__(self, id: str, name: str, address: "Address"):
        self.id = id
        self.name = name
        self.address = address
        self.rooms: List["Room"] = []
    
    def addRoom(self, room):
        self.rooms.append(room)
    
    def getRooms(self):
        return self.rooms

class Room:
    def __init__(self, id: str, roomType: "RoomType", roomStatus: "RoomStatus", price):
        self.id = id
        self.roomType = roomType
        self.roomStatus = roomStatus
        self.price = price

class RoomType(Enum):
    STANDARD = "STANDARD"
    VIP = "VIP"
    DELUXE = "DELUXE"

class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    NOTAVAILABLE = "NOTAVAILABLE"

class BookingStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"

class PaymentStatus(Enum):
    UNPAID = "UNPAID"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"

class Payment:
    def __init__(self, amount: int):
        self.id = str(uuid.uuid4())
        self.amount = amount
        self.date = datetime.now()
        self.paymentStatus = PaymentStatus.PENDING
    
    def completePayment(self):
        self.paymentStatus = PaymentStatus.COMPLETED

class Booking:
    def __init__(self, user: "User", hotel: "Hotel", room: "Room", checkIn: datetime, checkOut: datetime):
        self.id = str(uuid.uuid4())
        self.user = user
        self.hotel = hotel
        self.room = room
        self.checkIn = checkIn
        self.checkOut = checkOut
        self.bookingDate = datetime.now()
        self.bookingStatus = BookingStatus.CONFIRMED
        self.payment: Payment | None = None


class Search:
    def searchByHotelName(self, hotelBookingSystem: HotelBookingSystem, hotelName: str):
        return [
            h for h in hotelBookingSystem.hotels
            if h.name.lower() == hotelName.lower()
        ]
    
    def searchByCity(self, hotelBookingSystem: HotelBookingSystem, city: str):
        return [
            h for h in hotelBookingSystem.hotels
            if h.address.city.lower() == city.lower()
        ]
    
    def searchByRoomType(self, hotelBookingSystem: HotelBookingSystem, roomType: "RoomType"):
        res = []
        for hotel in hotelBookingSystem.hotels:
            for room in hotel.rooms:
                if room.roomType == roomType and room.roomStatus == RoomStatus.AVAILABLE:
                    res.append((hotel, room))
        return res
    
    def searchByPriceRange(self, hotelBookingSystem: HotelBookingSystem, minPrice: int, maxPrice: int):
        res = []
        for hotel in hotelBookingSystem.hotels:
            for room in hotel.rooms:
                if minPrice <= room.price <= maxPrice and room.roomStatus == RoomStatus.AVAILABLE:
                    res.append((hotel,room))
        return res

class Person:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
        self.search: "Search" = Search()

class Admin(Person):
    def addHotel(self, hotelBookingSystem: HotelBookingSystem, hotel: Hotel):
        hotelBookingSystem.addHotel(hotel)
    
    def updateHotel(self, hotelBookingSystem: HotelBookingSystem, hotelId: str):
        return next((hotel for hotel in hotelBookingSystem.hotels if hotel.id == hotelId), None)

    def removeHotel(self, hotelBookingSystem: HotelBookingSystem, hotelid: str):
        hotelBookingSystem.hotels = [hotel for hotel in hotelBookingSystem.hotels if hotel.id != hotelid]

    def addRoom(self, hotel: Hotel, room: Room):
        hotel.addRoom(room)
    
    def updateRoom(self, hotel: Hotel, roomId: str):
        return next((room for room in hotel.rooms if room.id == roomId), None)

    def removeRoom(self, hotel: Hotel, roomId: str):
        hotel.rooms = [room for room in hotel.rooms if room.id != roomId]

class User(Person):
    def __init__(self, id: str, name: str, email: str):
        super().__init__(id, name, email)
        self.bookings: List["Booking"] = []
    
    def reserveRoom(self, hotelBookingSystem: "HotelBookingSystem", hotel: Hotel, room: "Room", checkIn: datetime, checkOut: datetime):
        if room.roomStatus != RoomStatus.AVAILABLE:
            return None
    
        if not hotelBookingSystem.isRoomAvailable(room, checkIn, checkOut):
            return None
        
        room.roomStatus = RoomStatus.RESERVED
        booking = Booking(self, hotel, room, checkIn, checkOut)
        self.bookings.append(booking)
        hotelBookingSystem.addBooking(booking)
        return booking

    def makePayment(self, booking: "Booking"):
        if booking.bookingStatus == BookingStatus.CONFIRMED and not booking.payment:
            payment = Payment(booking.room.price)
            payment.completePayment()
            booking.payment = payment
            booking.room.roomStatus = RoomStatus.NOTAVAILABLE
            return payment
        return None

    def getBookings(self):
        return self.bookings

    def cancelBooking(self, hotelBookingSystem: HotelBookingSystem, bookingId):
        return hotelBookingSystem.cancelBooking(bookingId)
        

system = HotelBookingSystem()

address = Address('Neknampur', 'Manikonda', 'Hyderabad', '500089')

hotel = Hotel('12', '9 Star', address)

room1 = Room('34', RoomType.DELUXE, RoomStatus.AVAILABLE, 2000)
room2 = Room('33', RoomType.VIP, RoomStatus.AVAILABLE, 3000)

admin = Admin('11', 'admin', 'admin@gmail.com')

admin.addHotel(system, hotel)
admin.addRoom(hotel, room1)
admin.addRoom(hotel, room2)

user = User('55', 'manu', 'manu@gmail.com')
check_in = datetime(2025, 1, 10)
check_out = datetime(2025, 1, 12)

booking = user.reserveRoom(system, hotel, room1, check_in, check_out)
user.makePayment(booking)

if booking:
    print("Booking Successful")
    print("Booking ID:", booking.id)
    print("Hotel:", booking.hotel.name)
    print("Room ID:", booking.room.id)
    print("Room Status:", booking.room.roomStatus.value)
    print("Check-in:", booking.checkIn)
    print("Check-out:", booking.checkOut)

    payment = user.makePayment(booking)
    if payment:
        print("\nPayment Successful")
        print("Payment ID:", payment.id)
        print("Amount:", payment.amount)
        print("Payment Status:", payment.paymentStatus.value)
        print("Room Status After Payment:", booking.room.roomStatus.value)
else:
    print("Booking Failed")



