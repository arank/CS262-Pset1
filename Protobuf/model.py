import re
from sets import Set
from build.protobufs import response_pb2 as ResponseProtoBuf

#
# These are effectively syntatic sugar for the ProtoBufs. They allow us to set
# properties on these objects and simply call the .serialize() when we want a
# protobuf represeantion.
#
# We prefer them to the protobuf representations because it allows us to use
# OOP and extend our types with custom methods.
#

# A single user
class User(object):
    def __init__(self, username):
        self.username = username
        # this is a list of messages that still need to be delivered to the user
        self.undeliveredMessages = MessageList()

    # convert to protobuf
    def serialize(self):
        user = ResponseProtoBuf.User()
        user.username = self.username
        return user

    # add a message to the user's undelivered message queue
    def receiveMessage(self, message):
        self.undeliveredMessages.addMessage(message)

    # returns undelivered messages and empties the internal list of messages to
    # deliver
    def flushMessages(self):
        messages = self.undeliveredMessages.serialize()
        self.undeliveredMessages = MessageList()
        return messages

# a set of users
class UserList(object):
    def __init__(self):
        self.users = {}

    # check if a user by username is in the user set
    def usernameExists(self, username):
        return username in self.users

    # get a user by the username (returning None on failure)
    def getUser(self, username):
        return self.users.get(username)

    # add a user object to the set of this object
    def addUser(self, user):
        self.users[user.username] = user

    # construct and return a userlist that is a subset of users in this list
    # who have usernames that match the query.
    #
    # A query takes the form of alphanumeric characters and asterics (where
    # asterics can match unboundedly many of any element). A query must be match
    # some part of the username. For example:
    #
    # J*k will match both Jack and Jak.
    def filter(self, query):
        userList = UserList()

        regex = re.compile(query.replace('*', '.*'))
        userList.users = { u: v for u, v in self.users.items() if regex.match(u) }

        return userList

    # Assumes a user with username exists
    def deleteUser(self, username):
        del self.users[username]

    # return a protobuf
    def serialize(self):
        users = ResponseProtoBuf.UserList()
        users.users.extend([u.serialize() for u in self.users.values()])
        return users

# a group, which includes 0 or more users
class Group(object):
    def __init__(self, groupname):
        self.groupname = groupname
        self.users = Set()

    # add a user to the group
    def addUser(self, user):
        self.users.add(user)

    # remove a user from teh group
    def pruneUser(self, user):
        self.users.discard(user)

    # recieve a message for the group (will be passed on to every member of the
    # group)
    def receiveMessage(self, message, userList):
        for user in self.users:
            user.receiveMessage(message)

    # convert to a protobuf
    def serialize(self):
        group = ResponseProtoBuf.Group()
        group.groupname = self.groupname
        group.users.extend([u.serialize() for u in self.users])
        return group

# a list of groups, fundamentally similar to userlist
class GroupList(object):
    def __init__(self):
        self.groups = {}

    # check if a group by a certain name exists in the set
    def groupnameExists(self, groupname):
        return groupname in self.groups

    # get a group by name
    def getGroup(self, groupname):
        return self.groups.get(groupname)

    # add a group object to the set
    def addGroup(self, group):
        self.groups[group.groupname] = group

    # Construct and return a list of groups whose name match a certain query.
    # See comment above UserList.filter
    def filter(self, query):
        groupList = GroupList()

        regex = re.compile(query.replace('*', '.*'))
        groupList.groups = { g: v for g, v in self.groups.items() if regex.match(g) }

        return groupList

    # remove a user from all groups in the group list
    def pruneUser(self, username):
        for group in self.groups.values():
            group.pruneUser(username)

    # convert to protobuf
    def serialize(self):
        groups = ResponseProtoBuf.GroupList()
        groups.groups.extend([g.serialize() for g in self.groups.values()])
        return groups

# A message representation, contains a from, to, and message. From must be a
# user, although to can be either a group or user.
class Message(object):
    def __init__(self, frm, to, msg):
        self.frm = frm
        self.to = to
        self.msg = msg

    # convert to protobuf
    def serialize(self):
        message = ResponseProtoBuf.Message()
        message.frm.CopyFrom(self.frm.serialize())
        message.msg = self.msg
        return message

# A list of messages.
class MessageList(object):
    def __init__(self):
        self.messages = []

    # add a message to the list
    def addMessage(self, message):
        self.messages.append(message)

    # convert to protobuf
    def serialize(self):
        messages = ResponseProtoBuf.MessageList()
        messages.messages.extend([m.serialize() for m in self.messages])
        return messages

# NOTE: Both DirectMessage and GroupMessage are backed by the Message protobuf
#       they just set different fields to indicate whether they are directed to
#       a user or group and inherit from the Message object.

# A direct message to another user
class DirectMessage(Message):
    def serialize(self):
        dm = super(DirectMessage, self).serialize()
        dm.type = ResponseProtoBuf.Message.DIRECT
        dm.toUser.CopyFrom(self.to.serialize())
        return dm

# A message to a group
class GroupMessage(Message):
    def serialize(self):
        gm = super(GroupMessage, self).serialize()
        gm.type = ResponseProtoBuf.Message.GROUP
        gm.toGroup.CopyFrom(self.to.serialize())
        return gm

# the error to the user from the server if an API call fails (typically user
# error, such as passing in an invalid name for a new user, or name that's
# already taken)
class UserError(Exception):
    def __init__(self, message):
        self.message = message

    def serialize(self):
        userError = ResponseProtoBuf.UserError()
        userError.message = self.message
        return userError
