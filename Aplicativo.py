import customtkinter as ctk
from tkinter import messagebox
from Back import confirmacao_login  # Ajuste conforme seu módulo
from front import abrir_gestor

ctk.set_appearance_mode("dark")

janela_login = ctk.CTk()
janela_login.title('Gestor-X')
janela_login.geometry("500x400")

ctk.CTkLabel(
    janela_login,
    text='Tela de Acesso',
    font=('Arial', 20, 'bold')
).pack(pady=30)

# LOGIN
ctk.CTkLabel(
    janela_login,
    text="Login:",
    font=('Arial', 15)
).pack()

login_entry = ctk.CTkEntry(janela_login, width=200)
login_entry.pack(pady=5)

# SENHA
ctk.CTkLabel(
    janela_login,
    text="Senha:",
    font=('Arial', 15)
).pack()

senha_entry = ctk.CTkEntry(janela_login, width=200, show="*")
senha_entry.pack(pady=5)

# LABEL DE ERRO
erro_label = ctk.CTkLabel(janela_login, text="", font=('Arial', 12), text_color="red")
erro_label.pack()

# FUNÇÃO DE LOGIN
def verificar_login():
    usuario = login_entry.get()
    senha_digitada = senha_entry.get()

    if not usuario or not senha_digitada:
        erro_label.configure(text="Preencha todos os campos!")
        return

    try:
        resultado = confirmacao_login(usuario, senha_digitada)

        if resultado:
            erro_label.configure(text="")
            print(f"Login realizado com sucesso! Bem-vindo, {resultado[1]}")
            janela_login.withdraw()
            abrir_gestor(janela_login)
        else:
            erro_label.configure(text="❌ Login ou senha incorretos")
            login_entry.delete(0, "end")
            senha_entry.delete(0, "end")
    except Exception as e:
        erro_label.configure(text=f"❌ Erro ao conectar: {str(e)}")
        print(f"Erro: {e}")

# BOTÃO
ctk.CTkButton(
    janela_login,
    text="Entrar",
    command=verificar_login,
    width=200,
    height=40,
    font=('Arial', 14)
).pack(pady=20)

janela_login.mainloop()