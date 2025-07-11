import datetime

def log_message(message, filename="app_log.txt"):
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

if __name__ == "__main__":
    log_message("Este é um teste de log.")
    log_message("Outra mensagem de log.")


