import html

def format_text_for_db(text: str):
    return html.unescape(text).lower().strip()