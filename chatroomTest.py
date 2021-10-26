import asyncio
from typing import Optional, Any

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100


def define_actions(b_f):
    if not b_f:
        return actions(name="cmd", buttons=["Send", {'label': "Exit", 'type': 'cancel'}])
    else:
        return actions(name="cmd", buttons=["Send", "Admin's tools", {'label': "Exit", 'type': 'cancel'}])


async def main():
    global chat_msgs
    lst = chat_msgs
    put_html("""
                <div class="dropdown-content">
                    <button>Kick User</button>
                    <button>Ban User</button>
                </div>
                <style type="text/css">
                    .dropdown-content {
                        display: none;
                        position: relative;
                        background-color: #f9f9f9;
                        width: 125.15px;
                        height: 38px;
                        bottom: 8px;
                        box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
                    }
                    div div div div div form div div button[value="Admin's tools"] {
                        .dropdown-content {
                            display: inline-block;
                        }
                    }
                </style>""")
    put_html("""<style type="text/css">
       body, #input-container{ 
        background: black;
       }
       .card {
        background: #2F4F4F;
        color: #00FFFF;
       }
       .form-control {
        transition: box-shadow 0.3s;
       }
       .ws-form-submit-btns {
        position: relative;
        top: 10px;
        padding-bottom: 8px;
       }
       .form-control:hover {
        box-shadow: 0 8px 12px 0 red, 0 6px 10px 0 red;
       }
       .invalid-feedback {
       color: yellow;
       font-size: 14px;
       
       }
      </style>""")
    put_markdown("## ✉ Welcome to ChatBox 1.0!").style("color:#00FFFF;")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True).style("background:#2F4F4F; color: wheat;")
    isin = lambda nick: "This nickname already used!" if nick in online_users or nick == '📢' else None
    iscorrect = lambda psd: "Incorrect password!" if psd != "neonkey1991" else None
    isadmin = False
    nickname = await input("Enter to chat", required=True, placeholder="Your name",
                           validate=isin)
    if len(nickname) > 6 and nickname[:6] == "ADMIN:":
        await input("Insert admin's password, please", required=True, placeholder="Password",
                    validate=iscorrect, type="password")
        isadmin = True
    online_users.add(nickname)

    put_html("""<style type="text/css">
       strong:first-child { 
        color: cornflowerblue;
       }
       .markdown-body code {
        border-radius: 4px;
        background-color: #FFFACD;
        color:black;
        font-weight: bold;
       }
       .markdown-body a {
        text-decoration: none;
        color: #F5F5DC;
       }
       a:hover {
        transition: font-size 0.5s;
        text-decoration: underline;
        font-size: 105%;
        color: #7FFF00;
        
       }
      </style>""")

    lst.append(('📢', f'**{nickname}** joined to chatbox!'))
    msg_box.append(put_markdown(f'📢 **{nickname}** joined to chatbox!').style("color: gold;"))

    while True:
        data = await input_group("💭 New message", [
            input(placeholder="Text of message ...", name="msg"),
            define_actions(isadmin),
        ], validate=lambda d: ("msg", "Empty message cannot be sended!") if not len(d["msg"]) and d[
            "cmd"] == "Send" else None)
        if data is None:
            break
        if data["cmd"] == "Send":
            msg_box.append(put_markdown(f"**{nickname}**: {data['msg']}"))
            lst.append((nickname, data['msg']))
        elif data["cmd"] == "Admin's tools":
            pass

    refresh_task = run_async(refresh(nickname, msg_box))

    refresh_task.close()

    online_users.remove(nickname)
    toast("You quited from chatbox!")
    msg_box.append(put_markdown(f'📢 User **{nickname}** quited the chat!').style("color: gold;"))
    lst.append(('📢', f'User **{nickname}** quited the chat!'))

    put_buttons(['Return to chatbox'], onclick=lambda btn: run_js('window.location.reload()'))


async def refresh(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:  # if not a message from current user
                msg_box.append(put_markdown(f"**{m[0]}**: {m[1]}"))

        # remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


if __name__ == "__main__":
    start_server(main, cdn=False, debug=True, port=9999, auto_open_webbrowser=True)
