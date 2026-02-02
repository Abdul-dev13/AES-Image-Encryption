import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from Crypto.Cipher import AES

IV = b"This is an IV456"  # 16 bytes for AES-CBC

# ---------------- ENCRYPT ----------------
def encrypt_image(image_path, password):
    folder = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    data = "".join(["{}{}{}".format(p[0]+100, p[1]+100, p[2]+100) for p in pixels])
    data += "h{}hw{}w".format(img.height, img.width)

    while len(data) % 16 != 0:
        data += "n"

    key = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, IV)
    encrypted = cipher.encrypt(data.encode())

    encrypted_file = os.path.join(folder, filename + ".crypt")
    with open(encrypted_file, "wb") as f:
        f.write(encrypted)

    messagebox.showinfo("Success", f"Image Encrypted Successfully!\nSaved as:\n{encrypted_file}")

# ---------------- DECRYPT ----------------
def decrypt_image(cipher_path, password):
    folder = os.path.dirname(cipher_path)
    with open(cipher_path, "rb") as f:
        ciphertext = f.read()

    key = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, IV)
    decrypted = cipher.decrypt(ciphertext).decode(errors="ignore")
    decrypted = decrypted.replace("n", "")

    try:
        height = int(decrypted.split("h")[1])
        width = int(decrypted.split("w")[1])
    except:
        messagebox.showerror("Error", "Incorrect password or corrupted file!")
        return

    decrypted = decrypted.replace(f"h{height}h", "")
    decrypted = decrypted.replace(f"w{width}w", "")

    pixels = []
    for i in range(0, len(decrypted), 9):
        r = int(decrypted[i:i+3]) - 100
        g = int(decrypted[i+3:i+6]) - 100
        b = int(decrypted[i+6:i+9]) - 100
        pixels.append((r, g, b))

    output_file = os.path.join(folder, "decrypted_" + os.path.splitext(os.path.basename(cipher_path))[0] + ".png")
    img = Image.new("RGB", (width, height))
    img.putdata(pixels)
    img.save(output_file)

    # Open automatically in Preview
    os.system(f'open "{output_file}"')

    messagebox.showinfo("Success", f"Image Decrypted Successfully!\nSaved as:\n{output_file}")

# ---------------- GUI ----------------
def encrypt_button():
    pwd = password_entry.get()
    if not pwd:
        messagebox.showwarning("Alert", "Enter password")
        return
    file = filedialog.askopenfilename(title="Select Image to Encrypt")
    if file:
        encrypt_image(file, pwd)

def decrypt_button():
    pwd = password_entry.get()
    if not pwd:
        messagebox.showwarning("Alert", "Enter password")
        return
    file = filedialog.askopenfilename(title="Select Encrypted File")
    if file:
        decrypt_image(file, pwd)

# ---------------- MAIN GUI ----------------
root = tk.Tk()
root.title("AES Image Encryption & Decryption (Python 3)")
root.geometry("400x200")

tk.Label(root, text="Enter Password").pack(pady=5)
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

tk.Button(root, text="Encrypt Image", command=encrypt_button,
          width=30, height=2).pack(pady=10)

tk.Button(root, text="Decrypt Image", command=decrypt_button,
          width=30, height=2).pack(pady=10)

root.mainloop()
