from pathlib import Path

def load_template(filename):
    path = f"static/templates/{filename}"
    with open(path, "r", encoding="utf-8") as file:
        return file.read()