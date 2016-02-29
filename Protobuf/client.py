import cmd

class ChatClient(cmd.Cmd):
    def do_createUser(self, username):


    def do_listAccounts(self):


    def do_createGroup(self, groupname, membersStr):


    def do_listGroups(self):


    def do_sendGroupMessage(self, fromUser, toGroup, message):


    def do_sendUserMessage(self, fromUser, toUser, message):


    def do_fetchMessages(self, username):


    def do_deleteAccount(self, username):


    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    ChatClient().cmdloop()
