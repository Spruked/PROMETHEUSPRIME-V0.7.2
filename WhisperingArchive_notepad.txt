class WhisperingArchive:
    def __init__(self):
        self.logs = []
        self.emotional_index = {}

    def record(self, message, emotion=None, glyph=None):
        entry = {
            "message": message,
            "emotion": emotion,
            "glyph": glyph
        }
        self.logs.append(entry)
        if emotion:
            self.emotional_index.setdefault(emotion, []).append(entry)

    def retrieve_by_emotion(self, emotion):
        return self.emotional_index.get(emotion, [])

    def invoke_whisper(self, glyph):
        return [log for log in self.logs if log["glyph"] == glyph]

    def get_logs(self):
        return self.logs

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            for log in self.logs:
                file.write(f"{log['message']}|{log['emotion']}|{log['glyph']}\n")

    def load_from_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                message, emotion, glyph = line.strip().split('|')
                self.record(message, emotion, glyph)
