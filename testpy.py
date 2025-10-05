import requests
import json
import getpass

# --- CONFIGURACIÓN ---
# Asegúrate de que esta URL base coincida con la configuración de tu proyecto
# La hemos cambiado a '/api/chat/' para reflejar la nueva estructura
BASE_URL = "http://127.0.0.1:8000/api/chat" 

# Variable global para almacenar el token de acceso después de iniciar sesión
access_token = None

def register_user():
    """Pide datos y registra un nuevo usuario."""
    print("\n--- 1. Registro de Nuevo Usuario ---")
    username = input("Elige un nombre de usuario: ")
    password = getpass.getpass("Elige una contraseña: ")
    try:
        # Apunta al nuevo endpoint de registro
        r = requests.post(f"{BASE_URL}/register/", data={'username': username, 'password': password})
        if r.status_code == 201:
            print("✅ ¡Usuario registrado exitosamente!")
        else:
            print(f"❌ Error al registrar: {r.status_code} {r.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

def login_user():
    """Pide credenciales e inicia sesión para obtener un token JWT."""
    global access_token
    print("\n--- 2. Inicio de Sesión ---")
    username = input("Nombre de usuario: ")
    password = getpass.getpass("Contraseña: ")
    try:
        # Apunta al endpoint de obtención de token
        r = requests.post(f"{BASE_URL}/token/", data={'username': username, 'password': password})
        if r.status_code == 200:
            access_token = r.json()['access']
            print("✅ ¡Inicio de sesión exitoso! Token obtenido.")
        else:
            print(f"❌ Error de credenciales.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

def create_new_session():
    """Crea una nueva sesión de chat vacía."""
    if not access_token:
        print("🛑 Necesitas iniciar sesión primero.")
        return
    
    print("\n--- 3. Creando nueva sesión de chat... ---")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        # Apunta al endpoint de creación de sesiones
        r = requests.post(f"{BASE_URL}/sessions/", headers=headers)
        if r.status_code == 201:
            session_id = r.json()['id']
            print(f"✅ ¡Nueva sesión de chat creada con ID: {session_id}!")
            # Inmediatamente después de crearla, iniciamos la conversación
            start_chatting(session_id)
        else:
            print(f"❌ Error al crear la sesión: {r.status_code} {r.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

def select_and_chat():
    """Muestra las sesiones existentes y permite al usuario elegir una para continuar."""
    if not access_token:
        print("🛑 Necesitas iniciar sesión primero.")
        return
        
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        r = requests.get(f"{BASE_URL}/sessions/", headers=headers)
        if r.status_code == 200:
            sessions = r.json()
            if not sessions:
                print("\nNo tienes ningún chat. ¡Crea uno nuevo!")
                return

            print(f"\n--- 4. Selecciona un chat para continuar ---")
            for idx, session in enumerate(sessions):
                print(f"  [{idx + 1}] Chat iniciado el {session['start_time']}")
            
            choice = input("Elige un número de chat: ")
            selected_idx = int(choice) - 1
            
            if 0 <= selected_idx < len(sessions):
                session_id = sessions[selected_idx]['id']
                # Una vez seleccionado, mostramos el historial e iniciamos el chat
                view_history(session_id)
                start_chatting(session_id)
            else:
                print("❌ Selección inválida.")
        else:
            print(f"❌ Error al listar las sesiones: {r.status_code}")
    except (requests.exceptions.RequestException, ValueError):
        print("❌ Error o entrada inválida.")

def start_chatting(session_id):
    """Bucle interactivo para enviar mensajes a una sesión específica."""
    print("\n--- Chateando (escribe 'salir' para terminar) ---")
    while True:
        user_message = input("Tú: ")
        if user_message.lower() == 'salir':
            break
        
        headers = {'Authorization': f'Bearer {access_token}'}
        payload = {'message_text': user_message}
        
        try:
            # Apunta al nuevo endpoint para enviar mensajes
            r = requests.post(f"{BASE_URL}/sessions/{session_id}/send_message/", headers=headers, json=payload)
            if r.status_code == 201:
                bot_response = r.json()
                print(f"Bot: {bot_response['message_text']}")
            else:
                print(f"❌ Error al enviar mensaje: {r.status_code} {r.json()}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")

def view_history(session_id):
    """Muestra el historial de un chat específico."""
    print(f"\n--- 5. Historial del Chat ID: {session_id} ---")
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        r = requests.get(f"{BASE_URL}/sessions/{session_id}/", headers=headers)
        if r.status_code == 200:
            details = r.json()
            for msg in details['messages']:
                print(f"  [{msg['sender'].capitalize()}]: {msg['message_text']}")
            print("="*20)
        else:
            print(f"❌ Error al ver el chat: {r.status_code} {r.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

def main():
    """Función principal que muestra el menú interactivo."""
    while True:
        print("\n======= CLIENTE DE CHAT-RAG =======")
        print("1. Registrar nuevo usuario")
        print("2. Iniciar sesión")
        print("3. Crear y empezar un nuevo chat")
        print("4. Continuar un chat existente")
        print("5. Salir")
        
        choice = input("Elige una opción: ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            create_new_session()
        elif choice == '4':
            select_and_chat()
        elif choice == '5':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida, intenta de nuevo.")

if __name__ == "__main__":
    main()