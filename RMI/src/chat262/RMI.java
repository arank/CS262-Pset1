package chat262;

import java.util.*;
import java.util.HashSet;
import java.rmi.*;

// TODO [Tomas, 2-21-2016] : IDK how RMI works, will we need sync methods?


interface Protocol262 extends Remote {
    public void createAccount(String name) throws IllegalArgumentException, RemoteException;
    public Set<String> listAccounts() throws RemoteException;
    public void createGroup(String name, Set<String> members) throws IllegalArgumentException, RemoteException;
    public Set<String> listGroups() throws RemoteException;
    public void sendMessage(String entityName, Boolean isGroup, String from, String message_txt) throws IllegalArgumentException, RemoteException;
    public List<Message> fetchMessages(String name) throws IllegalArgumentException, RemoteException;
    public void deleteAccount(String name) throws IllegalArgumentException, RemoteException;
}

class Server262 implements Protocol262 {
    private final HashMap<String, User> users;
    private final HashMap<String, Group> groups;
    
    public Server262() {
        users = new HashMap();
        groups = new HashMap();
    }
    
    @Override
    public void createAccount(String name) throws IllegalArgumentException {
        if (users.containsKey(name)) {
            throw new IllegalArgumentException("Username already exist");
        }
        
        users.put(name, new User(name));
    }
    
    @Override
    public Set<String> listAccounts() {
        return users.keySet();
    }
    
    @Override
    public void createGroup(String name, Set<String> members) throws IllegalArgumentException {
        if (groups.containsKey(name)) {
            throw new IllegalArgumentException("Group already exist");
        }
        
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
        return groups.keySet();
    }
    
    @Override
    public void sendMessage(String to, Boolean isGroup, String from, String message_txt) throws IllegalArgumentException {
        User from_user = users.get(from);
        if (from_user == null) {
            throw new IllegalArgumentException("To Group does not exist");
        }
        
        if (isGroup) {
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
    public List<Message> fetchMessages(String name) throws IllegalArgumentException {
        if (!users.containsKey(name)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
        
        User u = users.get(name);
        // copy it so you can clear the set
        List<Message> messages = u.getUndeliveredMessages();
        ArrayList<Message> toReturn = new ArrayList(messages);
        messages.clear();
        return toReturn;
    }
    
    @Override
    public void deleteAccount(String name) throws IllegalArgumentException {
        if (!users.containsKey(name)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
        
        users.remove(name);
        // TODO: remove user from all groups
    }
}

class Message {
    protected User from;
    protected String msg;
    protected Reciever to;
    
    public Message(User from, String msg, Reciever to) {
        this.from = from;
        this.msg = msg;
        this.to = to;
    }
}

interface Reciever {
    String getName();
    void recieveMessage(Message m);
}

class User implements Reciever {
    protected String username;
    protected Set<Group> groups;
    protected ArrayList<Message> undeliveredMessages;
    
    public User(String name) {
        username = name;
        groups = new HashSet();
        undeliveredMessages = new ArrayList(); 
    }
    
    // NOTE: DO NOT CALL, only Group should call
    public void addGroup(Group g) {
        groups.add(g);
    }
    
    // NOTE: DO NOT CALL, only Group should call
    public void removeGroup(Group g) {
        groups.remove(g);
    }
    
    public List<Message> getUndeliveredMessages() {
        return undeliveredMessages;
    }
    
    public void recieveMessage(Message m) {
        undeliveredMessages.add(m);
    }
    
    public String getName() {
        return username;
    }
}

class Group implements Reciever {
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
    
    @Override
    public void recieveMessage(Message m) {
        for (User u:members) {
            u.recieveMessage(m);
        }
    }

    @Override
    public String getName() {
        return groupname;
    }
}
