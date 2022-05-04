# asca
Antiscam Discord Bot

Asca moderates scammers and deletes scam messages

![Profile](https://cdn.discordapp.com/attachments/936463189237977139/955675143131267072/profile.png)

*Optionally configure via slash commands*

### Modes of Operation

Both modes of operation require `Manage Messages` to delete scam messages

- **Timeout Mode (Default):** Requires `Moderate Members` to **timeout** scammers
- **Ban Mode:** Requires `Ban Members` to **ban** scammers

[Add to Server](https://discord.com/api/oauth2/authorize?client_id=930922882886934588&permissions=1099511635972&scope=bot%20applications.commands)

<details>
<summary>Setup Your Own Instance</summary>

**Requires Python 3.10.x or later**

0. Create a Discord bot with
    * Scopes: `bot`, `applications.commands`
    * Permissions: `Manage Messages`, `Moderate Members`, `Ban Members`

1. Set `ASCA_DEVSERVER=𝗜𝗗` in env

2. Execute
```
% python -m pip install --requirement requirements.txt
% python bot.py
```

[Docker](https://hub.docker.com/r/dotbotio/asca)
</details>

<details>
<summary>Credits</summary>

* **Liz** (Lead Designer)
* **Mac** (Lead Tester)
* **Lauch** (Tester)
* **Sam** (Tester)
</details>
