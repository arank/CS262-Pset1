package chat262;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Scanner;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author Jared
 */

public class ChatClient {
    public static void main(String[] args) throws Exception {
	String host = (args.length < 1) ? null : args[0];
        Protocol262 server = getServer(host);
        System.out.println("connected to server");
        
        String currentUser = null;
        String currentRoom = null;
        
        Scanner input = new Scanner(System.in);        
        while (input.hasNext()) {
            // get a line of input
            String line = input.nextLine();
            if (line.startsWith("/")) {
                try {
                    String[] command = line.split(" ");
                    switch (command[0]) {
                        case "/adduser":
                            server.createAccount(command[1]);
                            break;

                        case "/group":
                            List<String> members = Arrays.asList(Arrays.copyOfRange(command, 2, command.length));
                            server.createGroup(command[1], new HashSet<>(members));
                            break;

                        case "/listusers": {
                            String filter = command.length > 1 ? command[1] : null;
                            for (String name : server.listAccounts(filter)) {
                                System.out.println("> " + name);
                            }
                            break;
                        }

                        case "/listgroups": {
                            String filter = command.length > 1 ? command[1] : null;
                            for (String name : server.listGroups(filter)) {
                                System.out.println("> " + name);
                            }
                            break;
                        }

                        case "/login": {
                            String user = command[1];
                            try {
                                server.createAccount(user);
                            } catch (IllegalArgumentException e) {
                                // user already exists
                            }                        
                            currentUser = user;
                            break;
                        }

                        case "/leaveforever":
                            if (currentUser != null) {
                                server.deleteAccount(currentUser);
                                currentUser = null;
                            }
                            break;
                          
                        case "/m":
                            currentRoom = command[1];
                            break;

                        case "/get":
                            for (Message m : server.fetchMessages(currentUser)) {
                                String from = m.from;
                                if (!m.to.equals(currentUser)) {
                                    from += " to " + m.to;
                                }
                                System.out.println(from + ": " + m.msg);
                            }
                            break;
                        
                        default:
                            throw new IllegalArgumentException("bad command");
                    }
                } catch (Exception e) {
                    System.err.println("> Bad Command");
                }
            } else {
                if (currentUser != null && currentRoom != null) {
                    server.sendMessage(currentRoom, currentUser, line);
                }
            }
        }        
    }
    
    static Protocol262 getServer(String host) throws Exception {
        Registry registry = LocateRegistry.getRegistry(host);
        Protocol262 stub = (Protocol262) registry.lookup("chat262");
        return stub;
    }
}