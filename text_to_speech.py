from gtts import gTTS
import os


def speech(text):

    language = 'en'

    output = gTTS(text=text, lang=language, slow=False)

    output.save("static/output.mp3")


    # Play the converted file
    #os.system("start static/output.mp3")



