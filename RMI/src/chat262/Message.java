/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package chat262;

import java.io.Serializable;

/**
 * Tuple passed around identifying a message, it's contents, sender, and intended recipient
 * @author Jared
 */
public class Message implements Serializable {
    public static final long serialVersionUID = 1L;

    /**
     * from is the username string of the message sender
     */
    protected String from;

    /**
     * to is the username|groupname string of the message recipient.
     * The message may be delivered to someone not named in the .to field
     * if they are a member of a group named in the .to field, or a member of a
     * group that is a member of a group named in the .to field, recursively.
     * Usernames and groupnames share a namespace, so this name is unambiguous.
     */
    protected String to;
    
    /**
     * the message text contents
     */
    protected String msg;
    
    /**
     * Message tuple constructor
     * @param from      assigned to the .from member
     * @param msg       assigned to the .msg member
     * @param to        assigned to the .to member
     */
    public Message(String from, String msg, String to) {
        this.from = from;
        this.msg = msg;
        this.to = to;
    }
}
