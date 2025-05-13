from deep_translator import GoogleTranslator

def translate_text(text, source_lang, target_lang):
    return GoogleTranslator(source=source_lang, target=target_lang).translate(text)







