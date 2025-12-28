from typing import List, Dict
from enum import Enum
from datetime import datetime
import uuid

class OrderStatus(Enum):
    CREATED = 'CREATED'
    PAYMENT_PENDING = 'PAYMENT_PENDING'
    PAID = 'PAID'
    PACKED = 'PACKED'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'
    DELIVERED = 'DELIVERED'
    CANCELED = 'CANCELED'

class PaymentStatus(Enum):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class FoodDeliverySystem:
    def __init__(self):
        self.restaurants: List["Restaurant"] = []
    
    def addRestaurant(self, restaurant):
        self.restaurants.append(restaurant)
    
    def getRestaurants(self):
        return self.restaurants

class Inventory:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.stock: Dict[Food, int] = {}
    
    def getStock(self):
        return self.stock
    
    def addStock(self, food, qty):
        self.stock[food] = self.stock.get(food, 0) + qty
    
    def checkStock(self, food, qty):
        return self.stock.get(food, 0) >= qty
    
    def updateStock(self, food, qty):
        self.stock[food] -= qty

class Menu:
    def __init__(self):
        self.menu: List["Food"] = []
    
    def addFoodToMenu(self, food):
        self.menu.append(food)
    
    def getMenu(self):
        return self.menu

class Food:
    def __init__(self, name, price):
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = price
    
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Food) and self.id == other.id

class Address:
    def __init__(self, street: str, area: str, city: str, pincode: int):
        self.street = street
        self.area = area
        self.city = city
        self.pincode = pincode

class Restaurant:
    def __init__(self, name, address: Address, inventory: Inventory, menu: Menu):
        self.id = str(uuid.uuid4())
        self.name = name
        self.address = address
        self.inventory = inventory
        self.menu = menu


class CartItem:
    def __init__(self, food: Food, quantity: int, price: int):
        self.id = str(uuid.uuid4())
        self.food = food
        self.quantity = quantity
        self.price = price


class Cart:
    def __init__(self):
        self.items: Dict["Food", int] = {}
    
    def addToCart(self, food: Food, quantity: int):
        self.items[food] = self.items.get(food, 0) + quantity
        print("Item added")
    
    def getItems(self):
        return self.items
    
    def removeProduct(self, food: Food):
        self.items.pop(food, None)
        print("Item removed")
    
    def getTotalPrice(self):
        return sum(
            product.price * qty
            for product, qty in self.items.items()
        )

class OrderItem:
    def __init__(self, food: Food, quantity: int, price: int):
        self.id = str(uuid.uuid4())
        self.food = food
        self.quantity = quantity
        self.price = price

class Order:
    def __init__(self, items: List[OrderItem], payment: "Payment", restaurant: Restaurant):
        self.id = str(uuid.uuid4())
        self.items = items
        self.orderStatus = OrderStatus.CREATED
        self.createdAt = datetime.now()
        self.payment = payment
        self.restaurant = restaurant
        self.deliveryPartner = None
    
    def assignDeliveryPartner(self, agent: "DeliveryPartner"):
        self.deliveryPartner = agent
        self.orderStatus = OrderStatus.PACKED
    
    def updateStatus(self, orderStatus: OrderStatus):
        self.orderStatus = orderStatus
    
    def placeOrder(self):
        for item in self.items:
            if not self.restaurant.inventory.checkStock(item.food, item.quantity):
                raise Exception("Out of stock")
        
        if self.payment.pay():
            for item in self.items:
                self.restaurant.inventory.updateStock(item.food, item.quantity)
            self.orderStatus = OrderStatus.PAID

class DeliveryAssignmentService:
    def assign(self, order: Order, agents: List["DeliveryPartner"]):
        if order.orderStatus != OrderStatus.PAID:
            raise Exception("Order not ready")

        for agent in agents:
            if agent.isAvailable:
                agent.acceptOrder()
                order.assignDeliveryPartner(agent)
                return agent
        raise Exception("No agent available")

class Payment:
    def __init__(self):
        self.paymentStatus = PaymentStatus.INITIATED
    
    def pay(self):
        raise NotImplementedError

class CardPayment(Payment):
    def pay(self):
        self.paymentStatus = PaymentStatus.SUCCESS
        return True

class UPIPayment(Payment):
    def pay(self):
        self.paymentStatus = PaymentStatus.SUCCESS
        return True

class OrderTrack:
    def track(order: Order):
        return order.orderStatus

class Person:
    def __init__(self, name, phone):
        self.id = str(uuid.uuid4())
        self.name = name
        self.phone = phone

class DeliveryPartner(Person):
    def __init__(self, name, phone):
        super().__init__(name, phone)
        self.isAvailable = True
    
    def acceptOrder(self):
        if not self.isAvailable:
            raise Exception("Agent not available")
        self.isAvailable = False
    
    def deliveryOrder(self, order: Order):
        order.updateStatus(OrderStatus.OUT_FOR_DELIVERY)
        order.updateStatus(OrderStatus.DELIVERED)
        print("Food delivered")
        self.isAvailable = True

class Admin(Person):
    def addRestaurant(self, system: FoodDeliverySystem, restaurant: Restaurant):
        system.addRestaurant(restaurant)
    
    def updateMenu(self, menu: Menu, food: Food):
        menu.addFoodToMenu(food)
    
    def updateInventory(self, restaurant: Restaurant, food: Food, qty: int):
        restaurant.inventory.addStock(food, qty)

class User(Person):
    def __init__(self, name, phone, address: Address):
        super().__init__(name, phone)
        self.address = address
    
    def searchRestaurant(self, system: FoodDeliverySystem, restaurantName):
        return [
            restaurant for restaurant in system.restaurants 
            if restaurant.name.lower() == restaurantName.lower()
        ]
    
    def selectRestaurant(self, system: FoodDeliverySystem, restaurantName):
        return (restaurant for restaurant in system.restaurants 
                if restaurant.name.lower() == restaurantName.lower())
    
    def addToCart(self, cart: Cart, food: Food, qty: int):
        cart.addToCart(food, qty)
    
    def order(self, cart: Cart, payment: Payment, restaurant: Restaurant):
        items = [
            OrderItem(food, qty, food.price) for food, qty in cart.getItems().items()
        ]

        return Order(items, payment, restaurant)
    
    def trackOrder(self, order: Order):
        return order.orderStatus

system = FoodDeliverySystem()

address = Address('Manikonda', 'Manikonda', 'Hyderabad', 500089)

inventory = Inventory()

biryani = Food('Biryani', 200)
pulav = Food('Pulav', 200)

inventory.addStock(biryani, 5)
inventory.addStock(pulav, 5)

menu = Menu()
menu.addFoodToMenu(biryani)
menu.addFoodToMenu(pulav)

restaurant = Restaurant("FoodFood", address, inventory, menu)
system.addRestaurant(restaurant)

cart = Cart()

user = User('manu', 123456789, address)

user.addToCart(cart, biryani, 2)

payment = CardPayment()

order = user.order(cart, payment, restaurant)
order.placeOrder()

agents = [DeliveryPartner("Ravi", 999999999)]
DeliveryAssignmentService().assign(order, agents)

print(order.orderStatus)
