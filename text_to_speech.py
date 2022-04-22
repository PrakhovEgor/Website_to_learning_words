from gtts import gTTS


def speech(text, lg):
    language = ['en', 'ru']
    output = gTTS(text=text, lang=language[lg], slow=False)
    output.save("static/output.mp3")
