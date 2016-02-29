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
