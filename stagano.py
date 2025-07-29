import wave
import base64

def extract_hidden_hash(audio_path):
    """Extracts the license hash hidden in the audio file."""
    with wave.open(audio_path, 'rb') as audio:
        frames = bytearray(audio.readframes(audio.getnframes()))

    # Extract bits from LSB
    binary_data = ''.join(str(sample & 1) for sample in frames[:len(frames) // 8])

    # Convert binary to string
    byte_chunks = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    extracted_text = ''.join(chr(int(byte, 2)) for byte in byte_chunks)

    # Find EOF marker
    end_marker = extracted_text.find("EOF")
    if end_marker != -1:
        extracted_text = extracted_text[:end_marker]

    # First 8 chars = hash (short), rest = Base64 encoded full hash
    short_hash = extracted_text[:8]
    encoded_hash = extracted_text[8:]

    try:
        full_hash = base64.b64decode(encoded_hash).decode('utf-8')
    except Exception:
        full_hash = None

    return short_hash, full_hash
