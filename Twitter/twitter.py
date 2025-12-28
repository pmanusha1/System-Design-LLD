from typing import List, Dict
from enum import Enum
from datetime import datetime
import uuid

class User:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.followers: List["User"] = []
        self.following: List["User"] = []
        self.tweets: List["Tweet"] = []

class Tweet:
    def __init__(self, user: User, content: str):
        self.id = str(uuid.uuid4())
        self.user = user
        self.userId = user.id
        self.content = content
        self.createdAt = datetime.now()
        self.likes: List["Like"] = []
        self.comments: List["Comment"] = []
    
    def __str__(self):
        return f"{self.content} — by {self.user.name} ({len(self.likes)}♥, {len(self.comments)}💬)"
    
class Like:
    def __init__(self, user: User, tweet: Tweet):
        self.id = str(uuid.uuid4())
        self.userId = user.id
        self.tweetId = tweet.id
        self.createdAt = datetime.now()

class Comment:
    def __init__(self, user: User, tweet: Tweet, content: str):
        self.id = str(uuid.uuid4())
        self.userId = user.id
        self.tweetId = tweet.id
        self.content = content
        self.createdAt = datetime.now()

class UserService:
    def createProfile(self, name):
        return User(name)
    
    def follow(self, follower: User, followee: User):
        if followee == follower: return
        if followee not in follower.following:
            follower.following.append(followee)
            followee.followers.append(follower)
    
    def unFollow(self, follower: User, followee: User):
        if followee in follower.following:
            follower.following.remove(followee)
        
        if follower in followee.followers:
            followee.followers.remove(follower)

class TweetService:
    def createTweet(self, user: User, content):
        tweet = Tweet(user, content)
        user.tweets.append(tweet)
        return tweet
    
    def likeTweet(self, user: User, tweet: Tweet):
        if any(l.userId == user.id for l in tweet.likes):
            return len(tweet.likes)
        like = Like(user, tweet)
        tweet.likes.append(like)
        return len(tweet.likes)
    
    def commentOnTweet(self, user: User, tweet: Tweet, content):
        comment = Comment(user, tweet, content)
        tweet.comments.append(comment)
        return tweet.comments

class FeedService:
    def getTweet(self, user: User):
        feed: List["Tweet"] = []
        for followee in user.following:
            feed.extend(followee.tweets)
        return sorted(feed, key=lambda t: t.createdAt, reverse=True)

userService = UserService()
manu = userService.createProfile('manu')
lavi = userService.createProfile('lavi')

userService.follow(manu, lavi)
userService.follow(lavi, manu)

tweetService = TweetService()
tweet = tweetService.createTweet(manu, "Happy birthday lavi")
tweetService.likeTweet(lavi, tweet)
tweetService.commentOnTweet(lavi, tweet, "Thank you!")

feed = FeedService()
for t in feed.getTweet(lavi):
    print(t)