#!/usr/bin/env python3
"""
Setup script for Verisure Rasa Demo
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Instalando dependencias...")
    
    # Install from requirements.txt
    if not run_command("pip install -r requirements.txt", "Instalando dependencias de requirements.txt"):
        return False
    
    return True

def setup_database():
    """Setup database tables"""
    print("\n🗄️ Configurando base de datos...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️ Archivo .env no encontrado. Creando archivo de ejemplo...")
        if os.path.exists('env.example'):
            run_command("cp env.example .env", "Copiando archivo de configuración")
            print("📝 Por favor, edita el archivo .env con tus credenciales de base de datos")
        else:
            print("❌ Error: No se encontró env.example")
            return False
    
    # Run database setup
    if not run_command("python database_config.py", "Configurando tablas de base de datos"):
        return False
    
    return True

def train_model():
    """Train the Rasa model"""
    print("\n🤖 Entrenando modelo de Rasa...")
    
    if not run_command("rasa train", "Entrenando modelo"):
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Configurando Verisure Rasa Demo...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Error: No se pudieron instalar las dependencias")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Error: No se pudo configurar la base de datos")
        sys.exit(1)
    
    # Train model
    if not train_model():
        print("❌ Error: No se pudo entrenar el modelo")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Configuración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Inicia el servidor de acciones: rasa run actions")
    print("2. En otra terminal, inicia el servidor principal: rasa run")
    print("3. Prueba el bot: rasa shell")
    print("4. O ejecuta el script de prueba: python test_bot.py")

if __name__ == "__main__":
    main() 