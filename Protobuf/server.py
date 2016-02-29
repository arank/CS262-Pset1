# ********************************************
# TODO : What do we do if a user sends a message, then deletes themself?
#        (the unreceived message has a ref to a deleted user)
# ********************************************

from flask import Flask
from build import request_pb2 as RequestProtoBuf
import model

app = Flask(__name__)

USERS = UserList()
GROUPS = GroupList()

#
# Users
#

@app.get("/users")
def listUsers():
    return USERS.serialize()

@app.post("/users/:username")
def createUser(username):
    if USERS.usernameExists(username):
        raise UserError("User Exists")

    user = User(username)
    USERS.addUser(user)
    return user.serialize()

@app.delete("/users/:username")
def deleteUser(username):
    if not USERS.usernameExists(username):
        raise UserError("Missing User")

    USERS.deleteUser(username)
    GROUPS.pruneUser(username)

#
# Groups
#

@app.get("/groups")
def listGroups():
    return GROUPS.serialize()

@app.post("/groups/:groupname")
def createGroup(groupname):
    if GROUPS.groupnameExists(groupname):
        raise UserError("Group Exists")

    group = Group(groupname)
    GROUPS.addGroup(group)
    return group.serialize()

@app.put("/groups/:groupname/users/:username")
def addUserToGroup(groupname, username):
    group = GROUPS.getGroup(groupname)
    if group is None:
        raise UserError("Missing Group")

    if not USERS.usernameExists(username):
        raise UserError("User does not exist")

    group.addUser(username)
    return group.serialize()

#
# Messages
#

def decodeMessage(request):
    # TODO: fix this
    message = RequestProtoBuf.Message.unwrap(request.body)

    if message.msg is None || msg == '':
        raise UserError("Invaid Message Body")

    fromUser = USERS.getUser(message.from)
    if fromUser is None:
        raise UserError("Invaid from User")

    return fromUser, msg

@app.post("/users/:username/messages")
def sendDirectMessage(username):
    msg, fromUser = decodeMessage(request)
    toUser = USERS.getUser(username)
    if toUser is None:
        raise UserError("Missing To User")

    message = DirectMessage(fromUser, toUser, msg)
    toUser.receiveMessage(message)
    return True

@app.post("/groups/:groupname/messages")
def sendGroupMessage(groupname):
    msg, fromUser = decodeMessage(request)
    toGroup = GROUPS.getGroup(groupname)
    if toGroup is None:
        raise UserError("Missing To Group")

    message = GroupMessage(fromUser, toGroup, msg)
    toGroup.receiveMessage(message, USERS)
    return True

@app.get("/users/:username/messages")
def listMessages(username):
    user = USERS.getUser(username)
    if user is None:
        raise UserError("Missing User")

    return user.flushMessages()

if __name__ == "__main__":
    app.run()
