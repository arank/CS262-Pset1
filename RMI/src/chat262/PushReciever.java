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
 *
 * @author Jared
 */
public interface PushReciever extends Remote {
    public void recieve(List<Message> msgs) throws RemoteException;
}
