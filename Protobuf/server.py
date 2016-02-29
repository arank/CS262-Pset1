# ********************************************
# TODO : What do we do if a user sends a message, then deletes themself?
#        (the unreceived message has a ref to a deleted user)
# ********************************************

class User(object):
    def __init__(self, name):
        self.name = name
        self.undeliveredMessages = []
        self.groups = []

    def receiveMessage(self, message):
        self.undeliveredMessages.append(message)

    def getMessages(self):
        to_return = self.undeliveredMessages
        self.undeliveredMessages = []
        return to_return

    # DO NOT CALL -- only group should call this
    def _addGroup(self, group):
        self.groups.append(group)

    # DO NOT CALL -- only group should call this
    def _removeGroup(self, group):
        self.groups.remove(group)

    def cleanupGroups(self):
        for group in self.groups:
            group.removeMember(self)

class Group(object):
    def __init__(self, name, members):
        self.name = name
        self.members = []
        for member in members:
            self.addMember(member)

    def addMember(self, member):
        member._addGroup(self)
        self.members.append(member)

    def removeMember(self, member):
        member._removeGroup(self)
        self.members.remove(member)

    def cleanupMembers(self):
        for member in self.members:
            member._removeGroup(self)
        self.members = []

    def receiveMessage(self, message):
        for member in self.members:
            member.receiveMessage(message)

def Message(object):
    def __init__(self, toUser, fromUser, message):
        self.toUser = toUser
        self.fromUser = fromUser
        self.message = message

class APIError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Server262(object):
    def __init__(self):
        self.users = {}
        self.groups = {}

    def createUser(self, name):
        if name in self.users:
            raise APIError("User Exists")
        newUser = User(name)
        self.users[name] = newUser
        return newUser

    def listAccounts(self):
        return self.users.keys()

    def createGroup(self, name, memberNames):
        if name in self.groups:
            return APIError("Group Exists")

        members = [self.users.get(memberName, None) for memberName in memberNames]
        if None in members:
            raise APIError("Member does not exist")

        newGroup = Group(name, memberNames)
        self.groups[name] = newGroup
        return newGroup

    def listGroups(self):
        return self.groups.keys()

    def sendGroupMessage(self, toname, fromname, message):
        toGroup = self.groups.get(toname, None)
        if toUser is None:
            raise APIError("Missing To Group")

        fromUser = self.users.get(fromname, None)
        if fromUser is None:
            raise APIError("Missing From User")

        newMessage = Message(toGroup, fromUser, message)
        toGroup.receiveMessage(newMessage)

    def sendUserMessage(self, toname, fromname, message):
        toUser = self.users.get(toname, None)
        if toUser is None:
            raise APIError("Missing To User")

        fromUser = self.users.get(fromname, None)
        if fromUser is None:
            raise APIError("Missing From User")

        newMessage = Message(toUser, fromUser, message)
        fromUser.receiveMessage(newMessage)

    def fetchMessages(self, username):
        if name not in self.users:
            raise APIError("Missing User")
        return self.users.get(username).receiveMessage()

    def deleteAccount(self, username):
        user = self.users.pop(username, None)

        if user is None:
            raise APIError("Missing User")

        user.cleanupGroups()
