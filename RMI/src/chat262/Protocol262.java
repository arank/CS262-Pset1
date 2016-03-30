package chat262;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;
import java.util.Set;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * In designing our server we made the assumption that it would be the central
 * state store for the system, and that the clients would be able to fail
 * gracefully at any point without corrupting any assumptions made about the
 * system state. We kept all the server state in memory to avoid taking a
 * dependency on a database.
 *
 * The client is responsible for declaring who they are. No authentication
 * method was created for clients so there is nothing to stop users from logging
 * in as one another. The RMI security model is not very clear, and we are not
 * sure whether a malicious user who can connect to the server could eventually
 * read/write another user’s messages, even if we tried to implement
 * authentication.
 *
 * We implementing push messaging by sending a UnicastRemoteObject representing
 * the client to the server. When the server wants to send a message to a
 * client, it calls .recieve() on the remote object proxy it holds for that
 * particular client. We associate users with clients by having each user have a
 * single client. When the client logs in, it sets itself as it’s user’s client.
 * When a user receives a message, the server tries to send it to the
 * corresponding client. If that invocation fails or the user doesn’t have an
 * attached client, we assume the client has left, so we set the user’s client
 * to null and buffer the message until they log in from somewhere else. When a
 * client switches users, it unsets itself from being the old user's’ client
 * with a test-and-swap API call. This is so if another client has logged in as
 * the same user after us, when we log in as a different user we don’t kick the
 * later, unrelated, client off.
 *
 * We used RMI as a simple RPC mechanism. It was tempting to try to use RMI as a
 * higher level abstraction. We decided against this during implementation, as
 * it reduced complexity and uncertainty to only use RMI only to send back and
 * forth strings and collections of strings.
 *
 * For example, it would feel idiomatic for Java to send a message by calling
 * User.sendMessage(User to, String message) However, then the client would have
 * to hold RemoteObjects for the user sending and the user receiving the
 * message. If we received a message from that user and wanted to show their
 * name with that message, we’d have to make another remote call to the server
 * to get their name. Alternatively, we could serialize the users, including a
 * username and identifier. However then when we make a call on the server using
 * the User object we hold on the client, it would be a copy, so the server
 * would have to look up the appropriate server-side user object by identifier.
 * We would have to figure out how to serialize the user’s identifier, but not
 * include their undelivered messages. If the other user changed their name, (a
 * functionality we don’t currently support,) it would not be seen on the
 * client. We found it was simply easier to use usernames as identifiers.

 * @author Jared
 */
public interface Protocol262 extends Remote {
    public void createAccount(String name) throws IllegalArgumentException, RemoteException;
    public Set<String> listAccounts(String filter) throws RemoteException;
    public void createGroup(String name, Set<String> members) throws IllegalArgumentException, RemoteException;
    public Set<String> listGroups(String filter) throws RemoteException;
    public void sendMessage(String entityName, String from, String message_txt) throws IllegalArgumentException, RemoteException;
    public List<Message> fetchMessages(String name) throws IllegalArgumentException, RemoteException;
    public void deleteAccount(String name) throws IllegalArgumentException, RemoteException;

    public void setListener(String username, PushReciever reciever) throws RemoteException;
    public Boolean unsetListener(String username, PushReciever reciever) throws RemoteException;
}
