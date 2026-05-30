import json
import base64
import zlib
from pathlib import Path

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad



# -------------------------
# GET KEY FROM PLATFORM (IMPORTANT)
# -------------------------
def get_key(base_url, api_key):
    response = requests.get(
        f"{base_url}/api/v1/key",
        headers={"Authorization": f"Bearer {api_key}"}
    )

    response.raise_for_status()
    return response.json()


# -------------------------
# Decrypt single record
# Assumes:
# Base64( IV + CipherText )
# AES-CBC
# -------------------------
def decrypt_record(record, key, iv=None, mode="cbc"):
    """
    Handles AES decryption properly for assessment Layer 2
    """

    raw = base64.b64decode(record)

    key = key.encode() if isinstance(key, str) else key

    # -------------------------
    # CBC MODE (MOST LIKELY CASE)
    # -------------------------
    if mode.lower() == "cbc":

        # Case 1: IV provided separately from API
        if iv:
            cipher = AES.new(key, AES.MODE_CBC, iv.encode() if isinstance(iv, str) else iv)
            decrypted = cipher.decrypt(raw)

        # Case 2: IV is prefixed in ciphertext (VERY COMMON IN THESE TESTS)
        else:
            iv = raw[:16]
            ciphertext = raw[16:]

            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)

    # -------------------------
    # ECB MODE fallback
    # -------------------------
    else:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(raw)

    # -------------------------
    # Remove padding safely
    # -------------------------
    try:
        decrypted = unpad(decrypted, AES.block_size)
    except:
        pass

    # IMPORTANT: DO NOT blindly assume utf-8
    try:
        return decrypted.decode("utf-8")
    except:
        return decrypted

# -------------------------
# Decrypt full dataset
# -------------------------
def decrypt_dataset(records, key, iv=None, mode="cbc"):
    decrypted_data = []

    for i, record in enumerate(records):
        try:
            plain = decrypt_record(record, key, iv, mode)

            # only keep valid outputs
            if plain:
                decrypted_data.append(plain)

        except Exception as e:
            print(f"[FAILED] Record {i}: {e}")

    return decrypted_data

# -------------------------
# Save output
# -------------------------
def save_output(data, output_file):
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":

    BASE_URL = "https://your-api-url"
    API_KEY = "sa_xxx"

    # 1. Get dataset already loaded from Layer 1
    records = [...]  # your JSON-loaded dataset

    # 2. Get encryption key from platform
    key_data = get_key(BASE_URL, API_KEY)

    key = key_data.get("key")
    iv = key_data.get("iv")   # optional

    mode = key_data.get("mode", "cbc")

    # 3. Decrypt dataset
    decrypted = decrypt_dataset(records, key, iv, mode)

    print("Decrypted records:", len(decrypted))
    print("Sample:", decrypted[0] if decrypted else None)