/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package chat262;

import java.io.Serializable;

/**
 *
 * @author Jared
 */
public class Message implements Serializable {
    public static final long serialVersionUID = 1L;

    protected String from;
    protected String to;
    protected String msg;
    
    public Message(String from, String msg, String to) {
        this.from = from;
        this.msg = msg;
        this.to = to;
    }
}
