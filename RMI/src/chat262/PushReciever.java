/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package chat262;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

/**
 * PushReciever is our generalized interface for pushing batches of messages
 * from chat "server" to chat "client".  It is intended to be the interface to
 * a stub of a remote RMI server living on a chat "client", with the .recieve()
 * method invoked by the chat "server" which would here be the RMI client.
 */
public interface PushReciever extends Remote {
    public void recieve(List<Message> msgs) throws RemoteException;
}
