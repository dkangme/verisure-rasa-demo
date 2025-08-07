#!/usr/bin/env python3
"""
Test script for Verisure Rasa Demo
"""

import requests
import json
import time

def test_bot_conversation():
    """Test the bot with a sample conversation"""
    
    # Bot endpoint
    bot_url = "http://localhost:5005/webhooks/rest/webhook"
    
    # Test conversation flow
    test_messages = [
        "hola",
        "sí",
        "puedo pagar",
        "mañana",
        "ya pagué"
    ]
    
    session_id = "test_session_123"
    
    print("🤖 Iniciando prueba del chatbot Verisure...")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n👤 Usuario: {message}")
        
        # Send message to bot
        payload = {
            "sender": session_id,
            "message": message
        }
        
        try:
            response = requests.post(bot_url, json=payload)
            if response.status_code == 200:
                bot_responses = response.json()
                for response in bot_responses:
                    print(f"🤖 Bot: {response.get('text', 'No response')}")
            else:
                print(f"❌ Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se puede conectar al bot. Asegúrate de que esté ejecutándose.")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        time.sleep(1)  # Small delay between messages
    
    print("\n" + "=" * 50)
    print("✅ Prueba completada!")

def test_database_connection():
    """Test database connection"""
    try:
        import mysql.connector
        from database_config import get_database_connection
        
        print("\n🔍 Probando conexión a base de datos...")
        
        connection = get_database_connection()
        if connection and connection.is_connected():
            print("✅ Conexión a base de datos exitosa!")
            connection.close()
        else:
            print("❌ Error: No se pudo conectar a la base de datos")
    except ImportError:
        print("❌ Error: mysql-connector-python no está instalado")
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")

if __name__ == "__main__":
    print("🚀 Verisure Rasa Demo - Test Suite")
    print("=" * 50)
    
    # Test database connection
    test_database_connection()
    
    # Test bot conversation
    test_bot_conversation()
    
    print("\n📋 Instrucciones:")
    print("1. Asegúrate de que el servidor de acciones esté ejecutándose: rasa run actions")
    print("2. Asegúrate de que el servidor principal esté ejecutándose: rasa run")
    print("3. Ejecuta este script para probar el bot") 