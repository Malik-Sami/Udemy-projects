MORSE_CODE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',
    '/': '-..-.',  '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
    ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
    '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
}

MORSE_TO_TEXT = {v: k for k, v in MORSE_CODE.items()}


def text_to_morse(text: str) -> str:
    text = text.upper()
    try:
        return ' '.join(MORSE_CODE[ch] for ch in text)
    except KeyError as e:
        raise ValueError(f"Unsupported character: {e.args[0]!r}") from None


def morse_to_text(morse: str) -> str:
    words = morse.strip().split(' / ')
    decoded_words = []
    for word in words:
        letters = word.strip().split()
        try:
            decoded_words.append(''.join(MORSE_TO_TEXT[code] for code in letters))
        except KeyError as e:
            raise ValueError(f"Unsupported code: {e.args[0]!r}") from None
    return ' '.join(decoded_words)


def main():
    print("Morse Code Converter")
    print("1. Text -> Morse")
    print("2. Morse -> Text")
    print("3. Quit")

    while True:
        choice = input("\nChoose an option (1/2/3): ").strip()

        if choice == '1':
            text = input("Enter text: ")
            try:
                print("Morse:", text_to_morse(text))
            except ValueError as e:
                print("Error:", e)

        elif choice == '2':
            morse = input("Enter Morse code (letters space-separated, '/' between words): ")
            try:
                print("Text:", morse_to_text(morse))
            except ValueError as e:
                print("Error:", e)

        elif choice == '3':
            print("Goodbye!")
            break

        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()

# I approached this project by first structuring a comprehensive lookup dictionary and dynamically generating its reverse for two-way translation, keeping the core conversion functions separate from the user CLI. Encoding text to Morse was straightforward, while tokenizing Morse back into readable text with proper spacing and handling unsupported characters proved to be the trickiest part. My biggest learning was the importance of clear delimiters when parsing serialized data and how dictionary comprehensions can prevent duplicate data errors. For my next project, I want to implement automated unit tests from the start for edge cases, and if I were to tackle this again, I would add audio playback for the dots and dashes alongside command-line argument support to make it a more interactive and versatile tool.
