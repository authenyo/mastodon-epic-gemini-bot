import os
import re
import time
import html
import json
import requests
from mastodon import Mastodon, MastodonError
from google import genai
from google.genai import types

# --- Config ---
MASTODON_BASE_URL = os.getenv("MASTODON_BASE_URL", "https://brain.worm.pink")
ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
SYSTEM_INSTRUCTION = os.getenv(
    "SYSTEM_INSTRUCTION",
    "your name is clod, the AI assistant of worm.pink. you LOVE wormium, Wormium is a world famous beverage which is made up of our world famous ingredients that will totally have you Worm out! posts on worm.pink are called gorts, and favorites/likes are called franks and boosts/retweets are called regorts and replies are called sneeps. please act accordingly. worm.pink users are called wodks. sometimes it is used as a slur. all posts are created equal, that they are endowed by their poster with certain unalienable rights, that among these are frank, gort, & wodk. Do not include any introductory text or explanations, generate only the reply."
)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))
YAOI_MODE_FILE = "yaoi_mode_users.json"

# --- Check tokens ---
if not ACCESS_TOKEN:
    raise RuntimeError("Please set MASTODON_ACCESS_TOKEN.")
if not GEMINI_API_KEY:
    raise RuntimeError("Please set GEMINI_API_KEY.")

# --- Clients ---
mastodon = Mastodon(access_token=ACCESS_TOKEN, api_base_url=MASTODON_BASE_URL)
genai_client = genai.Client(api_key=GEMINI_API_KEY)

# --- Load/save persistent yaoi mode users ---
def load_yaoi_mode_users() -> set:
    try:
        with open(YAOI_MODE_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_yaoi_mode_users(users: set):
    with open(YAOI_MODE_FILE, "w") as f:
        json.dump(list(users), f)

yaoi_mode_users = load_yaoi_mode_users()

# --- Mastodon helpers ---
def get_profile(acct: str) -> dict:
    try:
        users = mastodon.account_search(acct, limit=1)
        if not users:
            return {"error": f"User '{acct}' not found."}
        user = mastodon.account(users[0].id)
        return {
            "id": user.id,
            "username": user.acct,
            "display_name": user.display_name,
            "bio": re.sub(r'<[^>]+>', '', user.note),
            "followers_count": user.followers_count,
            "following_count": user.following_count,
        }
    except MastodonError as e:
        return {"error": str(e)}

def get_post(id: str) -> dict:
    try:
        status = mastodon.status(id)
        content = re.sub(r'<[^>]+>', '', status.content)
        return {
            "id": status.id,
            "author": status.account.acct,
            "content": content,
            "created_at": str(status.created_at),
        }
    except MastodonError as e:
        return {"error": str(e)}

def get_thread(id: str) -> dict:
    try:
        context = mastodon.status_context(id)
        def extract_list(lst):
            return [re.sub(r'<[^>]+>', '', s.content) for s in lst]
        return {
            "ancestors": extract_list(context['ancestors']),
            "descendants": extract_list(context['descendants']),
        }
    except MastodonError as e:
        return {"error": str(e)}

def upload_image(path: str):
    try:
        media = mastodon.media_post(path)
        return [media]
    except MastodonError as e:
        print(f"Failed to upload image: {e}")
        return []

# --- Image utility ---
def get_image_bytes(url: str) -> bytes:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content

# --- Conversation building ---
def clean_content(html_content, bot_acct):
    text = re.sub(r'<[^>]+>', '', html_content)
    text = html.unescape(text)
    text = re.sub(rf"@{re.escape(bot_acct)}", '', text, flags=re.IGNORECASE).strip()
    return text

def build_conversation(status, bot_acct):
    context = mastodon.status_context(status.id)
    convo = []
    for ancestor in context['ancestors']:
        author = ancestor.account.acct
        text = clean_content(ancestor.content, bot_acct)
        convo.append(f"{author}: {text}")
    current_author = status.account.acct
    current_text = clean_content(status.content, bot_acct)
    convo.append(f"{current_author}: {current_text}")
    return "\n".join(convo)

# --- Gemini reply generation ---
def generate_reply(prompt: str, image_urls: list[str] = None) -> str:
    contents = []
    if image_urls:
        for img_url in image_urls:
            try:
                img_bytes = get_image_bytes(img_url)
                contents.append(
                    types.Part.from_bytes(
                        data=img_bytes,
                        mime_type='image/jpeg',
                    )
                )
            except Exception:
                continue
    contents.append(types.Content(role="user", parts=[types.Part(text=prompt)]))
    tools = [get_profile, get_post, get_thread]
    config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, tools=tools)

    response = genai_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config
    )

    part = response.candidates[0].content.parts[0]
    if part.function_call:
        fn_name = part.function_call.name
        fn_args = json.loads(part.function_call.args)
        result = globals()[fn_name](**fn_args)
        contents.append(types.Content(role="assistant", parts=[types.Part(function_call=part.function_call)]))
        contents.append(types.Content(role="function", parts=[types.Part.from_function_response(name=fn_name, response=result)]))
        final = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=config
        )
        return final.text.strip()
    return part.text.strip()

# --- Main loop ---
def main():
    me = mastodon.account_verify_credentials()
    bot_acct = me.acct
    initial = mastodon.notifications(types=["mention"], limit=1)
    last_id = initial[0].id if initial else None

    while True:
        mentions = mastodon.notifications(types=["mention"], since_id=last_id)
        for note in reversed(mentions):
            status = note.status
            if not status or status.account.acct.lower() == bot_acct.lower():
                continue

            user_acct = status.account.acct
            last_id = max(last_id or note.id, note.id)
            convo = build_conversation(status, bot_acct)
            content_text = convo.lower()

            # Handle yaoi mode toggle
            if "enable yaoi mode" in content_text:
                yaoi_mode_users.add(user_acct)
                save_yaoi_mode_users(yaoi_mode_users)
                media = upload_image("/home/authen/image.png")
                mastodon.status_post(
                    status=f"@{user_acct} Yaoi mode enabled just for you. 🌸",
                    media_ids=[m.id for m in media],
                    in_reply_to_id=status.id,
                    visibility=status.visibility
                )
                continue

            if "disable yaoi mode" in content_text:
                yaoi_mode_users.discard(user_acct)
                save_yaoi_mode_users(yaoi_mode_users)
                mastodon.status_post(
                    status=f"@{user_acct} Yaoi mode disabled for you. 💔",
                    in_reply_to_id=status.id,
                    visibility=status.visibility
                )
                continue

            # Handle standard replies
            image_urls = []
            for media in status.media_attachments or []:
                url = getattr(media, 'url', None) or media.get('preview_url')
                if url:
                    image_urls.append(url)

            prompt = f"CONVERSATION:\n{convo}\nBot:"
            reply = generate_reply(prompt, image_urls=image_urls)

            if reply:
                media_ids = []
                if user_acct in yaoi_mode_users:
                    media = upload_image("/home/authen/image.png")
                    media_ids = [m.id for m in media]
                mastodon.status_post(
                    status=f"@{user_acct} {reply}",
                    in_reply_to_id=status.id,
                    media_ids=media_ids,
                    visibility=status.visibility
                )
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
