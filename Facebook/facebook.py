from typing import List, Dict
from datetime import datetime
import uuid

class User:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.followers: List["User"] = []
        self.followings: List["User"] = []
        self.posts: List["Post"] = []

class Post:
    def __init__(self, user: "User", content: str):
        self.id = str(uuid.uuid4())
        self.user = user
        self.content = content
        self.likes: List["Like"] = []
        self.comments: List["Comment"] = []
        self.createdAt = datetime.now()
    
    def __str__(self):
        return f"{self.content} — by {self.user.name} ({len(self.likes)}♥, {len(self.comments)}💬)"

class Like:
    def __init__(self, user: User, post: Post):
        self.id = str(uuid.uuid4())
        self.user = user
        self.post = post

class Comment:
    def __init__(self, user: User, post: Post, content: str):
        self.id = str(uuid.uuid4())
        self.user = user
        self.post = post
        self.content = content

class Message:
    def __init__(self, sender: User, reciver: User, content: str):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = reciver
        self.content = content
        self.timestamp = datetime.now()
        self.read = False
    
    def __str__(self):
        readStatus = "" if self.read else "(unread)"
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.sender.name}: {self.content} {readStatus}"

class PostRepo:
    posts: List["Post"] = []
    
    @classmethod
    def addPost(cls, post: Post):
        cls.posts.append(post)
    
    @classmethod
    def getAllPost(cls):
        return cls.posts

class UserService:
    def createProfile(self, name):
        print('Profile creation')
        return User(name)
    
    def follow(self, follower: User, following: User):
        if follower.id == following.id:
            return
        
        if following not in follower.followings:
            follower.followings.append(following)
            following.followers.append(follower)
    
    def unFollow(self, follower: User, following: User):
        if following in follower.followings:
            follower.followings.remove(following)

        if follower in following.followers:
            following.followers.remove(follower)

class PostService:
    def addPost(self, user: User, content):
        post = Post(user, content)
        print('Adding post')
        user.posts.append(post)
        PostRepo.addPost(post)
        return post
    
    def removePost(self, user: User, post: Post):
        return user.posts.remove(post)
    
    def likePost(self, user: User, post: Post):
        if any(l.user.id == user.id  for l in post.likes): 
            return len(post.likes)
        
        like = Like(user, post)
        post.likes.append(like)
        return len(post.likes)
    
    def commentOnPost(self, user: User, post: Post, content: str):
        comment = Comment(user, post, content)
        post.comments.append(comment)
        return comment
    
class FeedService:
    def getFriendsFeed(self, user: User):
        feed: List["Post"] = []
        for followee in user.followings:
            feed.extend(followee.posts)
        return sorted(feed, key = lambda p: p.createdAt, reverse=True)

    def getGlobalFeed(self):
        return sorted(PostRepo.getAllPost(), key = lambda p: p.createdAt, reverse= True)

class Chat:
    def __init__(self, u1: User, u2: User):
        self.id = str(uuid.uuid4())
        self.participants = {u1.id, u2.id}
        self.messages: List["Message"] = []
    
    def addMessage(self, message: Message):
        self.messages.append(message)

class ChatRepo:
    chats: Dict[str, Chat] = {}

    @staticmethod
    def getChatId(u1: User, u2: User):
        return '-'.join(sorted([u1.id, u2.id]))
    
    @classmethod
    def getOrCreateChat(cls, u1: User, u2: User):
        chatId = cls.getChatId(u1, u2)
        if chatId not in cls.chats:
            cls.chats[chatId] = Chat(u1, u2)
        return cls.chats[chatId]

class ChatService:
    def sendMessage(self, sender: User, receiver: User, content: str):
        chat = ChatRepo.getOrCreateChat(sender, receiver)
        msg = Message(sender, receiver, content)
        chat.addMessage(msg)
        return msg
    
    def getChat(self, sender: User, receiver: User):
        chat = ChatRepo.getOrCreateChat(sender, receiver)
        return chat.messages
    
    def markAllRead(self, viewer: User, sender: User):
        chat = ChatRepo.getOrCreateChat(viewer, sender)
        for msg in chat.messages:
            if msg.receiver.id == viewer.id:
                msg.read = True


u1 = User("Manu")
u2 = User("Lavi")
us = UserService()
ps = PostService()
fs = FeedService()

us.follow(u1, u2)

p = ps.addPost(u2, "Good Morning")
ps.likePost(u1, p)
ps.commentOnPost(u1, p, "Hello!")

print("Friends Feed:")
for post in fs.getFriendsFeed(u1):
    print(post)

print("\nGlobal Feed:")
for post in fs.getGlobalFeed():
    print(post)

chatService = ChatService()

chatService.sendMessage(u1, u2, "Hey Lavi")
chatService.sendMessage(u2, u1, "Hi Manu!")
chatService.sendMessage(u1, u2, "How are you?")

# view chat as Manu
for msg in chatService.getChat(u1, u2):
    print(msg)

# mark unread messages as read for Manu
chatService.markAllRead(u1, u2)

# view chat as Manu
for msg in chatService.getChat(u2, u1):
    print(msg)
