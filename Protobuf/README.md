# Installation

We use Protocol Buffers v2. If using OS X, execute:

        brew update && brew install protobuf
        pip install requests protobuf

# Run

Before you run you must compile the protobufs, execute:

        make

Then to run the server, execute:

        python server.py

Then to run the client, execute:

        python client.py

NOTE: If python complains that build.protobufs doesn't exist, place __init__.py files (that are empty) in the build/ folder and the build/protobufs folder.

# Usage

Once you are in the client program you may issue the following commands from the command line

     /adduser <user name>

Adds a user name that can be logged into. Throws an error of a user or a group with that name already exists.

     /group <group name>

Adds a group with the given name with no members. Throws an error of a user or a group with that name already exists.

    /invite <group name> <username>

Adds that user to the specified group, if either don't exist it throws an error.

    /listusers <pattern default=*>

Lists all users on the server filtering user names by the pattern (which recognizes only wildcard charecters). The default if no pattern is given is to match all users.

    /listgroups <pattern default=*>

Lists all groups on the server filtering group names by the pattern (which recognizes only wildcard charecters). The default if no pattern is given is to match all groups.

    /login <user name>

Log the client in under the given user name.

    /logout

Log out the client.

    /dm <username> <message>

This sends a message to that user.

    /gm <groupname> <message>

This sends a message to that user.

    /leaveforever

If logged in under a username this deletes your user from the server forever, and removes the user from all groups they are in.

    /get

If logged in under a username this retrieves any new messages in your queue on the server

    /mvg <groupname>

This sets the current recipient to that group.

    /mvu <username>

This sets the current recipient to that user.

    /mvo

This sets the current recipient to None.

Simply typing in characters without a slash command will send them from the logged in user to the current recipient.

NOTE: Logging in does not validate the username. It is simply a client-side convenience. 
