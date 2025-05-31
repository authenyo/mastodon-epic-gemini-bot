<h1>mastodon-epic-gemini-bot, aka clod</h1>
<img src="https://4get.authenyo.xyz/proxy?i=https%3A%2F%2Fmedia.tenor.com%2FlJa1KnY6quwAAAAM%2Fnettspend-drankdrankdrank.gif" align="right">
<center><img src="https://files.catbox.moe/ut9vn3.jpg"></center>

LLM Mastodon bot that uses either the Gemini API or the OpenAI API. It also has yaoi mode. Talk to it [here](https://brain.worm.pink/clod) (default prompt a little unhinged, may be offensive).

# ✨ Features
- **yaoi mode**

Scrapes a random image from Danbooru and attaches it to every response for a user, enable by mentioning the bot and typing "enable yaoi mode".
- **image understanding** 

if you mention the bot with a image attached it will download the image and send it over to the LLM. (may not work in the OpenAI api idk)
- **function calling** 

it can fetch the thread for context, search posts, fetch profiles and urls.
- **it's awesome.** 

very awesome

## Installation

1. Install required dependencies:
```
pip install -r requirements.txt
```

2. Copy the `.env-example` file to `.env` and edit it with your settings:
```
cp .env-example .env
```

3. Run both `main.py` and `danbooru.py` at the same time. You can use `screen` for this.
```
python main.py
```
```
python danbooru.py
```
## Configuration

### main.py

Edit the `.env` file with your own settings:
- AI_PROVIDER, `gemini` or `openai`
- GEMINI_API_KEY, API key for gemini, get it [here](https://aistudio.google.com/apikey)
- MASTODON_BASE_URL, the instance where your bot is
- MASTODON_ACCESS_TOKEN, the access token of your bot, just catch it using devtools or something
- OPENAI_API_KEY, API key for OpenAI

optional but if you want to change them go ahead: 
- GEMINI_MODEL, any of [these models](https://ai.google.dev/gemini-api/docs/models) that output text, i just use gemini 2.0 flash idk if the rest works
- SYSTEM_INSTRUCTION, self explanatory the prompt that the bot uses
- OPENAI_BASE_URL, if you want to use stuff like DeepSeek and anything compatible with the OpenAI API
- OPENAI_MODEL, which model you're using on OpenAI

### For yaoi mode (danbooru.py)

- DANBOORU_API_KEY, danbooru api key self-explanatory
- DANBOORU_USERNAME, your danbooru username
