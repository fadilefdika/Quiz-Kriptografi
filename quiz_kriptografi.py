import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# Vigenere chiper
def vigenere_encrypt(text, key):
    result = ""
    key_length = len(key)
    for i, char in enumerate(text):
        if char.isalpha():
            shift = ord(key[i % key_length].upper()) - ord('A')
            if char.isupper():
                result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                result += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
        else:
            result += char
    return result

def vigenere_decrypt(text, key):
    result = ""
    key_length = len(key)
    for i, char in enumerate(text):
        if char.isalpha():
            shift = ord(key[i % key_length].upper()) - ord('A')
            if char.isupper():
                result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            else:
                result += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
        else:
            result += char
    return result


# Playfair chiper
def generate_playfair_matrix(key):
    key = key.upper().replace("J", "I")
    matrix = []
    used_chars = set()
    
    for char in key + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in used_chars:
            matrix.append(char)
            used_chars.add(char)
    
    return [matrix[i:i+5] for i in range(0, 25, 5)]

def find_in_matrix(matrix, char):
    for i, row in enumerate(matrix):
        if char in row:
            return i, row.index(char)
    return -1, -1

def prepare_text(text):
    text = text.upper().replace("J", "I")
    prepared = ""
    
    i = 0
    while i < len(text):
        a = text[i]
        b = text[i + 1] if i + 1 < len(text) else 'X'
        
        if a == b:
            prepared += a + 'X'
            i += 1
        else:
            prepared += a + b
            i += 2
    
    if len(prepared) % 2 != 0:
        prepared += 'X'
    
    return prepared

def playfair_encrypt(text, key):
    matrix = generate_playfair_matrix(key)
    text = prepare_text(text)
    
    result = ""
    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        row1, col1 = find_in_matrix(matrix, a)
        row2, col2 = find_in_matrix(matrix, b)
        
        if row1 == row2:
            result += matrix[row1][(col1 + 1) % 5] + matrix[row2][(col2 + 1) % 5]
        elif col1 == col2:
            result += matrix[(row1 + 1) % 5][col1] + matrix[(row2 + 1) % 5][col2]
        else:
            result += matrix[row1][col2] + matrix[row2][col1]
    
    return result

def playfair_decrypt(text, key):
    if len(text) % 2 != 0:
        text += 'X'
    
    matrix = generate_playfair_matrix(key)
    
    result = ""
    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        row1, col1 = find_in_matrix(matrix, a)
        row2, col2 = find_in_matrix(matrix, b)
        
        if row1 == row2:
            result += matrix[row1][(col1 - 1) % 5] + matrix[row2][(col2 - 1) % 5]
        elif col1 == col2:
            result += matrix[(row1 - 1) % 5][col1] + matrix[(row2 - 1) % 5][col2]
        else:
            result += matrix[row1][col2] + matrix[row2][col1]
    
    return result


# Hill 
def matrix_vector_multiply(matrix, vector, mod):
    return [(sum(matrix[i][j] * vector[j] for j in range(3)) % mod) for i in range(3)]

def matrix_multiply(a, b, mod):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) % mod for j in range(3)] for i in range(3)]

def matrix_inverse(matrix, mod):
    det = (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
           - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
           + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])) % mod
    
    det_inv = pow(det, -1, mod)
    
    adj = [
        [(matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) % mod,
         (matrix[0][2] * matrix[2][1] - matrix[0][1] * matrix[2][2]) % mod,
         (matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1]) % mod],
        [(matrix[1][2] * matrix[2][0] - matrix[1][0] * matrix[2][2]) % mod,
         (matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]) % mod,
         (matrix[0][2] * matrix[1][0] - matrix[0][0] * matrix[1][2]) % mod],
        [(matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]) % mod,
         (matrix[0][1] * matrix[2][0] - matrix[0][0] * matrix[2][1]) % mod,
         (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % mod]
    ]
    
    return [[((det_inv * adj[i][j]) % mod) for j in range(3)] for i in range(3)]

def hill_encrypt(text, key):
    while len(text) % 3 != 0:
        text += 'x'

    key_matrix = [[ord(key[i*3+j]) - ord('a') for j in range(3)] for i in range(3)]
    
    ciphertext = ""
    for i in range(0, len(text), 3):
        block = [ord(c) - ord('a') for c in text[i:i+3]]
        encrypted = matrix_vector_multiply(key_matrix, block, 26)
        ciphertext += ''.join([chr(c % 26 + ord('A')) for c in encrypted])
    
    return ciphertext

def hill_decrypt(text, key):
    key_matrix = [[ord(key[i*3+j]) - ord('a') for j in range(3)] for i in range(3)]
    
    key_inverse = matrix_inverse(key_matrix, 26)
    
    plaintext = ""
    for i in range(0, len(text), 3):
        block = [ord(c) - ord('A') for c in text[i:i+3]]
        decrypted = matrix_vector_multiply(key_inverse, block, 26)
        plaintext += ''.join([chr(c % 26 + ord('a')) for c in decrypted])
 
    return plaintext

class CipherGUI:
    def __init__(self, master):
        self.master = master
        master.title("Aplikasi Cipher")
        master.geometry("600x500")

        # Cipher method selection
        ttk.Label(master, text="Pilih metode cipher:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.cipher_method = ttk.Combobox(master, values=["Vigenere", "Playfair", "Hill"])
        self.cipher_method.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.cipher_method.set("Vigenere")

        # Input source selection
        ttk.Label(master, text="Pilih sumber input:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.input_source = ttk.Combobox(master, values=["Teks", "File"])
        self.input_source.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.input_source.set("Teks")
        self.input_source.bind("<<ComboboxSelected>>", self.toggle_input_method)

        # Text input
        self.text_input = ttk.Entry(master, width=50)
        self.text_input.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # File input
        self.file_path = tk.StringVar()
        self.file_input = ttk.Entry(master, textvariable=self.file_path, state="disabled", width=40)
        self.file_input.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.file_button = ttk.Button(master, text="Pilih File", command=self.choose_file, state="disabled")
        self.file_button.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # Key input
        ttk.Label(master, text="Masukkan kunci:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.key_input = ttk.Entry(master, width=50)
        self.key_input.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

        # Operation selection
        ttk.Label(master, text="Pilih operasi:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.operation = ttk.Combobox(master, values=["Enkripsi", "Dekripsi"])
        self.operation.grid(row=5, column=1, sticky="ew", padx=10, pady=5)
        self.operation.set("Enkripsi")

        # Process button
        self.process_button = ttk.Button(master, text="Proses", command=self.process_cipher)
        self.process_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Result display
        ttk.Label(master, text="Hasil:").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.result_display = tk.Text(master, height=10, width=50, wrap=tk.WORD)
        self.result_display.grid(row=8, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        # Configure grid
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(8, weight=1)

    def toggle_input_method(self, event=None):
        if self.input_source.get() == "Teks":
            self.text_input.config(state="normal")
            self.file_input.config(state="disabled")
            self.file_button.config(state="disabled")
        else:
            self.text_input.config(state="disabled")
            self.file_input.config(state="normal")
            self.file_button.config(state="normal")

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_path.set(file_path)

    def process_cipher(self):
        method = self.cipher_method.get()
        key = self.key_input.get()
        operation = self.operation.get()

        if self.input_source.get() == "Teks":
            text = self.text_input.get()
        else:
            if not self.file_path.get():
                messagebox.showerror("Error", "Pilih file terlebih dahulu!")
                return
            with open(self.file_path.get(), 'r') as file:
                text = file.read().replace('\n', '').strip()

        if not text or not key:
            messagebox.showerror("Error", "Masukkan teks dan kunci!")
            return

        if method == "Vigenere":
            result = vigenere_encrypt(text, key) if operation == "Enkripsi" else vigenere_decrypt(text, key)
        elif method == "Playfair":
            result = playfair_encrypt(text, key) if operation == "Enkripsi" else playfair_decrypt(text, key)
        elif method == "Hill":
            result = hill_encrypt(text, key) if operation == "Enkripsi" else hill_decrypt(text, key)
        else:
            messagebox.showerror("Error", "Metode cipher tidak valid!")
            return

        self.result_display.delete(1.0, tk.END)
        self.result_display.insert(tk.END, result)

if __name__ == "__main__":
    root = tk.Tk()
    gui = CipherGUI(root)
    root.mainloop()