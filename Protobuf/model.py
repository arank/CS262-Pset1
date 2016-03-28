import re
from sets import Set
from build.protobufs import response_pb2 as ResponseProtoBuf

#
# These are effectively syntatic sugar for the ProtoBufs. They allow us to set
# properties on these objects and simply call the .serialize() when we want a
# protobuf represeantion.
#

# A single user
class User(object):
    def __init__(self, username):
        self.username = username
        # this is a list of messages that still need to be delivered to the user
        self.undeliveredMessages = MessageList()

    def serialize(self):
        user = ResponseProtoBuf.User()
        user.username = self.username
        return user

    def receiveMessage(self, message):
        self.undeliveredMessages.addMessage(message)

    # returns undelivered messages and empties the internal list of messages to
    # deliver
    def flushMessages(self):
        messages = self.undeliveredMessages.serialize()
        self.undeliveredMessages = MessageList()
        return messages

# a list of users
class UserList(object):
    def __init__(self):
        self.users = {}

    def usernameExists(self, username):
        return username in self.users

    def getUser(self, username):
        return self.users.get(username)

    def addUser(self, user):
        self.users[user.username] = user

    def filter(self, query):
        userList = UserList()

        regex = re.compile(query.replace('*', '.*'))
        userList.users = { u: v for u, v in self.users.items() if regex.match(u) }

        return userList

    # Assumes a user with username exists
    def deleteUser(self, username):
        del self.users[username]

    def serialize(self):
        users = ResponseProtoBuf.UserList()
        users.users.extend([u.serialize() for u in self.users.values()])
        return users

# a group, which includes 0 or more users
class Group(object):
    def __init__(self, groupname):
        self.groupname = groupname
        self.users = Set()

    def addUser(self, user):
        self.users.add(user)

    def pruneUser(self, user):
        self.users.discard(user)

    def receiveMessage(self, message, userList):
        for user in self.users:
            user.receiveMessage(message)

    def serialize(self):
        group = ResponseProtoBuf.Group()
        group.groupname = self.groupname
        group.users.extend([u.serialize() for u in self.users])
        return group

# a list of groups
class GroupList(object):
    def __init__(self):
        self.groups = {}

    def groupnameExists(self, groupname):
        return groupname in self.groups

    def getGroup(self, groupname):
        return self.groups.get(groupname)

    def addGroup(self, group):
        self.groups[group.groupname] = group

    def filter(self, query):
        groupList = GroupList()

        regex = re.compile(query.replace('*', '.*'))
        groupList.groups = { g: v for g, v in self.groups.items() if regex.match(g) }

        return groupList

    def pruneUser(self, username):
        for group in self.groups.values():
            group.pruneUser(username)

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

    def serialize(self):
        message = ResponseProtoBuf.Message()
        message.frm.CopyFrom(self.frm.serialize())
        message.msg = self.msg
        return message

# A list of messages.
class MessageList(object):
    def __init__(self):
        self.messages = []

    def addMessage(self, message):
        self.messages.append(message)

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


class UserError(Exception):
    def __init__(self, message):
        self.message = message

    def serialize(self):
        userError = ResponseProtoBuf.UserError()
        userError.message = self.message
        return userError
