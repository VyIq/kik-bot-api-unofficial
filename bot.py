#!/usr/bin/env python3
import logging
import sys

import kik_unofficial.datatypes.xmpp.chatting as chatting
from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback
from kik_unofficial.datatypes.xmpp.errors import SignUpError, LoginError
from kik_unofficial.datatypes.xmpp.roster import FetchRosterResponse, PeersInfoResponse
from kik_unofficial.datatypes.xmpp.sign_up import RegisterResponse, UsernameUniquenessResponse
from kik_unofficial.datatypes.xmpp.login import LoginResponse, ConnectionFailedResponse
from kik_unofficial.datatypes.xmpp.xiphias import UsersResponse, UsersByAliasResponse
import random
import time

listfr = ['a', 'b', 'c', 'd', 'e', 'f']
listfn = ['0', '1', '2', '3', '4', '5', '6', '7', '8']

x = ''.join(random.choice(listfn + listfr) for _ in range(32))
y = ''.join(random.choice(listfn + listfr) for _ in range(16))
device_id = x
android_id = y

username = sys.argv[1] if len(sys.argv) > 1 else input('Username: ')
password = sys.argv[2] if len(sys.argv) > 2 else input('Password: ')


def main():
    # set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(KikClient.log_format()))
    logger.addHandler(stream_handler)

    # create the bot
    bot = EchoBot()


class EchoBot(KikClientCallback):
    def __init__(self):
        self.client = KikClient(self, username, password, android_id_override=android_id, device_id_override=device_id)

    def on_authenticated(self):
        print("Now I'm Authenticated, let's request roster")
        self.client.request_roster()

    def on_login_ended(self, response: LoginResponse):
        print("Full name: {} {}".format(response.first_name, response.last_name))

    def read_ajids():
        ajid_list = open('ops.txt', 'r')
        lines = ajid_list.readlines()

        count = 0

        for line in lines:
            count += 1
            print("{}".format(line.strip()))
            time.sleep(0.3)

    def on_chat_message_received(self, chat_message: chatting.IncomingChatMessage):
        print("[+] '{}' says: {}".format(chat_message.from_jid, chat_message.body))

        if chat_message.body.lower() == "ping":
            self.client.send_chat_message(chat_message.from_jid, "Pong")

        elif chat_message.body.lower() == "help":
            self.client.send_chat_message(chat_message.from_jid, "This bot is owned by @RETROUX and programmed by @VyIq. \n\n Contact either for questions or concerns! <3")

        elif chat_message.from_jid == 'retroux_502@talk.kik.com' and chat_message.body.startswith("-op"):
            ajid = str(chat_message.body.replace("op ", ""))
            ajid_list = open('ops.txt', 'a')
            ajid_list.writelines(ajid + "\n")
            ajid_list.close()
            self.client.send_chat_message(chat_message.from_jid, "Opped " + ajid)

        else:
            self.client.send_chat_message(chat_message.from_jid, "Hello, say 'help' for contact info or 'ping' to check if the bot is online.")

    def on_group_message_received(self, chat_message: chatting.IncomingGroupChatMessage):
        if str(chat_message.raw_element).count("</alias-sender>") > 1 and "</alias-sender>" not in str(chat_message.body):
            return

        print("[+] '{}' from group ID {} says: {}".format(chat_message.from_jid, chat_message.group_jid, chat_message.body))

        if chat_message.from_jid == 'read_ajids' and chat_message.body.startswith("ban"):
            ajid = str(chat_message.body.replace("ban ", ""))
            self.client.ban_member_from_group(chat_message.group_jid, ajid)
 
        elif chat_message.from_jid == 'read_ajids' and chat_message.body.startswith("kick"):
            ajid = str(chat_message.body.replace("kick ", ""))
            self.client.remove_peer_from_group(chat_message.group_jid, ajid)

        elif chat_message.from_jid == 'read_ajids' and chat_message.body.startswith("promote"):
            ajid = str(chat_message.body.replace("promote ", ""))
            self.client.promote_to_admin(chat_message.group_jid, ajid)

        elif chat_message.from_jid == 'read_ajids' and chat_message.body.startswith("demote"):
            ajid = str(chat_message.body.replace("demote ", ""))
            self.client.demote_admin(chat_message.group_jid, ajid)

        elif chat_message.from_jid == 'read_ajids' and chat_message.body.startswith("add"):
            username = str(chat_message.body.replace("add ", ""))
            self.client.send_chat_message(chat_message.group_jid, "Attempting to add \"" + username + "\" to the group.")
            try:
                def get_jid(username):
                    try:
                        grab_jid = self.client.get_jid(username)
                        return grab_jid
                    except:
                        return False
                jid = get_jid(username)
                attempts = 1
                while jid == False:
                    if attempts > 5:
                        self.client.send_chat_message(chat_message.group_jid,
                                                      "I was unable to get the JID for \"" + username + "\"! Please try again.\n(Make sure the username is valid!)")
                        jid = ""
                    else:
                        jid = get_jid(username)
                        attempts = attempts + 1
                self.client.add_peer_to_group(chat_message.group_jid, jid)
                if jid:
                    self.client.send_chat_message(chat_message.group_jid, "Add attempt complete!")
            except:
                self.client.send_chat_message(chat_message.group_jid, "Add attempt failed!")

        elif chat_message.from_jid == 'read_ajids' and chat_message.body.startswith("status"):
             with open("ops.txt", "r") as f:
                self.client.send_chat_message(chat_message.group_jid, f.read())

        elif chat_message.body.lower() == "ping":
            self.client.send_chat_message(chat_message.group_jid, "Pong")

    def on_roster_received(self, response: FetchRosterResponse):
        print("[+] Chat partners:\n" + '\n'.join([str(member) for member in response.peers]))

    def on_friend_attribution(self, response: chatting.IncomingFriendAttribution):
        print("[+] Friend attribution request from " + response.referrer_jid)

    def on_peer_info_received(self, response: PeersInfoResponse):
        print("[+] Peer info: " + str(response.users))

    def on_status_message_received(self, response: chatting.IncomingStatusResponse):
        pass

    def on_username_uniqueness_received(self, response: UsernameUniquenessResponse):
        print("Is {} a unique username? {}".format(response.username, response.unique))

    def on_sign_up_ended(self, response: RegisterResponse):
        print("[+] Registered as " + response.kik_node)

    # Error handling

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("[-] Connection failed: " + response.message)

    def on_login_error(self, login_error: LoginError):
        if login_error.is_captcha():
            login_error.solve_captcha_wizard(self.client)

    def on_register_error(self, response: SignUpError):
        print("[-] Register error: {}".format(response.message))


if __name__ == '__main__':
    main()
