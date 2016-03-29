package chat262;

import java.rmi.RemoteException;
import java.util.*;
import java.util.HashSet;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

/**  
*
* @author Jared
* @author Aran
* @version 1.0z Mar 28 2016
*/
public class Server262 implements Protocol262 {
    // The map of all users currently registered with the server
	private final HashMap<String, User> users;
	
	// The map of all groups currently registered with the server
    private final HashMap<String, Group> groups;
    
	/** 
	 * Initialization Method to Create data Maps associated with the server object
	 */
    public Server262() {
        users = new HashMap<>();
        groups = new HashMap<>();
    }
    
	/**
	 * Main method to create a server and protocol object 
	 * setting up the remote registry for RMI and establishin  a connection to it.
	 * This throws no exceptions if it fails though it will print to std err.
	 * @param args		command lines arguments are unused in this implementation 
	 */
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
    
	/** 
	 * creates an account by creating a new user object registering it in the user map 
	 * @param name		username to assign the new user
	 * @throws 			Illegal arguement exception if the username is already in the map
	 */
    @Override
    public synchronized void createAccount(String name) throws IllegalArgumentException {
        // Check if user already exists
    	if (users.containsKey(name) || groups.containsKey(name)) {
            throw new IllegalArgumentException("Username already exist");
        }
        
        users.put(name, new User(name));
        System.out.println("created user " + name);
    }
    
	/** 
	 * Lists all accounts (usernames) that match the given filter string 
	 * (matching on all strings if a null filter is given) 
	 * @param filter	the filter string to match accounts against (supporting wild card * which matches all substrings of charecters) if a null value is given it defaults to *
	 * @returns 		a Set of the username strings that match the given pattern
	 */
    @Override
    public Set<String> listAccounts(String filter) {
    	HashSet<String> all_users = new HashSet<>(users.keySet());
    	if (filter == null || filter.length() == 0) {
    		filter = "*";
    	}
    	
    	// Filter all elements in the map using the regex (based on the filter)
    	String regex = ("\\Q" + filter + "\\E").replace("*", "\\E.*\\Q");
    	for (Iterator<String> i = all_users.iterator(); i.hasNext();) {
    	    String element = i.next();
	        if (!element.matches(regex)){
	        	i.remove();
	        }
    	}
        return all_users;
    }
    
	/** 
	 * creates an group by creating a new group object registering it in the group map and adding all members
	 * @param name		group name to assign the new group
	 * @param memebers  a set of username strings to add to this new group		
	 * @throws 			Illegal arguement exception if the group name is already in the map
	 * @throws 			Illegal arguement exception if a username in the member set does not exist
	 */
    @Override
    public synchronized void createGroup(String name, Set<String> members) throws IllegalArgumentException {
        // Check if groupname already exists
    	if (users.containsKey(name) || groups.containsKey(name)) {
            throw new IllegalArgumentException("Group already exist");
        }
        
        // Create new group
        Group newGroup = new Group(name);
        
        // For each member in the set check if they exist and if so add them to the group
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
    
	/** 
	 * Lists all groups (groupnames) that match the given filter string 
	 * (matching on all strings if a null filter is given) 
	 * @param filter	the filter string to match groups against (supporting wild card * which matches all substrings of charecters) if a null value is given it defaults to *
	 * @returns 		a Set of the groupname strings that match the given pattern
	 */
    @Override
    public Set<String> listGroups(String filter) {
    	HashSet<String> all_groups = new HashSet<>(groups.keySet());
    	if (filter == null || filter.length() == 0) {
    		filter = "*";
    	}
    	
    	// Filter all elements in the map using the regex (based on the filter)
        String regex = ("\\Q" + filter + "\\E").replace("*", "\\E.*\\Q");
    	for (Iterator<String> i = all_groups.iterator(); i.hasNext();) {
    	    String element = i.next();
	        if (!element.matches(regex)){
	        	i.remove();
	        }
    	}
        return all_groups;
    }
    
	/** 
	 * sends a message from one user to another user or a registered group of users
	 * @param from		user name of the user sending the message
	 * @param to  		user name of group name of the recipient of the message
	 * @param message_txt	the text string of the message being sent	
	 * @throws 			Illegal arguement exception if the group or user name being set to doesn't exist
	 * @throws 			Illegal arguement exception if a username sending the message doesn't exist
	 */
    @Override
    public synchronized void sendMessage(String to, String from, String message_txt) throws IllegalArgumentException {
        // Create a new message object to place on user object queue or the group object queue
    	Message m = new Message(from, message_txt, to);

    	// Check valid from user
        User from_user = users.get(from);
        if (from_user == null) {
            throw new IllegalArgumentException("To Group does not exist");
        }
        
        // Check if valid group or user being sent to
        Reciever r = groups.get(to);
        if (r == null) {
            r = users.get(to);
        }
        if (r == null) {
            throw new IllegalArgumentException("Message reciever does not exist");
        }
        
        // Send message to user or group
        r.recieveMessage(m);
    }
    
	/** 
	 * Retrives the undelivered queue of messages for a specified user (clearing the exsiting queue from the server)
	 * @param name		user name of the user to get undelivered message queue contents for
	 * @throws 			Illegal arguement exception if the user name does not exist
	 * @return 			A list of undelivered messages for the user name (which is empty if there are no new messages for that user)
	 */
    @Override
    public synchronized List<Message> fetchMessages(String name) throws IllegalArgumentException {
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
    
	/** 
	 * Deletes a given user from the system via their username
	 * @param name		user name of the user to delete
	 * @throws 			Illegal arguement exception if the user name does not exist
	 */
    @Override
    public synchronized void deleteAccount(String name) throws IllegalArgumentException {
        // check if user exists
    	if (!users.containsKey(name)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
        
        // Get user and delete it from all the groups
        User user_obj = users.get(name);
        for (Group g : groups.values()) {
            if (g.members.contains(user_obj)){
            	g.members.remove(user_obj);
            }
        }
        
        users.remove(name);
    }

	/** 
	 * Effectively logs a user in by setting their client to the connection to push messages to the client
	 * @param username	user name of the user who is logging in to receive messages
	 * @param reciever  the reciver object to push new messages to
	 * @throws 			Illegal arguement exception if a username does not exist
	 */
    @Override
    public synchronized void setListener(String username, PushReciever reciever) throws RemoteException {
    	// check if user exists
        if (!users.containsKey(username)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
        
        // Set the users reciever to that given by the client
        User user = users.get(username);
        user.client = reciever;
        user.deliverMessages();
    }

	/** 
	 * Effectively logs a user out by setting their client to the connection to null
	 * @param username	user name of the user who is logging out
	 * @param reciever  the reciver object for the client (to verify that this is indeed the correct person to logout)
	 * @throws 			Illegal arguement exception if a username does not exist
	 */
    @Override
    public synchronized Boolean unsetListener(String username, PushReciever reciever) throws RemoteException {
        // check if user exists
    	if (!users.containsKey(username)) {
            throw new IllegalArgumentException("Username doesn't exist");
        }
    	
    	// uncouple user from the reciever if the pointers match
        User user = users.get(username);
        if (user.client.equals(reciever)) {
            user.client = null;
            return true;
        } else {
            // mostly for debugging
            return false;
        }
    }
}

/** 
 * Interface for an object that dynamically recieves messages from a remote client
 */
interface Reciever {
    String getName();
    void recieveMessage(Message m);
}

/** 
 * The user object that can be logged in, added to groups, receive messages, and store undelivered message
 */
class User implements Reciever {
    protected String username;
    
    // groups user is in
    protected Set<Group> groups;
    
    // messages that haven't been delivered to client yet
    protected ArrayList<Message> undeliveredMessages;
    
    // The reciever for the logged in client to dyanamically push messages to
    public PushReciever client;
    
	/** 
	 * Constructor to set the username and set up the group and message queues
	 * @param username	user name to set
	 */
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
    
	/** 
	 * Returns all the undelivered messages for the current user object
	 * @returns		the list of undelivered message objects in the queue
	 */
    public List<Message> getUndeliveredMessages() {
        return undeliveredMessages;
    }
    
	/** 
	 * Adds a new message to the users undelivered crew and delivers it instantly if the user client is set
	 * @param m		message to add queue or deliver if the user is logged in
	 */
    @Override
    public void recieveMessage(Message m) {
        undeliveredMessages.add(m);
        deliverMessages();
    }
    
	/** 
	 * If the user is logged in (i.e. client is set) deliver messages instantly to the reciver
	 */
    public void deliverMessages() {
        try {
        client.recieve(undeliveredMessages);
        undeliveredMessages.clear();
            
        } catch (Exception e) {
            // client went away; remove client
            client = null;
        }
    }
    
	/** 
	 * Getter for username of user
	 * @returns		the username of the user object
	 */
    @Override
    public String getName() {
        return username;
    }
}

/** 
 * A group object that has member list of users, and can receive messages
 */
class Group implements Reciever {
    public String groupname;
    
    // Users in this group
    public Set<User> members;
    
	/** 
	 * Constructor for the group and setting up the member set
	 * @param name		the name of the group
	 */
    public Group(String name) {
        groupname = name;
        members = new HashSet<>();
    }
    
	/** 
	 * Adds a member to the group and adds this group the users grouplist
	 * @param u		the user to add to this group
	 */
    public void addMember(User u) {
        u.addGroup(this);
        members.add(u);
    }
    
	/** 
	 * Removes a member from the group and removes the group from the users grouplist
	 * @param u		user object to remove from the group
	 */
    public void removeMember(User u) {
    	// remove this group from the user
        u.removeGroup(this);
        members.remove(u);
    }
    
	/** 
	 * Removes all users from the group
	 */
    public void cleanUp() {
        for (User u : members) {
            removeMember(u);
        }
    }
    
	/** 
	 * Sends a message object to all indavidual users in the group
	 * @param m		messages to send to group members
	 */
    @Override
    public void recieveMessage(Message m) {
        for (User u:members) {
            u.recieveMessage(m);
        }
    }
    
	/** 
	 * Getter for groupname
	 * @return		the name of the group
	 */
    @Override
    public String getName() {
        return groupname;
    }
}
