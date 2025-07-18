import customtkinter as ctk
import tkinter.messagebox as msg
from tkinter.colorchooser import askcolor
import requests, pyperclip, json, datetime, os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class Dimbed(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dimbed — Discord Embed Creator")
        self.geometry("570x770")

        self.color = "#3498db"

        tabs = ctk.CTkTabview(self)
        tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.webhook_tab = tabs.add("Webhook")
        self.bot_tab = tabs.add("Bot")
        self.clip_tab = tabs.add("Clipboard")

        self.build_webhook_tab()
        self.build_bot_tab()
        self.build_clip_tab()

    def build_embed_fields(self, tab):
        title = ctk.CTkEntry(tab, placeholder_text="Embed Title")
        title.pack(pady=5)

        desc = ctk.CTkTextbox(tab, height=120)
        desc.insert("0.0", "Embed Description")
        desc.pack(pady=5)

        color_btn = ctk.CTkButton(tab, text="Choose Color", command=self.choose_color)
        color_btn.pack(pady=5)

        ping = ctk.CTkEntry(tab, placeholder_text="Ping Role (Optional)")
        ping.pack(pady=5)

        return title, desc, ping

    def choose_color(self):
        _, hexval = askcolor(title="Pick Embed Color")
        if hexval:
            self.color = hexval

    def get_embed_dict(self, title, desc):
        return {
            "title": title.get(),
            "description": desc.get("0.0", "end").strip(),
            "color": int(self.color.replace("#", ""), 16)
        }

    def build_webhook_tab(self):
        self.wh_title, self.wh_desc, self.wh_ping = self.build_embed_fields(self.webhook_tab)
        self.wh_url = ctk.CTkEntry(self.webhook_tab, placeholder_text="Webhook URL")
        self.wh_url.pack(pady=5)

        ctk.CTkButton(self.webhook_tab, text="Send Embed", command=self.send_webhook).pack(pady=10)
        ctk.CTkButton(self.webhook_tab, text="Export Script", command=self.export_webhook_script).pack(pady=5)

    def send_webhook(self):
        embed = {"embeds": [self.get_embed_dict(self.wh_title, self.wh_desc)]}
        ping = self.wh_ping.get().strip()
        if ping:
            if ping.startswith("@"):
                embed["content"] = ping
            elif ping.isdigit():
                embed["content"] = f"<@&{ping}>"
        try:
            res = requests.post(self.wh_url.get(), json=embed)
            msg.showinfo("Webhook", "Sent!" if res.status_code == 204 else f"Error: {res.status_code}")
        except Exception as e:
            msg.showerror("Exception", str(e))

    def export_webhook_script(self):
        embed = self.get_embed_dict(self.wh_title, self.wh_desc)
        ping = self.wh_ping.get().strip()
        content = f'"{ping}"' if ping.startswith("@") else f'"<@&{ping}>"' if ping.isdigit() else '""'

        filename = f"webhook_embed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        code = f"""import requests

url = "{self.wh_url.get()}"
embed = {{
    "content": {content},
    "embeds": [{json.dumps(embed, indent=4)}]
}}

res = requests.post(url, json=embed)
print("Sent!" if res.status_code == 204 else f"Error: {{res.status_code}}")
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        pyperclip.copy(json.dumps(embed, indent=4))
        msg.showinfo("Exported", f"Script saved as {filename} and embed copied to clipboard.")

    def build_bot_tab(self):
        self.bot_title, self.bot_desc, self.bot_ping = self.build_embed_fields(self.bot_tab)
        self.bot_token = ctk.CTkEntry(self.bot_tab, placeholder_text="Bot Token")
        self.bot_token.pack(pady=5)
        self.bot_channel = ctk.CTkEntry(self.bot_tab, placeholder_text="Channel ID")
        self.bot_channel.pack(pady=5)
        self.bot_command = ctk.CTkEntry(self.bot_tab, placeholder_text="Command Trigger (e.g. !embed)")
        self.bot_command.pack(pady=5)

        ctk.CTkButton(self.bot_tab, text="Send via Token", command=self.send_token).pack(pady=10)
        ctk.CTkButton(self.bot_tab, text="Export Script", command=self.export_token_script).pack(pady=5)

    def send_token(self):
        embed = self.get_embed_dict(self.bot_title, self.bot_desc)
        ping = self.bot_ping.get().strip()
        command = self.bot_command.get().strip()
        content = ""

        if ping:
            content += f"<@&{ping}>" if ping.isdigit() else ping
        if command:
            content += f" {command}"

        headers = {"Authorization": f"Bot {self.bot_token.get()}"}
        data = {"content": content, "embeds": [embed]}

        try:
            res = requests.post(
                f"https://discord.com/api/v10/channels/{self.bot_channel.get()}/messages",
                headers=headers, json=data
            )
            msg.showinfo("Bot", "Sent!" if res.status_code == 200 else f"Error: {res.status_code}")
        except Exception as e:
            msg.showerror("Exception", str(e))

    def export_token_script(self):
        embed = self.get_embed_dict(self.bot_title, self.bot_desc)
        ping = self.bot_ping.get().strip()
        command = self.bot_command.get().strip()
        content = ""

        if ping:
            content += f"<@&{ping}>" if ping.isdigit() else ping
        if command:
            content += f" {command}"

        filename = f"bot_embed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        code = f"""import requests

token = "{self.bot_token.get()}"
channel_id = "{self.bot_channel.get()}"
headers = {{
    "Authorization": f"Bot {{token}}"
}}

embed = {json.dumps(embed, indent=4)}
payload = {{
    "content": "{content}",
    "embeds": [embed]
}}

res = requests.post(f"https://discord.com/api/v10/channels/{{channel_id}}/messages", headers=headers, json=payload)
print("Sent!" if res.status_code == 200 else f"Error: {{res.status_code}}")
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        pyperclip.copy(json.dumps(embed, indent=4))
        msg.showinfo("Exported", f"Script saved as {filename} and embed copied to clipboard.")

    def build_clip_tab(self):
        title = ctk.CTkEntry(self.clip_tab, placeholder_text="Embed Title")
        title.pack(pady=5)
        desc = ctk.CTkTextbox(self.clip_tab, height=120)
        desc.insert("0.0", "Embed Description")
        desc.pack(pady=5)

        ctk.CTkButton(self.clip_tab, text="Choose Color", command=self.choose_color).pack(pady=5)

        def copy_embed():
            embed = {
                "title": title.get(),
                "description": desc.get("0.0", "end").strip(),
                "color": int(self.color.replace("#", ""), 16)
            }
            pyperclip.copy(json.dumps(embed, indent=4))
            msg.showinfo("Clipboard", "Embed dictionary copied!")

        ctk.CTkButton(self.clip_tab, text="Copy Embed to Clipboard", command=copy_embed).pack(pady=10)

if __name__ == "__main__":
    Dimbed().mainloop()
