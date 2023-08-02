#
# JBad: Bad JSON Parser (Pure Python) v1, revision 2, 21.07.2023
#
# PS: for Yaml Parse need PyYAML (`import yaml` in `def yamls(txt, *args, **kwargs)`)
# PS: Для парсинга Yaml нужен PyYAML (`import yaml` in `def yamls(txt, *args, **kwargs)`)
#
# Usage:
#   jbad.loads("...")
#

import re # FOR SOME RETURNS # Для некторых возвратов `{} {} {}`


# PRESETS # ПРЕСЕТЫ #
ALLOW_SORRY_ERRORS             = True   # Строка Sorry, как ошибка          # Sorry,asofnow,AppleWatchSeries8hasnotbeenreleasedyet.
ALLOW_PRELIMINARY_PARSING      = True   # Включать предварительный парсинг  # PRELIMINARY PARSING (уменьшает число проходов, но увеличивает число ошибок)
ALLOW_KEYS_WITHOUT_QUOTAS      = True   # Имена параметров без кавычек      # {  key :  "Value" }
ALLOW_KEYS_AS_DIGITS           = True   # Имена параметров как число        # {  111 :  "Value" }
ALLOW_STRINGS_IN_SINGLE_QUOTAS = True   # Строки в одинарных кавычках       # { 'key':  'Value' }
ALLOW_FORGET_COMMA_IN_DICT     = True   # Пропущены запятые в словарях      # { 'key':  'Value'  'Key2': 'Value2'}
ALLOW_FORGET_COMMA_IN_ARRAY    = True   # Пропущены запятые в массивах      # [ 'x' 'y' 'z' ]
ALLOW_ENDING_COMMA_IN_DICT     = True   # Открытая запятая в конце словаря  # { 'key':  'Value', 'Key2': 'Value2', }
ALLOW_ENDING_COMMA_IN_ARRAY    = True   # Открытая запятая в конце массива  # [ 'x', 'y', 'z', ]
ALLOW_EMPTY_RECORDS_IN_DICT    = True   # Возможны пропуски в словаре       # { 'key':  'Value', ,  'Key2': 'Value2' } { 'key':  'Value', 'Key2' ,  'Key3': 'Value3' } -> None
ALLOW_EMPTY_RECORDS_IN_ARRAY   = True   # Пустые элементы в массиве         # [ 0, 1, , 2]  ->  None
ALLOW_FORGOT_START_DICT        = True   # Нет открывающей скобки словаря    # 'key':  'Value',  'Key2': 'Value2' }
ALLOW_FORGOT_END_DICT          = True   # Нет закрывающей скобки словаря    # { 'key':  'Value', ,  'Key2': 'Value2'
ALLOW_FORGOT_START_ARRAY       = True   # Нет открывающей скобки массива    # 0, 1 ]
ALLOW_FORGOT_END_ARRAY         = True   # Нет закрывающей скобки массива    # [ 0, 1
ALLOW_STRINGS_STARTS_WITH_DOG  = True   # Допускаются строки с собаки       # { "key": @"Value" }
ALLOW_DICTS_WITHOUT_CAGE       = True   # Возможен словарь без скобок       # 'key':  'Value', 'Key2': 'Value2'
ALLOW_CALC_BLOCKS_IF_THROW     = True   # Считать число скобок словаря      # ... }}}
ALLOW_YAML_ANALYSE             = True   # Проверять на предмет Yaml         # YAML (выполняется намного дольше)
ALLOW_YAML_PLUS_JSON_ANALYSE   = True   # Проверять на предмет Yaml+JSON    # YAML + JSON (выполняется намного-намного дольше)
ALLOW_THREE_DOTS_AS_ANY        = True   # Многоточье как любое значение     # , ... ,
ALLOW_FLEXIBLE_NUMBERS         = True   # Нестандартная запись чисел        # .5 | +10
ALLOW_SIMPLE_TYPES_RETURN      = False  # Возвращать простые типы как dict  # string | int | float ...
ALTERNATIVE_DECIMAL_DELIMITERS = [',']  # Массив доп разделителей дроби (,) # { "Price": 2,15 } -- ARRAY
DEFAULT_WHITE_SPACE_CHARACTERS = [' ', '\t', '\r', '\n', u'\u2800']         # Пробелы # WhiteSpace 


# COUNTERS #
COUNTER_JSON = 0 # Считаем число проходов
COUNTER_YAML = 0 # Считаем число проходов


def loads(txt: str, pos: int = 0, *args, **kwargs):
    """
    Parse JSON Text
    """

    global COUNTER_JSON
    COUNTER_JSON += 1

    # COLLECT ARGUMENTS #
    DEPTH            = 0     # Глубина рекурсии
    SKIP_ARRAY_CAGES = False # Пропускать проверку массива без скобок
    SKIP_DICT_CAGES  = False # Пропускать проверку словаря без скобок
    SKIP_LAST_DI_STR = False # Пропускать проверку открывающей скобки словаря
    SKIP_LAST_DI_END = False # Пропускать проверку закрывающей скобки словаря
    SKIP_LAST_AR_STR = False # Пропускать проверку открывающей скобки массива
    SKIP_LAST_AR_END = False # Пропускать проверку закрывающей скобки массива   
    SKIP_YAML_PARSE  = False # Пропускать проверку Yaml
    for k,v in kwargs.items():
        if k == "DEPTH"           : DEPTH             = v
        if k == "SKIP_ARRAY_CAGES": SKIP_ARRAY_CAGES  = v
        if k == "SKIP_DICT_CAGES" : SKIP_DICT_CAGES   = v
        if k == "SKIP_LAST_DI_STR": SKIP_LAST_DI_STR  = v
        if k == "SKIP_LAST_DI_END": SKIP_LAST_DI_END  = v
        if k == "SKIP_LAST_AR_STR": SKIP_LAST_AR_STR  = v
        if k == "SKIP_LAST_AR_END": SKIP_LAST_DI_END  = v        
        if k == "SKIP_YAML_PARSE" : SKIP_YAML_PARSE   = v        

    # EMPTY RESULT # ПУСТАЯ СТРОКА #
    if len(txt) == 0: return None    
    if pos > len(txt): return None    

    # ALL SPACES # ПРОБЕЛЫ #
    pos = trim_leading(txt, pos)
    if pos >= len(txt): return None    

    # INIT TEXT # ПЕРВЫЕ СИМВОЛЫ #
    start = pos
    first = txt[start:start+1]

    # PRELIMINARY PARSING # RECURSIVE # CAN BE REMOVED IF LOW PERFOMANCE #  
    # ПРЕДВАРИТЕЛЬНЫЙ ПАРСИНГ # ПРОПУСКАЕТСЯ ПРИ РЕКУРСИИ # МОЖНО ОТКЛЮЧИТЬ ДЛЯ СКОРОСТИ #

    if ALLOW_SORRY_ERRORS and (txt[start:].startswith("Sorry,") or txt[start:].startswith("'Sorry,") or txt[start:].startswith('"Sorry,')):
        JsonBodyException.throw(txt.strip())    

    if ALLOW_PRELIMINARY_PARSING:
        if ALLOW_FORGOT_START_ARRAY and not SKIP_LAST_AR_STR and txt.strip().endswith("]") and not txt[start:].startswith("["):
            try: return loads("[" + txt, SKIP_LAST_AR_STR = True, DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)
            except: pass
        if ALLOW_FORGOT_END_ARRAY and not SKIP_LAST_AR_END and txt[start:].startswith("]") and not txt.strip().endswith("["):
            try: return loads(txt + "]", SKIP_LAST_AR_END = True, DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)
            except: pass        
        if ALLOW_DICTS_WITHOUT_CAGE and not SKIP_ARRAY_CAGES and first == "{" and re.search('}\\s*{', txt):
            try: return loads("[" + txt + "]", SKIP_DICT_CAGE = True, DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)
            except: pass    
    
    # WITH POSTANALYSE # С ПОСТОБРАБОТКОЙ ИСКЛЮЧЕНИЙ #
    try:

        # PRELIMINARY PARSING - QUOTED TEXT # 
        # ПРЕДВАРИТЕЛЬНЫЙ ПАРСИНГ - ТЕКСТ В КАВЫЧКАХ #
        if ALLOW_PRELIMINARY_PARSING:
            if ALLOW_DICTS_WITHOUT_CAGE and not SKIP_DICT_CAGES and (first == '"' or first == "'"):
                p = trim_leading(txt, parse_string(txt, start, first)[1])
                if txt[p:p+1] == ':': return loads("{" + txt + "}", SKIP_DICT_CAGES = True, DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)

        if ALLOW_YAML_ANALYSE and not SKIP_YAML_PARSE and txt[start:].startswith("-"): 
            SKIP_YAML_PARSE = True
            return yamls(txt, DEPTH = DEPTH) # YAML

        # MAIN JSON PARSING # ОСНОВНОЙ ПАРСИНГ JSON #
        element, pos = parse_json(txt, pos)
        validate_json(txt, pos, condition = (pos == len(txt)))
        diff = isinstance(element, dict) or isinstance(element, list)
        if not diff:
            if ALLOW_SIMPLE_TYPES_RETURN: return {"result": element}
            else: JsonValidationException.throw("Text isn't a JSON:", txt, 0)
        return element

    # POSTANALYSE # ПОСТОБРАБОТКА ИСКЛЮЧЕНИЙ #
    except Exception as e:

        # COMMA ERROR IN ARRAY OB OBJECTS # ВОЗМОЖНО ОШИБКА В МАССИВЕ ОБЪЕКТОВ - НЕТ ЗАПЯТОЙ #
        if isinstance(e, JsonValidationException):
            if txt[start:].startswith("{") and e.Symbol == ',':
                try: return loads("[" + txt + "]", DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)
                except Exception as ie: set_inner_exceptions(e, ie)

        # FORGOR { } # ЗАБЫЛИ ОДНУ ИЗ СКОБОК #
        if isinstance(e, JsonValidationException) or isinstance(e, IndexError):
            if ALLOW_FORGOT_START_DICT and not SKIP_LAST_DI_STR and txt.strip().endswith("}") and not txt[start:].startswith("{"):
                try: return loads("{" + txt, SKIP_LAST_BL_STR = True, DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)
                except Exception as ie: set_inner_exceptions(e, ie)
            if ALLOW_FORGOT_END_DICT and not SKIP_LAST_DI_END and txt[start:].startswith("{") and not txt.strip().endswith("}"):
                try: return loads(txt + "}", SKIP_LAST_BL_END = True, DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)
                except Exception as ie: set_inner_exceptions(e, ie)

        # CALCULATE {} # ПОДСЧЕТ СКОБОК, ВОЗМОЖНО ЗАБЫЛИ ЗАКРЫТЬ/ОТКРЫТЬ #
        if ALLOW_CALC_BLOCKS_IF_THROW and DEPTH == 0:
           bs = txt[start:].startswith("{")
           be = txt.strip().endswith("}")
           if bs or be:
                bstart, bend = calculate_blocks(txt)
                if bstart > bend:
                    for i in range(bend, bstart): txt = txt + "}"
                if bend > bstart:
                    for i in range(bstart, bend): txt = "{" + txt
                if bs != be: txt = "{" + txt + "}"
                try: return loads(txt, DEPTH = DEPTH + 1, SKIP_YAML_PARSE = SKIP_YAML_PARSE)
                except Exception as ie: set_inner_exceptions(e, ie)

        # MAYBE YAML # ВОЗМОЖНО YAML #
        if ALLOW_YAML_ANALYSE and not SKIP_YAML_PARSE and not isinstance(e, YamlValidationException) and DEPTH == 0:
            try: return yamls(txt, DEPTH = DEPTH)
            except Exception as ie: set_inner_exceptions(e, ie)

        raise e


def trim_leading(txt, pos):
    """
    Return Leading Non-Whitespace Position
    """

    #return re.compile(r'\s*').match(txt, pos).end() # -- slower
    ln = len(txt)
    for i in range(pos, ln): 
        if txt[i] not in DEFAULT_WHITE_SPACE_CHARACTERS: 
            return i
    return ln


def trim_trailing(txt, pos): 
    """
    Return Traling Non-Whitespace Position
    """

    return trim_leading(txt, pos + 1)


def calculate_blocks(txt):
    """
    Calculate {} blocks
    """

    bs = 0
    be = 0
    i = 0
    while i < len(txt):
        if txt[i] in ['"','"']:
            i += 1
            while txt[i] not in ['"','"']:
                if txt[i] == '\\': i += 2
                else: i += 1        
        if txt[i] == '{': bs += 1
        if txt[i] == '}': be += 1
        i += 1
    return bs, be


def parse_json(txt, pos, objType = None):
    """
    Parse JSON Any from string
    """

    first_char = txt[pos]
    if first_char == '{':
        return parse_object(txt, pos)
    elif first_char == '[':
        return parse_array(txt, pos)
    elif first_char == '"':
        return parse_string(txt, pos, '"')
    elif ALLOW_STRINGS_IN_SINGLE_QUOTAS and first_char == "'":
        return parse_string(txt, pos, "'")
    elif ALLOW_STRINGS_STARTS_WITH_DOG and first_char == "@":
        return parse_json(txt, pos + 1)
    elif first_char == 'n':
        return parse_null(txt, pos)
    elif first_char == 't' or first_char == 'T':
        return parse_true(txt, pos)
    elif first_char == 'f' or first_char == 'F':
        return parse_false(txt, pos)
    elif ALLOW_THREE_DOTS_AS_ANY and txt[pos:].startswith('...'):
        return parse_dots(txt, pos)
    else:
        return parse_number(txt, pos)


def parse_object(txt, pos):
    """
    Parse JSON Object from string
    """

    validate_json(txt, pos, expected='{')

    pos = trim_trailing(txt, pos)
    obj = {}

    while (symb := txt[pos]) != '}':

        if ALLOW_KEYS_AS_DIGITS and symb.isdigit():
            key, pos = parse_key_as_digits(txt, pos)
        elif ALLOW_KEYS_WITHOUT_QUOTAS and symb.isalpha():
            key, pos = parse_key_no_quotas(txt, pos)
        elif ALLOW_STRINGS_STARTS_WITH_DOG and symb == "@":
            pos += 1
            continue
        elif ALLOW_STRINGS_IN_SINGLE_QUOTAS and symb == "'":
            key, pos = parse_string(txt, pos, symb)
        else:
            key, pos = parse_string(txt, pos)

        if ALLOW_EMPTY_RECORDS_IN_DICT and (symb := txt[trim_leading(txt, pos)]) in ['}',',']:
            obj[key] = None
            pos = trim_trailing(txt, pos)
            validate_json(txt, pos, not_expected='}')
            continue

        validate_json(txt, pos, expected=':')
        value, pos = parse_json(txt, trim_trailing(txt, pos), 'obj')

        obj[key] = value

        if (symb := txt[pos]) == ',':
            pos = trim_trailing(txt, pos)
            if ALLOW_ENDING_COMMA_IN_DICT and txt[pos] == "}": break
            if ALLOW_EMPTY_RECORDS_IN_DICT:
                while txt[pos] == ",": pos = trim_trailing(txt, pos)   
                continue
            validate_json(txt, pos, not_expected='}')
        elif ALLOW_FORGET_COMMA_IN_DICT and symb != '}':
            validate_json(txt, pos, not_expected='}')
        else:
            validate_json(txt, pos, expected='}')

    return obj, trim_trailing(txt, pos)


def parse_array(txt, pos):
    """
    Pars JSON Array from string
    """

    validate_json(txt, pos, expected='[')

    pos = trim_trailing(txt, pos)
    arr = []

    while txt[pos] != ']':
        
        python_element, pos = parse_json(txt, pos, 'arr')
        arr.append(python_element)

        if (symb := txt[pos]) == ',':            
            pos = trim_trailing(txt, pos)            
            if ALLOW_ENDING_COMMA_IN_ARRAY and txt[pos] == "]": break
            if ALLOW_EMPTY_RECORDS_IN_ARRAY:
                while txt[pos] == ",":
                    arr.append(None)
                    pos = trim_trailing(txt, pos)   
                continue
            validate_json(txt, pos, not_expected=']')
        elif ALLOW_FORGET_COMMA_IN_ARRAY and symb != '}':
            validate_json(txt, pos, not_expected='}')
        else:
            validate_json(txt, pos, expected=']')

    return arr, trim_trailing(txt, pos)


def parse_string(txt, pos, endsymbol='"'):
    """
    Parse JSON String from string
    """

    validate_json(txt, pos, expected=endsymbol)

    pos += 1
    i0 = pos
    while txt[pos] != endsymbol:
        if txt[pos] == '\\': pos += 2
        else: pos += 1

    python_string = escape(txt[i0:pos])
    return python_string, trim_trailing(txt, pos)


def parse_key_no_quotas(txt, pos):  
    """
    Parse JSON String without Quotas
    """

    i0 = pos
    while txt[pos] != ":":
        if txt[pos] == '\\': pos += 2
        else: pos += 1

    python_string = escape(txt[i0:pos])
    return python_string, pos


def parse_key_as_digits(txt, pos):  
    """
    Parse JSON Dictionary Keys as Digits
    """

    i0 = pos
    while txt[pos] not in ["'",'"',':',',']:
        if txt[pos] == '\\': pos += 2
        else: pos += 1

    python_string = escape(txt[i0:pos])
    return python_string, pos


def parse_null(txt, pos):
    """
    Parse JSON Null from string
    """

    validate_json(txt, pos, condition=(txt[pos:pos+4].lower() == 'null'))
    return None, trim_leading(txt, pos+4)


def parse_true(txt, pos):
    """
    Parse JSON True from string
    """
    
    validate_json(txt, pos, condition=(txt[pos:pos+4].lower() == 'true'))
    return True, trim_leading(txt, pos+4)


def parse_false(txt, pos):
    """
    Parse JSON False from string
    """

    validate_json(txt, pos, condition=(txt[pos:pos+5].lower() == 'false'))
    return False, trim_leading(txt, pos+5)


def parse_number(txt, pos):
    """
    Parse JSON Number from string
    """

    if ALLOW_FLEXIBLE_NUMBERS:
        validate_json(txt, pos, condition=(txt[pos] in '+-IN.' or '0' <= txt[pos] <= '9'))
    else:
        validate_json(txt, pos, condition=(txt[pos] in '-IN' or '0' <= txt[pos] <= '9'))

    is_number_char = lambda char: '0' <= char <= '9' or char in '+-Ee.'
    
    prefix = ""
    while True:
        if txt[pos] == 'N':
            validate_json(txt, pos, condition=(txt[pos:pos+3] == 'NaN'))
            return float('nan'), trim_leading(txt, pos+3)
        elif txt[pos] == 'I':
            validate_json(txt, pos, condition=(txt[pos:pos+8] == 'Infinity'))
            return float('inf'), trim_leading(txt, pos+8)
        elif txt[pos] == '-' and txt[pos+1] == 'I':
            validate_json(txt, pos, condition=(txt[pos:pos+9] == '-Infinity'))
            return float('-inf'), trim_leading(txt, pos+9)
        elif ALLOW_FLEXIBLE_NUMBERS and txt[pos] == "+":
            pos += 1
            continue
        elif ALLOW_FLEXIBLE_NUMBERS and txt[pos] == "." and txt[pos + 1].isdigit():
            pos += 1
            prefix = "0."
        break
    
    if not ALTERNATIVE_DECIMAL_DELIMITERS:
        j = next((j for j in range(pos, len(txt)) if not is_number_char(txt[j])), len(txt))
    else:
        delimiter = None
        for j in range(pos, len(txt)):
            ch = txt[j]
            if is_number_char(ch) or ch == '.': continue
            if ch in ALTERNATIVE_DECIMAL_DELIMITERS: 
                delimiter = ch
                continue
            while txt[pos:j].endswith(','): j += -1
            break
        if delimiter:
            try: return float(txt[pos:j].replace(delimiter,".")), trim_leading(txt, j)
            except ValueError as ie: JsonValidationException.throw('Invalid JSON number:', txt, pos, [ie])

    use_float = float if prefix else any(txt[i] in 'Ee.' for i in range(pos, j))
    python_converter = float if use_float else int

    numb = txt[pos:j]

    if ALLOW_FLEXIBLE_NUMBERS:
        if numb == "." or numb == '-' or numb == '+': return 0, trim_leading(txt, j)
        if numb in ".....": return float('inf'), trim_leading(txt, j)
    else:
        if numb == "." or numb == '-' or numb == '+': JsonValidationException.throw('Unexpected token:', txt, pos)

    try:
        return python_converter(prefix + numb), trim_leading(txt, j)
    except ValueError as ie:
        JsonValidationException.throw('Invalid JSON number:', txt, pos, [ie])


def parse_dots(txt, pos):
    """
    Parse `...`
    """

    ln = len(txt)
    for i in range(pos, ln): 
        till = i
        if txt[i] != '.' or txt[i] in DEFAULT_WHITE_SPACE_CHARACTERS or txt[i] in [',' , ']', '}']: 
            break        
    return txt[pos:till], till


def validate_json(txt, pos, expected=None, not_expected=None, condition=None):
    """
    Validate JSON String
    """

    assert expected is not None or not_expected is not None or condition is not None,\
        'expected, not_expected, or condition must be declared'

    expected is not None and txt[pos] == expected or \
    not_expected is not None and txt[pos] != not_expected or \
    condition is True or \
    JsonValidationException.throw('Unexpected token:', txt, pos)


def escape(st, encoding='utf-8'):
    """
    Escape String
    """

    return (st.encode('latin1')        # To bytes, required by 'unicode-escape'
             .decode('unicode-escape') # Perform the actual octal-escaping decode
             .encode('latin1')         # 1:1 mapping back to bytes
             .decode(encoding))


################## YAML BLOCK ##################


def yamls(txt, *args, **kwargs):
    """
    Parse Yaml
    """

    global COUNTER_YAML
    COUNTER_YAML += 1

    import yaml # PyYAML

    DEPTH = 0 # Глубина рекурсии
    NOT_WITH_JSON = False # Пропускать проверку JSON & YAML
    for k,v in kwargs.items():
        if k == "DEPTH": DEPTH  = v
        if k == "NOT_WITH_JSON": NOT_WITH_JSON  = v

    try: 
       res = yaml.safe_load(txt)
       return res
    except Exception as e:
        if ALLOW_YAML_PLUS_JSON_ANALYSE and not NOT_WITH_JSON:
            lines = txt.splitlines()
            try: return json_and_yaml_parse(lines, DEPTH)        
            except Exception as ie: set_inner_exceptions(e, ie)
            try: return yaml_and_json_parse(lines, DEPTH)        
            except Exception as ie: set_inner_exceptions(e, ie)
        YamlValidationException.throw(e)


def json_and_yaml_parse(lines, depth = 0):
    """
    Check JSON then Yaml
    """

    index = -1    
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if "]" in line or "}" in line:
            index = i 
            break
    if index > 0 and index < len(lines):
        json_text = ""
        for i in range(0, index + 1): json_text += lines[i] + "\n"
        yaml_text = ""
        for i in range(index + 1, len(lines)): yaml_text += lines[i] + "\n"
        json_text = json_text.strip()
        yaml_text = yaml_text.strip()
        if len(json_text) > 1 and len(yaml_text) > 2: # [] | a:b
            try: json_res = loads(json_text, SKIP_YAML_PARSE = True, DEPTH = depth + 1)
            except: json_res = {}
            try: yaml_res = yamls(yaml_text, NOT_WITH_JSON = True, DEPTH = depth + 1)
            except: yaml_res = {}
            if bool(json_res) or bool(yaml_res): 
                return merge_json_and_yaml(json_res, yaml_res)
    YamlValidationException.throw("Not a JSON + Yaml")


def yaml_and_json_parse(lines, depth = 0):
    """
    Check Yaml then JSON
    """

    index = -1    
    for i in range(0, len(lines)):        
        line = lines[i].strip()
        if "[" in line or "{" in line: break        
        index = i
    if index > 0 and index < len(lines):
        yaml_text = ""
        for i in range(0, index + 1): yaml_text += lines[i] + "\n"
        json_text = ""
        for i in range(index + 1, len(lines)): json_text += lines[i] + "\n"
        yaml_text = yaml_text.strip()
        json_text = json_text.strip()
        if len(yaml_text) > 1 and len(json_text) > 2: # [] | a:b
            try: json_res = loads(json_text, SKIP_YAML_PARSE = True, DEPTH = depth + 1)
            except: json_res = {}
            try: yaml_res = yamls(yaml_text, NOT_WITH_JSON = True, DEPTH = depth + 1)
            except: yaml_res = {}
            if bool(json_res) or bool(yaml_res): 
                return merge_json_and_yaml(json_res, yaml_res)
    YamlValidationException.throw("Not a JSON + Yaml")


def merge_json_and_yaml(json_res, yaml_res):
    """
    Merge JSON and Yaml Objects
    """

    res = {}
    if isinstance(json_res, dict) and isinstance(yaml_res, dict):
        res = json_res | yaml_res
    if isinstance(json_res, list) and isinstance(yaml_res, dict):
        if len(json_res) == 1: res = yaml_res | json_res[0]
        else: res = yaml_res | {"properties": json_res}
    if isinstance(json_res, dict) and isinstance(yaml_res, list):
        if len(yaml_res) == 1: res = json_res | yaml_res[0]
        else: res = json_res | {"data": yaml_res}
    if isinstance(json_res, list) and isinstance(yaml_res, list):
        res = {"properties": json_res, "data": yaml_res}
    if not bool(res): YamlValidationException.throw("Not a JSON + Yaml")
    return res


def set_inner_exceptions(outerException: Exception, innerException: Exception):
    """
    Set Inner Exceptions to curent
    """

    if not hasattr(outerException, 'InnerExceptions'):
        outerException.InnerExceptions = []
    elif not outerException.InnerExceptions: 
        outerException.InnerExceptions = []
    outerException.InnerExceptions.append(innerException)
    return outerException


################## EXCEPTIONS BLOCK ##################


class JsonBodyException(ValueError):
    """
    Exception returned by Server, Not JSON
    """
    
    @staticmethod
    def throw(msg: str):
        raise JsonBodyException(msg)


class YamlValidationException(ValueError):
    """
    Exception Returned by Yaml Parser
    """
    
    @staticmethod
    def throw(msg: str):
        raise YamlValidationException(msg)


class JsonValidationException(ValueError):
    """
    Exception Returned by JBad Parser
    """
    
    InnerExceptions = None
    Message = None
    Position = -1
    Symbol = None
    Text = None
    
    @staticmethod
    def throw(msg, txt, pos, InnerExceptions = None):
        if pos == len(txt): text = f"{msg} `({txt[-20:]}...)"
        elif pos > 1: text = f"{msg} `{txt[pos:pos+1]}` at pos {pos} (...{txt[max(0,pos-20):pos]}^{txt[pos:pos+1]}^{txt[pos+1:min(pos+20,len(txt))]}...)"
        else: text = f"{msg} `{txt[pos]}` at pos {pos} (^{txt[pos]}^{txt[pos+1:min(pos+20,len(txt))]}...)"
        err = JsonValidationException(text)
        err.Message = text
        err.Position = pos
        err.Symbol = txt[pos:pos+1]
        err.Text = txt
        err.InnerExceptions = InnerExceptions
        raise err

