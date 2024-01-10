from emecAPI.settings   import BASE_URL
from unicodedata        import normalize
import base64


def normalize_key(key: str) -> str:
    """
    Normalize a given key by removing leading and trailing whitespace and colons,
    converting it to lowercase, replacing spaces with underscores, removing parentheses,
    removing non-ascii characters, and decoding the string.

    Args:
        key (str): The key to be normalized.

    Returns:
        str: The normalized key.
    """
    text = key.strip(': ')                              # Remove leading and trailing whitespace and colons.
    text = text.lower()                                 # Convert to lowercase.
    text = text.replace(' ', '_')                       # Replace spaces with underscores.
    text = text.replace('(' , '').replace(')', '')      # Remove parentheses.

    normalized = normalize('NFKD', text)                # Normalize the string.
    normalized = normalized.encode('ascii', 'ignore')   # Remove non-ascii characters.
    normalized = normalized.decode('utf-8')             # Decode the string.

    return normalized

def convert_text_to_base64(text_str: str, encoding: str = 'utf-8') -> str:
    """
    Converts a text string to base64 encoding.

    Args:
        text (str): The text string to be converted.
        encoding (str, optional): The encoding to be used. Defaults to 'utf-8'.

    Returns:
        str: The base64 encoded string.
    """
    if text_str is None:
        return None

    text = str(text_str).encode(encoding)   # Encode the ID.
    text = base64.b64encode(text)           # Convert the ID to base64.
    text = text.decode(encoding)            # Decode the ID.

    return text

def convert_b64_to_text(b64_text: str, encoding: str = 'utf-8') -> str:
    """
    Converts a base64 encoded string to plain text.

    Args:
        b64_text (str): The base64 encoded string.
        encoding (str, optional): The encoding to use for decoding the base64 string. Defaults to 'utf-8'.

    Returns:
        str: The decoded plain text.
    """
    if b64_text is None:
        return None

    text = str(b64_text).encode(encoding)   # Encode the ID.
    text = base64.b64decode(text)           # Decode the ID.
    text = text.decode(encoding)            # Decode the ID.

    return text

def set_url(method: str, ies_id_b64: str, course_id_b64: str = None) -> str:

        base_url            = BASE_URL
        url_ies_prefix      = 'consulta-ies/'
        url_course_prefix   = 'consulta-curso/'
        url_ies_divisor     = '/d96957f455f6405d14c6542552b0f6eb/'
        url_course_divisor  = '/9f1aa921d96ca1df24a34474cc171f61/'
        url_suffix_list     = '/list/1000'

        match method:
            case 'ies':
                query   = 'index'
                url     = f'{url_ies_prefix}{query}{url_ies_divisor}{ies_id_b64}'
            case 'metrics':
                query   = 'listar-historico-indicadores-ies'
                url     = f'{url_ies_prefix}{query}{url_ies_divisor}{ies_id_b64}{url_suffix_list}'
            case 'regulatory_act':
                query   = 'listar-ato-regulatorio'
                url     = f'{url_ies_prefix}{query}{url_ies_divisor}{ies_id_b64}{url_suffix_list}'
            case 'mec_process':
                query   = 'listar-processo'
                url     = f'{url_ies_prefix}{query}{url_ies_divisor}{ies_id_b64}{url_suffix_list}'
            case 'campus':
                query   = 'listar-endereco'
                url     = f'{url_ies_prefix}{query}{url_ies_divisor}{ies_id_b64}{url_suffix_list}'
            case 'courses':
                query   = 'listar-curso'
                url     = f'{url_ies_prefix}{query}{url_ies_divisor}{ies_id_b64}{url_suffix_list}'
            case 'courses_details_info_general':
                query   = 'detalhe-curso'
                url     = f'{url_course_prefix}{query}{url_course_divisor}0/{ies_id_b64}/{course_id_b64}'
            case 'courses_details_detail':
                query   = 'detalhe-curso'
                url     = f'{url_course_prefix}{query}{url_course_divisor}1/{ies_id_b64}/{course_id_b64}'
            case _:
                return None

        return f'{base_url}{url}'

def clean_boolean_fields(value: str) -> bool:
    """Parse the boolean fields.

    Args:
        value (str): Value to be parsed.

    Returns:
        bool: Returns the parsed value.
    """

    if value is None:
        return None
    elif value.upper() in ['SIM', 'YES', 'S', 'Y', 'ATIVO', 'ATIVA']:
        return True
    elif value in ['NÃO', 'NO', 'N', 'INATIVO', 'INATIVA']:
        return False
    else:
        return value