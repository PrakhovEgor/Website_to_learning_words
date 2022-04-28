from gtts import gTTS


def speech(text, lg, id):
    language = ['en', 'ru']
    output = gTTS(text=text, lang=language[lg], slow=False)
    output.save(f"static/{id}.mp3")
