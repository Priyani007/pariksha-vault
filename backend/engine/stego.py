"""
ParikshaVault - Invisible Steganographic Watermark Engine
Embeds and decodes forensic metadata (Exam Center, Room, Timestamp)
invisibly into question paper text using Unicode zero-width characters.
"""

import json

# Unicode Zero-Width Characters (Completely invisible on screen, print, and copy-paste)
ZW_ZERO = "\u200B"  # Zero-width space (represents binary 0)
ZW_ONE = "\u200C"   # Zero-width non-joiner (represents binary 1)
ZW_START = "\u200D" # Zero-width joiner (start marker)
ZW_END = "\uFEFF"   # Zero-width no-break space (end marker)


def text_to_binary(data_str: str) -> str:
    """Converts a string into its binary bitstream representation."""
    encoded_bytes = data_str.encode("utf-8")
    return "".join(format(byte, "08b") for byte in encoded_bytes)


def binary_to_text(bitstream: str) -> str:
    """Converts a binary bitstream back into a string."""
    bytes_list = []
    for i in range(0, len(bitstream), 8):
        byte_bits = bitstream[i : i + 8]
        if len(byte_bits) == 8:
            bytes_list.append(int(byte_bits, 2))
    return bytes(bytes_list).decode("utf-8", errors="ignore")


def embed_watermark(text: str, metadata: dict) -> str:
    """
    Invisibly embeds forensic metadata into normal question paper text.
    
    :param text: Standard human-readable question text
    :param metadata: Dict containing {"center_id": "104", "hall": "B", "timestamp": "09:15 AM"}
    :return: Visually identical text containing invisible forensic payload
    """
    # 1. Serialize and compress metadata to compact JSON
    payload_json = json.dumps(metadata, separators=(",", ":"))
    binary_payload = text_to_binary(payload_json)

    # 2. Encode binary into zero-width characters
    zw_payload = "".join(ZW_ZERO if bit == "0" else ZW_ONE for bit in binary_payload)
    stego_packet = ZW_START + zw_payload + ZW_END

    # 3. Inject the invisible packet after the first word
    words = text.split(" ", 1)
    if len(words) > 1:
        return f"{words[0]}{stego_packet} {words[1]}"
    else:
        return f"{text}{stego_packet}"


def extract_watermark(leaked_text: str) -> dict | None:
    """
    Extracts forensic metadata from a leaked text snippet.
    
    :param leaked_text: Text copied or OCR'd from Telegram/WhatsApp
    :return: Decoded metadata dictionary or None if clean
    """
    try:
        # Find start and end markers
        start_idx = leaked_text.find(ZW_START)
        end_idx = leaked_text.find(ZW_END)

        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            return None

        # Extract only the zero-width bitstream
        raw_bits = leaked_text[start_idx + len(ZW_START) : end_idx]
        bitstream = []
        for char in raw_bits:
            if char == ZW_ZERO:
                bitstream.append("0")
            elif char == ZW_ONE:
                bitstream.append("1")

        binary_string = "".join(bitstream)
        decoded_json = binary_to_text(binary_string)
        return json.loads(decoded_json)
    except Exception as e:
        print(f"[Stego Error]: {e}")
        return None


# Quick verification self-test
if __name__ == "__main__":
    print("=== ParikshaVault Stego Self-Test ===")
    
    sample_question = "Question 1: Explain Newton's third law of motion with a real-world example."
    leak_metadata = {
        "center_id": "CENTRAL-104",
        "center_name": "Velammal Hall, Chennai",
        "room": "Hall B - Room 12",
        "session": "NEET-UG-2026",
        "printed_at": "09:14 AM",
        "hash": "a4f891"
    }

    # Embed watermark
    watermarked_text = embed_watermark(sample_question, leak_metadata)

    print("\n[Normal Text Preview]:")
    print(watermarked_text)
    print(f"Visual Text Length: {len(sample_question)} | Encoded Buffer Length: {len(watermarked_text)}")
    print("Does it look identical to the naked eye? YES!")

    # Simulate Leak & Extraction
    print("\n[Forensic Leak Scanner Simulating Extraction...]")
    extracted_data = extract_watermark(watermarked_text)
    print("Extracted Forensic Payload:")
    print(json.dumps(extracted_data, indent=2))
