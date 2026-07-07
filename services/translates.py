import json

def get_lang(lang="br"):
    with open(f"./translate/{lang}.json", encoding="utf-8") as f:
        return json.load(f)