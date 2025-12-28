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

class Product:
    def __init__(self, name, price):
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = price
    
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Product) and self.id == other.id

class Inventory:
    def __init__(self):
        self.stock: Dict[Product, int] = {}
    
    def addStock(self, product: Product, quantity: int):
        self.stock[product] = quantity
    
    def checkStock(self, product: Product, quantity: int):
        return self.stock.get(product, 0) >= quantity
    
    def updateStock(self, product: Product, quantity):
        self.stock[product] -= quantity

class Cart:
    def __init__(self):
        self.items: Dict[Product, int] = {}
    
    def addToCart(self, product: Product, quantity: int):
        self.items[product] = self.items.get(product, 0) + quantity
    
    def getItems(self):
        return self.items
    
    def removeProduct(self, product: Product):
        self.items.pop(product, None)
    
    def getTotalPrice(self):
        return sum(
            product.price * qty
            for product, qty in self.items.items()
        )

class OrderItem:
    def __init__(self, product: Product, quantity):
        self.product = product
        self.quantity = quantity
        self.price = product.price  

class Payment:
    def __init__(self):
        self.status = PaymentStatus.INITIATED
    
    def pay(self):
        raise NotImplementedError

class CardPayment(Payment):
    def pay(self):
        self.status = PaymentStatus.SUCCESS
        print("Paid using card")
        return True

class UpiPayment(Payment):
    def pay(self):
        self.status = PaymentStatus.SUCCESS
        print("Paid using Upi")
        return True

class Order:
    def __init__(self, items: List[OrderItem], payment: Payment, inventory: Inventory):
        self.id = str(uuid.uuid4())
        self.items = items
        self.payment = payment
        self.inventory = inventory
        self.orderStatus = OrderStatus.CREATED
        self.deliveryAgent = None
    
    def placeOrder(self):
        for item in self.items:
            if not self.inventory.checkStock(item.product, item.quantity):
                raise Exception("Out of stock")
        
        if self.payment.pay():
            for item in self.items:
                self.inventory.updateStock(item.product, item.quantity)
            self.orderStatus = OrderStatus.PAID
    
    def assignDeliveryAgent(self, agent):
        if self.orderStatus != OrderStatus.PAID:
            raise Exception("Order not ready for delivery")
        self.deliveryAgent = agent
        self.orderStatus = OrderStatus.PACKED
    
    def updateStatus(self, status: OrderStatus):
        self.orderStatus = status

class Address:
    def __init__(self, street, area, city, pincode):
        self.street = street
        self.area = area
        self.city = city
        self.pincode = pincode

class User:
    def __init__(self, name, email, address: Address):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.address = address
    
    def searchProduct(self, inventory: Inventory, productName: str):
        return [
            p for p, q in inventory.stock.items()
            if p.name.lower() == productName.lower()
        ]
    
    def addProductToCart(self, cart: Cart, product: Product, qty: int):
        cart.addToCart(product, qty)
        print("Product added:", product.name)
        return product
    
    def removeProductFromCart(self, cart: Cart, product: Product):
        cart.removeProduct(product)
        print("Product removed:", product.name)
        return cart
    
    def placeOrder(self, cart: Cart, payment: Payment, inventory: Inventory):
        items = [
            OrderItem(p, q) for p, q in cart.getItems().items()
        ]
        return Order(items, payment, inventory)

    def trackOrder(self, order: Order):
        return order.orderStatus

class DeliveryAgent:
    def __init__(self, name, phone):
        self.id = str(uuid.uuid4())
        self.name = name
        self.phone = phone
        self.isAvailable = True

    def assignOrder(self, order: Order):
        if not self.isAvailable:
            raise Exception("Agent not available")
        self.isAvailable = False
        order.assignDeliveryAgent(self)

    def deliverOrder(self, order: Order):
        order.updateStatus(OrderStatus.OUT_FOR_DELIVERY)
        order.updateStatus(OrderStatus.DELIVERED)
        print("Delivered")
        self.isAvailable = True


inventory = Inventory()

mobile = Product("Mobile", 10000)
laptop = Product("Laptop", 20000)

inventory.addStock(mobile, 5)
inventory.addStock(laptop, 5)

inventory.checkStock(mobile, 2)
inventory.checkStock(laptop, 3)

cart = Cart()
address = Address('Neknampur', 'Manikonda', 'Hyderabad', '500089')

user = User('manu', 'manu@gmail.com', address)

user.searchProduct(inventory, 'mobile')

user.addProductToCart(cart, mobile, 2)
user.addProductToCart(cart, laptop, 1)

user.removeProductFromCart(cart, laptop)

agent = DeliveryAgent("Ravi", "9999999999")

payment = CardPayment()

order = user.placeOrder(cart, payment, inventory)
order.placeOrder()

agent.assignOrder(order)
agent.deliverOrder(order)

print(order.orderStatus)
 