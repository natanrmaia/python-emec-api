from unicodedata    import normalize
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