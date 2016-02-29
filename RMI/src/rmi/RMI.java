package rmi;

import java.util.*;
import java.util.HashSet;

// TODO [Tomas, 2-21-2016] : IDK how RMI works, will we need sync methods?

public class RMI {
    public static void main(String[] args) {
        // TODO [Tomas, 2-21-2016] : code application logic here
    }   
}

interface Protocol262 {
    public void createAccount(String name) throws IllegalArgumentException;
    public Set<String> listAccounts();
    public void createGroup(String name, Set<String> members) throws IllegalArgumentException;
    public Set<String> listGroups();
    public void sendMessage(String entityName, Boolean isGroup, String from, String message_txt) throws IllegalArgumentException;
    public Set<Message> fetchMessages(String name) throws IllegalArgumentException;
    public void deleteAccount(String name) throws IllegalArgumentException;
}

class Server262 implements Protocol262 {
    protected State s;
    
    public Server262() {
        s = new State();
    }
    
    @Override
    public void createAccount(String name) throws IllegalArgumentException {
        HashMap<String, User> users = s.getUsers();
        if (users.containsKey(name)) {
            throw new IllegalArgumentException("Username already exist");
        }
        
        users.put(name, new User(name));
    }
    
    @Override
    public Set listAccounts() {
        HashMap<String, User> users = s.getUsers();
        return users.keySet();
    }
    
    @Override
    public void createGroup(String name, Set<String> members) throws IllegalArgumentException {
        HashMap<String, Group> groups = s.getGroups();
        if (groups.containsKey(name)) {
            throw new IllegalArgumentException("Group already exist");
        }
        
        HashMap<String, User> users = s.getUsers();
        Group newGroup = new Group(name);
        for (String member:members) {
            User u = users.get(member);
            if (u == null) {
                newGroup.cleanUp();
                throw new IllegalArgumentException("User does not exist");
            }
            newGroup.addMember(u);
        }
        
        groups.put(name, newGroup);
    }
    
    @Override
    public Set<String> listGroups() {
        HashMap groups = s.getGroups();
        return groups.keySet();
    }
    
    @Override
    public void sendMessage(String to, Boolean isGroup, String from, String message_txt) throws IllegalArgumentException {
        HashMap<String, User> users = s.getUsers();
        User from_user = users.get(from);
        if (from_user == null) {
            throw new IllegalArgumentException("To Group does not exist");
        }
        
        if (isGroup) {
            HashMap<String, Group> groups = s.getGroups();
            Group g = groups.get(to);
            if (g == null) {
                throw new IllegalArgumentException("To Group does not exist");
            }
            
            Message m = new Message(from_user, message_txt, g);
            g.recieveMessage(m);
        } else {
            User u = users.get(to);
            if (u == null) {
                throw new IllegalArgumentException("To User does not exist");
            }
            
            Message m = new Message(from_user, message_txt, u);
            u.recieveMessage(m);
        }
    }
    
    @Override
    public Set<Message> fetchMessages(String name) throws IllegalArgumentException {
        HashMap<String, User> users = s.getUsers();
        if (!users.containsKey(name)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
        
        User u = users.get(name);
        // copy it so you can clear the set
        Set<Message> messages = u.getUndeliveredMessages();
        Set<Message> toReturn = new HashSet(messages);
        messages.clear();
        return toReturn;
    }
    
    @Override
    public void deleteAccount(String name) throws IllegalArgumentException {
        HashMap<String, User> users = s.getUsers();
        if (!users.containsKey(name)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
        
        users.remove(name);
    }
}

class Message {
    protected User from;
    protected String msg;
    protected Entity to;
    
    public Message(User from, String msg, Entity to) {
        this.from = from;
        this.msg = msg;
        this.to = to;
    }
}

interface Entity {}

class User implements Entity {
    protected String username;
    protected Set<Group> groups;
    protected Set<Message> undeliveredMessages;
    
    public User(String name) {
        username = name;
        groups = new HashSet();
        undeliveredMessages = new HashSet(); 
    }
    
    // NOTE: DO NOT CALL, only Group should call
    public void addGroup(Group g) {
        groups.add(g);
    }
    
    // NOTE: DO NOT CALL, only Group should call
    public void removeGroup(Group g) {
        groups.remove(g);
    }
    
    public Set<Message> getUndeliveredMessages() {
        return undeliveredMessages;
    }
    
    public void recieveMessage(Message m) {
        undeliveredMessages.add(m);
    }
}

class Group implements Entity {
    protected String groupname;
    protected Set<User> members;
    
    public Group(String name) {
        groupname = name;
        members = new HashSet();
    }
    
    public void addMember(User u) {
        u.addGroup(this);
        members.add(u);
    }
    
    public void removeMember(User u) {
        u.removeGroup(this);
        members.remove(u);
    }
    
    public void cleanUp() {
        for (User u : members) {
            removeMember(u);
        }
    }
    
    public void recieveMessage(Message m) {
        for (User u:members) {
            u.recieveMessage(m);
        }
    }
}

class State {
    protected HashMap<String, User> users;
    protected HashMap<String, Group> groups;
    
    public State() {
        users = new HashMap();
        groups = new HashMap();
    }
    
    public HashMap getUsers() {
        return users;
    }
    
    public HashMap getGroups() {
        return groups;
    }
}
