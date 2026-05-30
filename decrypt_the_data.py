import json
import base64
import gzip
import zlib
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


# -------------------------
# Load JSON file
# -------------------------
def load_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


# -------------------------
# Decrypt single record
# -------------------------
def decrypt_record(encoded_str, key):
    import base64
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad

    raw = base64.b64decode(encoded_str)

    # 🔥 ASSUME CBC WITH IV PREFIX (MOST COMMON IN THESE TESTS)
    iv = raw[:16]
    ciphertext = raw[16:]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    decrypted = cipher.decrypt(ciphertext)

    try:
        decrypted = unpad(decrypted, AES.block_size)
    except:
        pass

    return decrypted.decode("utf-8", errors="ignore")
# -------------------------
# Decrypt full dataset
# -------------------------
def decrypt_dataset(records, key, mode=AES.MODE_ECB, iv=None):

    results = []

    for i, record in enumerate(records):
        try:
            plain = decrypt_record(record, key, mode, iv)
            results.append(plain)

        except Exception as e:
            print(f"Failed at index {i}: {e}")

    return results


# -------------------------
# Save output
# -------------------------
def save_output(data, output_file):
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":

    # Load encrypted dataset
    records = load_data("data/raw/dataset.json")

    # IMPORTANT: replace with real API key
    key = b"1234567890123456"

    decrypted = decrypt_dataset(records, key)

    save_output(decrypted, "data/decrypted/decrypted.json")

    print("Decryption completed. Total records:", len(decrypted))