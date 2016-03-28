from flask import Flask, request
import re
from google.protobuf.message import DecodeError
from build.protobufs import request_pb2 as RequestProtoBuf
from model import User, UserList, Group, GroupList, UserError, GroupMessage, DirectMessage
from functools import wraps

app = Flask(__name__)

#
# Maintain global variables to act as a pseudo-database for all users and groups.
#
# N.B. There is no persistence, in that when the server restarts all information
# about users and groups is lost.
#

USERS = UserList()
GROUPS = GroupList()

# If the response is a ProtoBuf object, then we should serialize it into a string
# that will be returned in the HTTP response body. The @protoapi annotation is
# a piece of middleware that should wrap around all API methods. It is also
# responsible for catching UserErrors, which can be thrown by a methods to
# indicate that the user has supplied invalid request parameters.
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
# API user methods
#

# Validates that the query string contains only alphanumeric characters and
# wildcards, then returns the global list of users filtered to the query.
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

# Creates a user object and adds it to the global user list.
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

# Deletes a user, removing them from any groups they may have joined. Note that
# an undelivered messages could potentially still hold a reference to the user
# object, and so the object will remain in memory until all such messages are
# flushed.
@app.route("/v1/users/<username>", methods=["DELETE"])
@protoapi
def deleteUser(username):
    if not USERS.usernameExists(username):
        raise UserError("Missing User")

    USERS.deleteUser(username)
    GROUPS.pruneUser(username)

    return None

#
# API group methods
#

# Validates that the query string contains only alphanumeric characters and
# wildcards, then returns the global list of users filtered to the query.
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

# Creates a new group object with no users and adds it to the global group
# list
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

# Adds a user to a group by name.
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

# The ProtoBuf encoded message is sent as a string in the request body.
# We parse the string into a new Python ProtoBuf message object, and
# return the message string as well as the Python object for the sender.
def decodeMessage(request):
    message = RequestProtoBuf.Message()

    try:
        message.ParseFromString(request.data)
    except DecodeError:
        raise UserError("Invaid Message Protocol Buffer")

    if message.msg is None or message.msg == '':
        raise UserError("Invaid Message Body")

    fromUser = USERS.getUser(message.frm)
    if fromUser is None:
        raise UserError("Invalid from User")

    return message.msg, fromUser

# Decode the message and create a new DirectMessage object to be received
# by the user. Responds to the request with the serialized message.
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

# Decode the message and create a new GroupMessage object to be received
# by the user. Responds to the request with the serialized message.
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

# List all the messages for the given user, and clear them from the user's
# message queue so that they are only delivered once.
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
