# ********************************************
# TODO : What do we do if a user sends a message, then deletes themself?
#        (the unreceived message has a ref to a deleted user)
# ********************************************

from flask import Flask, request
import re
from build.protobufs import request_pb2 as RequestProtoBuf
from model import User, UserList, Group, GroupList, UserError, GroupMessage, DirectMessage
from functools import wraps

app = Flask(__name__)

USERS = UserList()
GROUPS = GroupList()

def protoapi(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            response = f(*args, **kwargs)
            if response is None:
                return "Success"
            return response.SerializeToString()
        except UserError as ue:
            return ue.serialize().SerializeToString(), 400
    return wrapped

#
# Users
#

@app.route("/v1/users", methods=["GET"])
@protoapi
def listUsers():
    query = request.args.get('q')
    if query:
        starless = query.replace('*', '')
        if starless and not starless.isalnum():
            raise UserError("Invalid Query")

        return USERS.filter(query).serialize()
    else:
        return USERS.serialize()

@app.route("/v1/users/<username>", methods=["POST"])
@protoapi
def createUser(username):
    if not username.isalnum():
        raise UserError("Invalid Username, Must Be Alphanumeric")
    elif USERS.usernameExists(username):
        raise UserError("User Exists")

    user = User(username)
    USERS.addUser(user)
    return user.serialize()

@app.route("/v1/users/<username>", methods=["DELETE"])
@protoapi
def deleteUser(username):
    if not USERS.usernameExists(username):
        raise UserError("Missing User")

    USERS.deleteUser(username)
    GROUPS.pruneUser(username)

    return None

#
# Groups
#

@app.route("/v1/groups", methods=["GET"])
@protoapi
def listGroups():
    query = request.args.get('q')
    if query:
        starless = query.replace('*', '')
        if starless and not starless.isalnum():
            raise UserError("Invalid Query")

        return GROUPS.filter(query).serialize()
    else:
        return GROUPS.serialize()

@app.route("/v1/groups/<groupname>", methods=["POST"])
@protoapi
def createGroup(groupname):
    if not groupname.isalnum():
        raise UserError("Invalid Groupname, Must Be Alphanumeric")
    elif GROUPS.groupnameExists(groupname):
        raise UserError("Group Exists")

    group = Group(groupname)
    GROUPS.addGroup(group)
    return group.serialize()

@app.route("/v1/groups/<groupname>/users/<username>", methods=["PUT"])
@protoapi
def addUserToGroup(groupname, username):
    group = GROUPS.getGroup(groupname)
    if group is None:
        raise UserError("Missing Group")

    if not USERS.usernameExists(username):
        raise UserError("User does not exist")

    group.addUser(USERS.getUser(username))
    return group.serialize()

#
# Messages
#

def decodeMessage(request):
    message = RequestProtoBuf.Message()
    message.ParseFromString(request.data)

    if message.msg is None or message.msg == '':
        raise UserError("Invaid Message Body")

    fromUser = USERS.getUser(message.frm)
    if fromUser is None:
        raise UserError("Invalid from User")

    return message.msg, fromUser

@app.route("/v1/users/<username>/messages", methods=["POST"])
@protoapi
def sendDirectMessage(username):
    msg, fromUser = decodeMessage(request)
    toUser = USERS.getUser(username)
    if toUser is None:
        raise UserError("Missing To User")

    message = DirectMessage(fromUser, toUser, msg)
    toUser.receiveMessage(message)
    return message.serialize()

@app.route("/v1/groups/<groupname>/messages", methods=["POST"])
@protoapi
def sendGroupMessage(groupname):
    msg, fromUser = decodeMessage(request)
    toGroup = GROUPS.getGroup(groupname)
    if toGroup is None:
        raise UserError("Missing To Group")

    message = GroupMessage(fromUser, toGroup, msg)
    toGroup.receiveMessage(message, USERS)
    return message.serialize()

@app.route("/v1/users/<username>/messages", methods=["GET"])
@protoapi
def listMessages(username):
    user = USERS.getUser(username)
    if user is None:
        raise UserError("Missing User")

    return user.flushMessages()

if __name__ == "__main__":
    # TODO : Not sure we should keep debug in 'prod'
    app.run(debug=True)
