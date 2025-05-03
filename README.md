<p><h1>mastodon-epic-gemini-bot, aka clod</h1>
<img src="https://4get.authenyo.xyz/proxy?i=https%3A%2F%2Fmedia.tenor.com%2FlJa1KnY6quwAAAAM%2Fnettspend-drankdrankdrank.gif" align="right"></p>

python mastodon AI chatbot that uses the gemini API that's really bad and i made with chatgpt. it sucks but its really funny. used for the best AI assistant ever, [clod](https://brain.worm.pink/clod).

# HOW DO I SET THIS SHIT UP

you technically need to run 2 scripts at the same time, main.py and danbooru.py for the yaoi mode. dont ask why. i should make it a toggle probably idk

## main.py
you need to set up your envs. if youre too lazy just edit the code to hardcode them in no one cares its 2025 you can do anything you want

the ones needed are:
- MASTODON_BASE_URL, the instance where your bot is
- MASTODON_ACCESS_TOKEN, the access token of your bot, just catch it using devtools or something
- GEMINI_API_KEY, API key for gemini, get it [here](https://aistudio.google.com/apikey)

optional but if you want to change them go ahead: 
- GEMINI_MODEL, any of [these models](https://ai.google.dev/gemini-api/docs/models) that output text, i just use gemini 2.0 flash lite idk if the rest works
- SYSTEM_INSTRUCTION, self explanatory the prompt that the bot uses

## danbooru.py

go in the code and edit these variables

- API_KEY, danbooru api key self-explanatory
- USERNAME,  your danbooru username

## now what

run both of these at the same time and it fucking WORKS!!!!!!!!!!!!!!!!!
