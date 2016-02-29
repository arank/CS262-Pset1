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
        self.users.append(newUser)
        return newUser

    def listAccounts(self):
        return self.users.keys()

    def createGroup():
        pass

    def listGroups():
        return self.groups.keys()

    def sendMessage(toname, isgroup, fromname, message):
        

    def fetchMessages(username):
        if name not in self.users:
            raise APIError("Missing User")
        return self.users.get(username).receiveMessage()

    def deleteAccount(username):
        user = self.users.pop(username, None)

        if user is None:
            raise APIError("Missing User")

        user.cleanupGroups()
