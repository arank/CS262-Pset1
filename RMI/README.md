To run this project you must first complile the class files by running javac -d classes/ -Xlint:unchecked src/chat262/*.java in the RMI
directory.

You must then start up the registry process by running $(cd classes/; rmiregistry)

Once that is set up you can choose to run either the server process by running java chat262.Server262 in the classes directrory
or the client process by running java chat262.ChatClient <IP ADDRESS OF HOST> in the classes directory

Clients may only connect to one host and may only communicate with other clients on that same host.

Once you are in the client program you may issue the following commnads

/adduser <user name> 
Adds a user name that can be logged into. Throws an error of a user or a group with that name already exists.

/group <group name> 
Adds a group with the given name that user can join. Throws an error of a user or a group with that name already exists.

/listusers <pattern default=*>
Lists all users on the server filtering user names by the pattern (which recognizes only wildcard charecters). The default if no pattern is given is to match all users.

/listgroups
Lists all groups on the server filtering group names by the pattern (which recognizes only wildcard charecters). The default if no pattern is given is to match all groups.

/login <user name> 
Log the client in under the given user name.

/leaveforever
If logged in under a username this deletes your user from the server forever.

/m <group or user name>
If logged in under a username this changes which user or group you are sending messages to.

/get
If logged in under a username this retrieves any new messages in your queue on the server

Once you are logged into under a username on the client and you have set who you are sending messages to using /m, simply entering
any text into standard in will automatically send messages from you to the other user or group.
