# asca
Antiscam Discord Bot

Asca moderates scammers and deletes scam messages

![Profile](https://cdn.discordapp.com/attachments/936463189237977139/937015273553289327/profile.png)

*Optionally configure via slash commands*

[Add to Server](https://discord.com/api/oauth2/authorize?client_id=930922882886934588&permissions=1099511635972&scope=bot%20applications.commands)

Note that the `Ban Members` permission is optional, if you are happy with the default of Timeout mode.

<details>
<summary>Setup Your Own Instance</summary>

**Requires Python 3.10.x or later**

0. Create a Discord bot with
    * Scopes: `bot`, `applications.commands`
    * Permissions: `Manage Messages`, `Moderate Members`, `Ban Members`

1. Execute
```
% python3 -m pip install --requirement requirements.txt
% python3 bot.py
```

[Docker](https://hub.docker.com/r/dotbotio/asca)
</details>

<details>
<summary>Credits</summary>

**Liz** (Lead Designer)
**Mас** (Lead Tester)
**Lauch** (Tester)
</details>
