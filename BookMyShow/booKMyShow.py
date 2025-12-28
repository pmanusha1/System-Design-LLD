from typing import List
from enum import Enum
from datetime import datetime

class BookMyShow:
    def __init__(self):
        self.cinemaHalls: List["CinemaHall"]= []
        self.movies: List["Movie"] = []
    
    def addCinemaHall(self, cinemahall):
        self.cinemaHalls.append(cinemahall)
    
    def addMovie(self, movie):
        self.movies.append(movie)

    def getCinemaHalls(self):
        return self.cinemaHalls

    def getMovies(self):
        return self.movies

class CinemaHall:
    def __init__(self, id: str, name: str, address: "Address"):
        self.id = id
        self.name = name
        self.address = address
        self.audis: List["Audi"] = []
    
    def addAudi(self, audi):
        self.audis.append(audi)

class Address:
    def __init__(self, street: str, area: str, city: str, pincode: str):
        self.street = street
        self.area = area
        self.city = city
        self.pincode = pincode

class Audi:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.seats: List["Seat"] = []
        self.shows: List["Show"] = []
    
    def addSeat(self, seat):
        self.seats.append(seat)
    
    def addShow(self, show):
        self.shows.append(show)

class Seat:
    def __init__(self, id: str, seatType: "SeatType", price: int):
        self.id = id
        self.seatType = seatType
        self.seatStatus = SeatStatus.Available
        self.price = price

class SeatType(Enum):
    Deluxe = "Deluxe"
    Vip = "Vip"
    Standrad = "Standard"

class SeatStatus(Enum):
    Available = "Available"
    Booked = "Booked"
    Reserved = "Reserved"
    Notavailable = "Not available"

class Show:
    def __init__(self, id: str, movie: "Movie", audi: "Audi", startTime: datetime, endTime: datetime):
        self.id = id
        self.movie = movie
        self.audi = audi
        self.startTime = startTime
        self.endTime = endTime
        self.seats: List["Seat"] = [
            Seat(seat.id, seat.seatType, seat.price) for seat in audi.seats
        ]
    

class Movie:
    def __init__(self, id: str, name: str, language: "Language", genre: "Genre", duration: int):
        self.id = id
        self.name = name
        self.language = language
        self.genre = genre
        self.duration = duration

class Language(Enum):
    Telugu = "Telugu"
    English = "English"
    Hindi = "Hindi"

class Genre(Enum):
    Drama = "Drama"
    Romcom = "Romcom"
    fantasy = "Fantasy"

class User:
    def __init__(self, id: str):
        self.id = id
        self.search = Search()


class SystemUser(User):
    def __init__(self, id: str, account: "Account", name: str, email: str):
        super().__init__(id)
        self.account = account
        self.name = name
        self.email = email

class Account:
    def __init__(self, id: str, accountName: str, password: str):
        self.id = id
        self.accountName = accountName
        self.password = password

class Admin(SystemUser):
    def addCinemaHall(self, bookMyShow, cinemahall):
        bookMyShow.addCinemaHall(cinemahall)
    
    def addMovie(self, bookMyShow, movie):
        bookMyShow.addMovie(movie)
    
    def addAudi(self, CinemaHall, audi):
        CinemaHall.addAudi(audi)
    
    def addShow(self, audi, show):
        audi.addShow(show)

class Member(SystemUser):
    def __init__(self, id, account, name, email):
        super().__init__(id, account, name, email)
        self.bookings: List["Booking"] = []
    
    def book(self, show, seatId):
        seat = next((s for s in show.seats if s.id == seatId), None)
        if not seat:
            raise Exception("Seat not found")
        
        if seat.seatStatus != SeatStatus.Available:
            raise Exception("Seat not available")
        
        seat.seatStatus = SeatStatus.Booked

        payment = Payment("pay10", seat.price, datetime.now(), PaymentStatus.Completed)

        booking = Booking("b1", self, show, show.movie, seat, seat.price, BookingStatus.Confirmed, payment)
        self.bookings.append(booking)

        return booking

    def getBookings(self):
        return self.bookings


class Search:
    def getMovieByName(self, movies, name):
        return [m for m in movies if m.name.lower() == name.lower()]

    def MovieByLanguage(self, movies, language):
        return [m for m in movies if m.language == language]

    def getMovieByGerne(self, movies, genre):
        return [m for m in movies if m.genre == genre]


class Booking:
    def __init__(self, id: str, user: "User", show: "Show", movie: "Movie", seat: "Seat", amount: int, bookingStatus: "BookingStatus", payment: "Payment"):
        self.id = id
        self.user = user
        self.show = show
        self.movie = movie
        self.seat = seat
        self.amount = amount
        self.bookingStatus = bookingStatus
        self.payment = payment
    
    def __str__(self):
        return (
            f"Booking(id={self.id}, "
            f"movie={self.movie.name}, "
            f"seat={self.seat.id}, "
            f"amount={self.amount}, "
            f"status={self.bookingStatus.value})"
        )
   
    def __repr__(self):
        return self.__str__()

class BookingStatus(Enum):
    Requested = "requested"
    Pending = "pending"
    Confirmed = "confirmed"
    Canceled = "canceled"


class Payment:
    def __init__(self, id: str, amount: int, date: datetime, paymentStatus: "PaymentStatus"):
        self.id = id
        self.amount = amount
        self.date = date
        self.paymentStatus = paymentStatus

class PaymentStatus(Enum):
    Unpaid = "unpaid"
    Pending = "pending"
    Completed = "completed"
    Canceled = "canceled"
    Refunded = "refunded"

address = Address("Alkapur", "Manikonda", "Hyderabad", "800059")

bookMyShow = BookMyShow()

cinemahall = CinemaHall('12', "IMAX", address)

movie = Movie('33', "System Design", Language.English, Genre.Drama, 120)

audi = Audi('1234', "L1")

seat1 = Seat('77', SeatType.Vip, 320)
seat2 = Seat('78', SeatType.Deluxe, 250)

audi.addSeat(seat1)
audi.addSeat(seat2)

show = Show('99', movie, audi, datetime.now(), datetime.now())

accountadmin = Account('11', "AdminAccount", "12345")

admin = Admin('123', accountadmin, "Admin", "admin@gmail.com")

admin.addCinemaHall(bookMyShow, cinemahall)
admin.addMovie(bookMyShow, movie)
admin.addAudi(cinemahall, audi)
admin.addShow(audi, show)

accountmem = Account('35', "Manusha", '12345')
user = Member('44', accountmem, "Manusha", "manusha@gmail.com")

booking = user.book(show, seat1.id)

bookings = user.getBookings()

print("Booking Successful")
print("Bookings..", bookings)
print("Seat:", booking.seat.id)
print("Status:", booking.seat.seatStatus)

