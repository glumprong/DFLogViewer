from flask import Flask, Response, render_template, request, jsonify
import re
import time
import threading
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)

# Path to your Dwarf Fortress game log file
LOG_FILE_PATH = "/home/ryu/.local/share/Steam/steamapps/common/Dwarf Fortress/gamelog.txt"
FILTERS_FILE_PATH = "/home/ryu/DFTools/DFLogViewer/filters.txt"
SETTINGS_FILE_PATH = "/home/ryu/DFTools/DFLogViewer/settings.json"

log_lines = []
clients = []

def load_filters(file_path):
    filters = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                match = re.match(r'^\[(.*?)\]\[(.*?)\] "(.*)"$', line) # Split categories, subcats, parser string
                if match:
                    category = match.group(1)
                    subcategory = match.group(2)
                    pattern = match.group(3)
                    print(f"Loading filter: Category: {category}, Subcategory: {subcategory}, Pattern: {pattern}")
                    filters.append((category, subcategory, re.compile(pattern)))
                else:
                    print(f"Error loading line: {line}")
            except Exception as e:
                print(f"Error loading line: {line}")
                print(e)
    return filters

filters = load_filters(FILTERS_FILE_PATH)

class LogHandler(FileSystemEventHandler):
    def __init__(self):
        self._log_file = open(LOG_FILE_PATH, 'r', encoding='cp437') # Thanks Putnam for the encoding info
        self._log_file.seek(0, os.SEEK_END)

    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            new_lines = self._log_file.readlines()
            if new_lines:
                for line in new_lines:
                    category, subcategory = self.filter_line(line.strip())
                    if category and subcategory:
                        formatted_line = {
                            "category": category,
                            "subcategory": subcategory,
                            "text": line.strip()
                        }
                    else:
                        formatted_line = {
                            "category": "UNKNOWN",
                            "subcategory": "UNKNOWN",
                            "text": "UNKNOWN"
                        }
                    log_lines.append(formatted_line)
                    for client in clients:
                        client.append(formatted_line)

    def filter_line(self, line):
        for category, subcategory, pattern in filters:
            if pattern.match(line):
                return category, subcategory
        return None, None

log_handler = LogHandler()
observer = Observer()
observer.schedule(log_handler, path=LOG_FILE_PATH, recursive=False)
observer.start()

@app.route('/stream')
def stream():
    def event_stream():
        messages = []
        clients.append(messages)
        try:
            while True:
                if messages:
                    message = messages.pop(0)
                    yield f"data: {message['category']}|{message['subcategory']}|{message['text']}\n\n"
                time.sleep(0.1)
        except GeneratorExit:
            clients.remove(messages)
    return Response(event_stream(), content_type='text/event-stream')

@app.route('/')
def index():
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    return render_template('index.html', settings=settings)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        try:
            # Load the file from the last time or the default file
            with open(SETTINGS_FILE_PATH, 'r') as f:
                current_settings = json.load(f)

            # Get new settings from JSON request body
            new_settings = request.get_json()

            # Check received data
            print("Received JSON data:", new_settings)

            # Merge new settings with existing settings
            updated_settings = current_settings.copy()
            updated_settings.update(new_settings)

            for category in updated_settings.get('categories', []):
                updated_settings[category] = new_settings.get(category, updated_settings[category])
                updated_settings[category + '_bold'] = new_settings.get(category + '_bold', 'normal')
                updated_settings[category + '_italic'] = new_settings.get(category + '_italic', 'normal')
                updated_settings[category + '_underline'] = new_settings.get(category + '_underline', 'none')

            print("Settings to be saved:", updated_settings)

            # Save updated settings
            temp_settings_path = SETTINGS_FILE_PATH + '.tmp'
            with open(temp_settings_path, 'w') as f:
                json.dump(updated_settings, f, indent=4)
            os.rename(temp_settings_path, SETTINGS_FILE_PATH)

            return jsonify({"success": True})

        except Exception as e:
            print("Error writing settings:", e)
            return jsonify({"success": False, "error": str(e)}), 500

    else:
        if not os.path.exists(SETTINGS_FILE_PATH):
            return jsonify({"error": "Settings file not found"}), 404

        try:
            with open(SETTINGS_FILE_PATH, 'r') as f:
                settings = json.load(f)
        except Exception as e:
            print("Error reading settings:", e)
            return jsonify({"error": str(e)}), 500

        return render_template('settings.html', settings=settings)


if __name__ == '__main__':
    # Create default settigns if no file exists
    if not os.path.exists(SETTINGS_FILE_PATH):
        default_settings = {
            "font_size": "26px",
            "categories": ["battle_minor", "battle", "battle_trance", "JobSuspension", "Production", "misc", "masterpiece", "beekeeping", "deaths", "dfhack", "fishing", "interactions", "intruders", "mandates", "mining", "moods", "named_item", "animals", "social", "profession", "migrants", "seasons", "weather", "trading", "system", "emotion"],
            "battle_minor": "#00008B",
            "battle": "#00008B",
            "battle_trance": "#00008B",
            "JobSuspension": "#00008B",
            "Production": "#00008B",
            "misc": "#00008B",
            "masterpiece": "#00008B",
            "beekeeping": "#00008B",
            "deaths": "#00008B",
            "dfhack": "#00008B",
            "fishing": "#00008B",
            "interactions": "#00008B",
            "intruders": "#00008B",
            "mandates": "#00008B",
            "mining": "#00008B",
            "moods": "#00008B",
            "named_item": "#00008B",
            "animals": "#00008B",
            "social": "#00008B",
            "profession": "#00008B",
            "migrants": "#00008B",
            "seasons": "#00008B",
            "weather": "#00008B",
            "trading": "#00008B",
            "system": "#00008B",
            "emotion": "#00008B",
            "battle_minor_bold": "normal",
            "battle_minor_italic": "normal",
            "battle_minor_underline": "none",
            "battle_bold": "normal",
            "battle_italic": "normal",
            "battle_underline": "none",
            "battle_trance_bold": "normal",
            "battle_trance_italic": "normal",
            "battle_trance_underline": "none",
            "JobSuspension_bold": "normal",
            "JobSuspension_italic": "normal",
            "JobSuspension_underline": "none",
            "Production_bold": "normal",
            "Production_italic": "normal",
            "Production_underline": "none",
            "misc_bold": "normal",
            "misc_italic": "normal",
            "misc_underline": "none",
            "masterpiece_bold": "normal",
            "masterpiece_italic": "normal",
            "masterpiece_underline": "none",
            "beekeeping_bold": "normal",
            "beekeeping_italic": "normal",
            "beekeeping_underline": "none",
            "deaths_bold": "normal",
            "deaths_italic": "normal",
            "deaths_underline": "none",
            "dfhack_bold": "normal",
            "dfhack_italic": "normal",
            "dfhack_underline": "none",
            "fishing_bold": "normal",
            "fishing_italic": "normal",
            "fishing_underline": "none",
            "interactions_bold": "normal",
            "interactions_italic": "normal",
            "interactions_underline": "none",
            "intruders_bold": "normal",
            "intruders_italic": "normal",
            "intruders_underline": "none",
            "mandates_bold": "normal",
            "mandates_italic": "normal",
            "mandates_underline": "none",
            "mining_bold": "normal",
            "mining_italic": "normal",
            "mining_underline": "none",
            "moods_bold": "normal",
            "moods_italic": "normal",
            "moods_underline": "none",
            "named_item_bold": "normal",
            "named_item_italic": "normal",
            "named_item_underline": "none",
            "animals_bold": "normal",
            "animals_italic": "normal",
            "animals_underline": "none",
            "social_bold": "normal",
            "social_italic": "normal",
            "social_underline": "none",
            "profession_bold": "normal",
            "profession_italic": "normal",
            "profession_underline": "none",
            "migrants_bold": "normal",
            "migrants_italic": "normal",
            "migrants_underline": "none",
            "seasons_bold": "normal",
            "seasons_italic": "normal",
            "seasons_underline": "none",
            "weather_bold": "normal",
            "weather_italic": "normal",
            "weather_underline": "none",
            "trading_bold": "normal",
            "trading_italic": "normal",
            "trading_underline": "none",
            "system_bold": "normal",
            "system_italic": "normal",
            "system_underline": "none",
            "emotion_bold": "normal",
            "emotion_italic": "normal",
            "emotion_underline": "none",
        }
        with open(SETTINGS_FILE_PATH, 'w') as f:
            json.dump(default_settings, f)
    try:
        app.run(debug=True, threaded=True, host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))
    finally:
        observer.stop()
        observer.join()
