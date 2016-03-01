To run this project you must first complile the class files by running javac -d classes/ -Xlint:unchecked src/chat262/*.java in the RMI
directory.

You must then start up the registry process by running $(cd classes/; rmiregistry)

Once that is set up you can choose to run either the server process by running java chat262.Server262 in the classes directrory
or the client process by running java chat262.ChatClient <IP ADDRESS OF HOST> in the classes directory

Clients may only connect to one host and may only communicate with other clients on that same host.
