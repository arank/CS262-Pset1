from sets import Set
from build import response_pb2 as ResponseProtoBuf

class User(object):
    def __init__(self, username):
        self.username = username
        self.groups = Set()
        self.undeliveredMessages = MessageList()

    def serialize(self):
        user = ResponseProtoBuf.User()
        user.username = self.username
        user.groupnames.extend([g.groupname for g in self.groups])
        return user

    def receiveMessage(self, message):
        self.undeliveredMessages.addMessage(message)

    def flushMessages(self):
        messages = self.undeliveredMessages.serialize()
        self.undeliveredMessages = MessageList()
        return messages


class UserList(object):
    def __init__(self):
        self.users = {}

    def usernameExists(self, username):
        return username in self.users

    def getUser(self, username):
        return self.users.get(username)

    def addUser(self, user):
        self.users[user.username] = user

    # Assumes a user with username exists
    def deleteUser(self, username):
        del self.users[username]

    def serialize(self):
        users = ResponseProtoBuf.UserList()
        users.users.extend([u.serialize() for u in self.users.values()])
        return users


class Group(object):
    def __init__(self, groupname):
        self.groupname = groupname
        self.usernames = Set()

    def addUser(self, username):
        self.usernames.add(username)

    def pruneUser(self, username):
        self.usernames.discard(username)

    def receiveMessage(self, message, userList):
        for username in self.usernames:
            user = userList.getUser(username)
            assert user is not None
            user.receiveMessage(message)

    def serialize(self):
        group = ResponseProtoBuf.Group()
        group.groupname = self.groupname
        group.usernames.extend([u.username for u in self.users])
        return group


class GroupList(object):
    def __init__(self):
        self.groups = {}

    def groupnameExists(self, groupname):
        return groupname in self.groups

    def getGroup(self, groupname):
        return self.groups.get(groupname)

    def addGroup(self, group):
        self.groups[group.groupname] = group

    def pruneUser(self, username):
        for group in self.groups.values():
            group.pruneUser(username)

    def serialize(self):
        groups = ResponseProtoBuf.GroupList()
        groups.groups.extend([g.serialize() for g in self.groups.values()])
        return groups

class Message(object):
    def __init__(self, frm, to, msg):
        self.frm = frm
        self.to = to
        self.msg = msg

    def serialize(self):
        message = ResponseProtoBuf.Message()
        message.frm = self.frm.username
        message.msg = self.msg
        return message


class MessageList(object):
    def __init__(self):
        self.messages = []

    def addMessage(self, message):
        self.messages.append(message)

    def serialize(self):
        messages = ResponseProtoBuf.MessageList()
        messages.messages.extend([m.serialize() for m in self.messages])
        return messages


class DirectMessage(Message):
    def serialize(self):
        dm = super()
        dm.type = ResponseProtoBuf.Message.DIRECT
        dm.toUser = self.to.username
        return dm


class GroupMessage(Message):
    def serialize(self):
        gm = super()
        dm.type = ResponseProtoBuf.Message.GROUP
        gm.toGroup = self.to.groupname
        return gm


class UserError(Exception):
    def __init__(self, message):
        self.message = message

    def serialize(self):
        userError = ResponseProtoBuf.UserError()
        userError.message = self.message
        return userError
