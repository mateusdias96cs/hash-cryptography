import os
import hashlib
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import difflib

# Funções de hashing
def gerar_hash(arquivo, algoritmo="sha256"):
    h = hashlib.new(algoritmo)
    with open(arquivo, "rb") as f:
        for bloco in iter(lambda: f.read(4096), b""):
            h.update(bloco)
    return h.hexdigest()

def salvar_hashes(pasta, algoritmo="sha256"):
    hashes = {}
    for root, dirs, files in os.walk(pasta):
        for nome in files:
            caminho = os.path.join(root, nome)
            try:
                hashes[caminho] = gerar_hash(caminho, algoritmo)
            except Exception as e:
                print(f"Erro ao processar {caminho}: {e}")
    with open(os.path.join(pasta, "hashes.txt"), "w", encoding="utf-8") as f:
        for caminho, h in hashes.items():
            f.write(f"{caminho}|{h}\n")
    messagebox.showinfo("Sucesso", f"Hashes ({algoritmo}) gerados e salvos em hashes.txt")

def comparar_texto(caminho, backup_path):
    try:
        with open(backup_path, "r", encoding="utf-8") as f1, open(caminho, "r", encoding="utf-8") as f2:
            conteudo1 = f1.readlines()
            conteudo2 = f2.readlines()
        diff = difflib.unified_diff(conteudo1, conteudo2, fromfile="Original", tofile="Atual")
        return "".join(diff)
    except Exception:
        return "Não foi possível comparar conteúdo (não é texto ou houve erro)."

def verificar_integridade(pasta, algoritmo="sha256"):
    try:
        with open(os.path.join(pasta, "hashes.txt"), "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo hashes.txt não encontrado. Gere os hashes primeiro.")
        return

    alterados = []
    log_path = os.path.join(pasta, "log_integridade.txt")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n--- Verificação em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

        for linha in linhas:
            caminho, hash_original = linha.strip().split("|")
            if os.path.exists(caminho):
                hash_atual = gerar_hash(caminho, algoritmo)
                if hash_atual != hash_original:
                    alterados.append((caminho, hash_original, hash_atual))
                    log.write(f"ALTERADO: {caminho}\n")
                    log.write(f"  Hash original: {hash_original}\n")
                    log.write(f"  Hash atual:    {hash_atual}\n")
            else:
                alterados.append((caminho, "REMOVIDO", "N/A"))
                log.write(f"REMOVIDO: {caminho}\n")

    # Janela moderna de resultados
    resultado_janela = ctk.CTkToplevel()
    resultado_janela.title("Resultado da Verificação")
    resultado_janela.geometry("800x500")

    texto = ctk.CTkTextbox(resultado_janela, width=780, height=460)
    texto.pack(padx=10, pady=10)

    if alterados:
        texto.insert("end", "⚠️ Arquivos alterados/removidos:\n\n")
        for caminho, hash_original, hash_atual in alterados:
            texto.insert("end", f"Arquivo: {caminho}\n")
            texto.insert("end", f"  Hash original: {hash_original}\n")
            texto.insert("end", f"  Hash atual:    {hash_atual}\n\n")

            if caminho.lower().endswith((".txt", ".py", ".csv", ".log")):
                diff = comparar_texto(caminho, caminho)  # precisa de backup original
                texto.insert("end", "Diferenças detectadas:\n")
                texto.insert("end", diff + "\n\n")

        texto.insert("end", f"Detalhes também salvos em: {log_path}\n")
    else:
        texto.insert("end", "✅ Todos os arquivos estão íntegros!\n")
        texto.insert("end", f"Log atualizado em: {log_path}\n")

    texto.configure(state="disabled")

# Interface moderna
ctk.set_appearance_mode("dark")  # "light" ou "dark"
ctk.set_default_color_theme("blue")  # temas: "blue", "green", "dark-blue"

root = ctk.CTk()
root.title("Verificador de Integridade 2025")
root.geometry("400x250")

algoritmo_var = ctk.StringVar(value="sha256")
opcoes = ["md5", "sha1", "sha256", "sha512"]

menu_algoritmo = ctk.CTkOptionMenu(root, variable=algoritmo_var, values=opcoes)
menu_algoritmo.pack(pady=20)

btn_gerar = ctk.CTkButton(root, text="Gerar Hashes da Pasta", command=lambda: salvar_hashes(filedialog.askdirectory(), algoritmo_var.get()))
btn_gerar.pack(pady=10)

btn_verificar = ctk.CTkButton(root, text="Verificar Integridade da Pasta", command=lambda: verificar_integridade(filedialog.askdirectory(), algoritmo_var.get()))
btn_verificar.pack(pady=10)

root.mainloop()
