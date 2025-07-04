import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import requests

def ambil_kurs_online():
    try:
        url = "https://open.er-api.com/v6/latest/IDR"
        response = requests.get(url)
        data = response.json()
        if data["result"] == "success":
            rates = data["rates"]
            return {
                kode: {
                    "nama": kode,
                    "nilai": 1 / rate if rate != 0 else 0
                }
                for kode, rate in rates.items()
            }
    except:
        print("❌ Tidak bisa ambil kurs dari API.")
    return None

data_kurs = ambil_kurs_online()
sumber_kurs = "REAL-TIME"

if not data_kurs:
    from data_kurs_default import data_kurs_default
    data_kurs = data_kurs_default
    sumber_kurs = "LOKAL (DEFAULT)"

print(f"📡 Kurs yang digunakan: {sumber_kurs}")

class MataUang:
    def __init__(self, kode, nama, nilai_terhadap_idr):
        self.kode = kode
        self.nama = nama
        self.nilai_terhadap_idr = nilai_terhadap_idr

class KonverterMataUang:
    def __init__(self, daftar_mata_uang):
        self.daftar = daftar_mata_uang

    def konversi(self, jumlah, asal_kode, tujuan_kode):
        asal = self.daftar[asal_kode]
        tujuan = self.daftar[tujuan_kode]
        jumlah_idr = jumlah * asal.nilai_terhadap_idr
        hasil = jumlah_idr / tujuan.nilai_terhadap_idr
        return hasil

class AplikasiKursGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator Kurs Mata Uang")
        self.root.geometry("400x400")

        self.daftar_mata_uang = {}
        for kode in sorted(data_kurs.keys()):
            data = data_kurs[kode]
            self.daftar_mata_uang[kode] = MataUang(kode, data["nama"], data["nilai"])

        self.konverter = KonverterMataUang(self.daftar_mata_uang)

        # Inisialisasi gambar bendera kosong
        self.flag_images = {}
        self.setup_gui()
        self.root.bind("<Return>", lambda event: self.konversi_uang()) # Tambahan tombol enter untuk konversi

    def setup_gui(self):
        # Input jumlah
        tk.Label(self.root, text="Jumlah:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_jumlah = tk.Entry(self.root)
        self.entry_jumlah.grid(row=0, column=1, padx=10, pady=5)

        # Dropdown asal
        tk.Label(self.root, text="Dari Mata Uang:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.combo_asal = ttk.Combobox(self.root, values=list(self.daftar_mata_uang.keys()), state="readonly")
        self.combo_asal.grid(row=1, column=1, padx=10, pady=5)
        self.combo_asal.current(0)
        self.combo_asal.bind("<<ComboboxSelected>>", self.update_bendera_asal)

        self.label_flag_asal = tk.Label(self.root)
        self.label_flag_asal.grid(row=1, column=2)

        # Dropdown tujuan
        tk.Label(self.root, text="Ke Mata Uang:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.combo_tujuan = ttk.Combobox(self.root, values=list(self.daftar_mata_uang.keys()), state="readonly")
        self.combo_tujuan.grid(row=2, column=1, padx=10, pady=5)
        self.combo_tujuan.current(1)
        self.combo_tujuan.bind("<<ComboboxSelected>>", self.update_bendera_tujuan)

        self.label_flag_tujuan = tk.Label(self.root)
        self.label_flag_tujuan.grid(row=2, column=2)

        # Tombol konversi
        self.btn_konversi = tk.Button(self.root, text="Konversi", command=self.konversi_uang)
        self.btn_konversi.grid(row=3, column=0, columnspan=3, pady=10)

        # Tombol clear
        self.btn_clear = tk.Button(self.root, text="Clear", command=self.clear_hasil)
        self.btn_clear.grid(row=5, column=0, columnspan=3, pady=5)

        # Label hasil
        self.text_hasil = tk.Text(self.root, height=10, width=45, state='disabled')
        self.text_hasil.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        # Tampilkan bendera awal
        self.update_bendera_asal()
        self.update_bendera_tujuan()

    def load_bendera(self, kode):
        # Ambil jalur absolut dari file png
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir,"flags",f"{kode.lower()}.png")
        print(f"🔍 Mencoba load: {path}")  # Tambahkan ini
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((40, 25))
            photo = ImageTk.PhotoImage(img)
            self.flag_images[kode] = photo
            return photo
        else:
            print(f"❌ Gagal menemukan gambar: {path}")  # Tambahkan ini
        return None


    def update_bendera_asal(self, event=None):
        kode = self.combo_asal.get()
        photo = self.load_bendera(kode)
        if photo:
            self.label_flag_asal.config(image=photo)
            self.label_flag_asal.image = photo
        else:
            self.label_flag_asal.config(image='')
            self.label_flag_asal.image = None

    def update_bendera_tujuan(self, event=None):
        kode = self.combo_tujuan.get()
        photo = self.load_bendera(kode)
        if photo:
            self.label_flag_tujuan.config(image=photo)
            self.label_flag_tujuan.image = photo
        else:
            self.label_flag_tujuan.config(image='')
            self.label_flag_tujuan.image = None

    def konversi_uang(self):
        try:
            jumlah = float(self.entry_jumlah.get())
            asal = self.combo_asal.get()
            tujuan = self.combo_tujuan.get()
            hasil = self.konverter.konversi(jumlah, asal, tujuan)
            hasil_teks = f"{jumlah:.2f} {asal} = {hasil:.2f} {tujuan}\n"

            self.text_hasil.config(state='normal')
            self.text_hasil.insert(tk.END, hasil_teks)
            self.text_hasil.config(state='disabled')
        except ValueError:
            self.text_hasil.config(state='normal')
            self.text_hasil.insert(tk.END, "Masukkan jumlah yang valid!\n")
            self.text_hasil.config(state='disabled')

    def clear_hasil(self):
        self.text_hasil.config(state='normal')
        self.text_hasil.delete("1.0", tk.END)
        self.text_hasil.config(state='disabled')

# Menjalankan aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiKursGUI(root)
    root.mainloop()
