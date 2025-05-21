from deep_translator import GoogleTranslator
from langcodes import Language, get, Language
from application_parts.multi_language.phrases import *
from babel import Locale
from pycountry import languages

# def translate_phrase(var_name:str, target_lang_code:str)->str:
#     return GoogleTranslator(source='uk', target=target_lang_code).translate(eval(var_name))

def return_all_lang_codes():
    all_lang_info = list(languages)
    all_lang_codes = [language.alpha_2 for language in all_lang_info if hasattr(language, 'alpha_2') and language.alpha_2 != 'ru' and check_language_code(language.alpha_2)]    
    return all_lang_codes

def translate_phrase(phrase:str, target_lang_code:str)->str:
    return GoogleTranslator(source='uk', target=target_lang_code).translate(eval(phrase))

def check_language_accurance(target_lang_code:str)->str:
    question_part =  GoogleTranslator(source='uk', target=target_lang_code).translate(lang_question)
    full_language_name = GoogleTranslator(source='en', target=target_lang_code).translate(Language.get(target_lang_code).display_name())
    return question_part + " " + full_language_name + "?"

def check_language_code(lang_code:str)->bool:
    try:
        Locale.parse(lang_code)
        return True
    except :
        return False

def return_you_choose(second_part:str, target_lang_code:str)->str:
    result = you_choose + second_part + "!"
    return translate_phrase(result, target_lang_code)

def return_please_choose_question(second_part:str, target_lang_code:str)->str:
    result = please_choose + second_part
    return translate_phrase(result, target_lang_code)