<p><h1>mastodon-epic-gemini-bot, aka clod</h1>
<img src="https://4get.authenyo.xyz/proxy?i=https%3A%2F%2Fmedia.tenor.com%2FlJa1KnY6quwAAAAM%2Fnettspend-drankdrankdrank.gif"></p>
<img src="https://files.catbox.moe/ut9vn3.jpg">

Python Mastodon AI chatbot that uses the Gemini API that's really bad and I made with ChatGPT. It sucks but it's really funny. Used for the best AI assistant ever, [clod](https://brain.worm.pink/clod).

# how can i do it help help me wahh im criyn help

you technically need to run 2 scripts at the same time, main.py and danbooru.py for the yaoi mode. dont ask why. i should make it a toggle or put them in the same script probably idk im too fucking lazy

## Installation

1. Install required dependencies:
```
pip install -r requirements.txt
```

2. Copy the `.env-example` file to `.env` and edit it with your settings:
```
cp .env-example .env
```

## Configuration

Edit the `.env` file with your own settings:
- MASTODON_BASE_URL, the instance where your bot is
- MASTODON_ACCESS_TOKEN, the access token of your bot, just catch it using devtools or something
- GEMINI_API_KEY, API key for gemini, get it [here](https://aistudio.google.com/apikey)

optional but if you want to change them go ahead: 
- GEMINI_MODEL, any of [these models](https://ai.google.dev/gemini-api/docs/models) that output text, i just use gemini 2.0 flash lite idk if the rest works
- SYSTEM_INSTRUCTION, self explanatory the prompt that the bot uses

## For yaoi mode (danbooru.py)

Set these in your `.env` file:

- DANBOORU_API_KEY, danbooru api key self-explanatory
- DANBOORU_USERNAME, your danbooru username

## now what

Run both of these at the same time. Use screen or tmux or whatever.
