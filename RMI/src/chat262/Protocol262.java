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
 *
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
