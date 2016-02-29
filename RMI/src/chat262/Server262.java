package chat262;

import java.util.*;
import java.util.HashSet;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;


public class Server262 implements Protocol262 {
    private final HashMap<String, User> users;
    private final HashMap<String, Group> groups;
    
    public Server262() {
        users = new HashMap<>();
        groups = new HashMap<>();
    }
    
    public static void main(String[] args) {
	try {
	    Server262 obj = new Server262();
	    Protocol262 stub = (Protocol262) UnicastRemoteObject.exportObject(obj, 0);

	    // Bind the remote object's stub in the registry
	    Registry registry = LocateRegistry.getRegistry();
	    registry.bind("chat262", stub);

	    System.out.println("Server ready");
	} catch (Exception e) {
	    System.err.println("Server exception: " + e.toString());
	    e.printStackTrace();
	}
    }
    
    @Override
    public void createAccount(String name) throws IllegalArgumentException {
        if (users.containsKey(name)) {
            throw new IllegalArgumentException("Username already exist");
        }
        
        users.put(name, new User(name));
        System.out.println("created user " + name);
    }
    
    @Override
    public Set<String> listAccounts(String filter) {
        // TODO filtering?
        return new HashSet<>(users.keySet());
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
    public Set<String> listGroups(String filter) {
        // TODO filtering?
        return new HashSet<>(groups.keySet());
    }
    
    @Override
    public void sendMessage(String to, String from, String message_txt) throws IllegalArgumentException {
        Message m = new Message(from, message_txt, to);

        User from_user = users.get(from);
        if (from_user == null) {
            throw new IllegalArgumentException("To Group does not exist");
        }
        
        Reciever r = groups.get(to);
        if (r == null) {
            r = users.get(to);
        }
        if (r == null) {
            throw new IllegalArgumentException("Message reciever does not exist");
        }
            
        r.recieveMessage(m);
    }
    
    @Override
    public List<Message> fetchMessages(String name) throws IllegalArgumentException {
        if (!users.containsKey(name)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
        
        User u = users.get(name);
        // copy it so you can clear the set
        List<Message> messages = u.getUndeliveredMessages();
        ArrayList<Message> toReturn = new ArrayList<>(messages);
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
        groups = new HashSet<>();
        undeliveredMessages = new ArrayList<>(); 
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
    
    @Override
    public void recieveMessage(Message m) {
        undeliveredMessages.add(m);
    }
    
    @Override
    public String getName() {
        return username;
    }
}

class Group implements Reciever {
    protected String groupname;
    protected Set<User> members;
    
    public Group(String name) {
        groupname = name;
        members = new HashSet<>();
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
