#!/usr/bin/env python3
"""
Script para insertar datos de prueba para Mauricio Martínez
"""

import mysql.connector
import os
from datetime import date, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_database_connection():
    """Get database connection using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'verisure_demo')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def insert_mauricio_data():
    """Insert test data for Mauricio Martínez"""
    connection = get_database_connection()
    if not connection:
        print("No se pudo conectar a la base de datos")
        return
    
    cursor = connection.cursor()
    
    try:
        # Insertar cliente Mauricio Martínez
        insert_customer_query = """
        INSERT INTO customers (name, email, phone, created_at) 
        VALUES (%s, %s, %s, NOW())
        """
        customer_data = ("Mauricio Martínez", "mauricio.martinez@email.com", "+56912345678")
        
        cursor.execute(insert_customer_query, customer_data)
        customer_id = cursor.lastrowid
        print(f"✅ Cliente Mauricio Martínez insertado con ID: {customer_id}")
        
        # Obtener fecha actual para calcular fechas de facturas
        today = date.today()
        
        # Insertar facturas pendientes para Mauricio
        invoices_data = [
            {
                'invoice_number': 'INV-2025-001-MM',
                'amount': 75000.00,
                'issue_date': today - timedelta(days=45),
                'due_date': today - timedelta(days=15),
                'status': 'pending'
            },
            {
                'invoice_number': 'INV-2025-002-MM',
                'amount': 45000.00,
                'issue_date': today - timedelta(days=30),
                'due_date': today - timedelta(days=5),
                'status': 'pending'
            },
            {
                'invoice_number': 'INV-2025-003-MM',
                'amount': 120000.00,
                'issue_date': today - timedelta(days=15),
                'due_date': today + timedelta(days=10),
                'status': 'pending'
            },
            {
                'invoice_number': 'INV-2025-004-MM',
                'amount': 85000.00,
                'issue_date': today - timedelta(days=10),
                'due_date': today + timedelta(days=20),
                'status': 'pending'
            }
        ]
        
        insert_invoice_query = """
        INSERT INTO invoices (customer_id, invoice_number, amount, issue_date, due_date, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        
        for invoice in invoices_data:
            invoice_data = (
                customer_id,
                invoice['invoice_number'],
                invoice['amount'],
                invoice['issue_date'],
                invoice['due_date'],
                invoice['status']
            )
            cursor.execute(insert_invoice_query, invoice_data)
            print(f"✅ Factura {invoice['invoice_number']} insertada - ${invoice['amount']:,.0f}")
        
        # Insertar algunas facturas pagadas para mostrar historial
        paid_invoices = [
            {
                'invoice_number': 'INV-2024-015-MM',
                'amount': 65000.00,
                'issue_date': today - timedelta(days=90),
                'due_date': today - timedelta(days=60),
                'status': 'paid',
                'payment_date': today - timedelta(days=65)
            },
            {
                'invoice_number': 'INV-2024-016-MM',
                'amount': 95000.00,
                'issue_date': today - timedelta(days=75),
                'due_date': today - timedelta(days=45),
                'status': 'paid',
                'payment_date': today - timedelta(days=50)
            }
        ]
        
        for invoice in paid_invoices:
            invoice_data = (
                customer_id,
                invoice['invoice_number'],
                invoice['amount'],
                invoice['issue_date'],
                invoice['due_date'],
                invoice['status']
            )
            cursor.execute(insert_invoice_query, invoice_data)
            
            # Actualizar la factura con payment_date
            update_payment_query = """
            UPDATE invoices 
            SET payment_date = %s 
            WHERE invoice_number = %s
            """
            cursor.execute(update_payment_query, (invoice['payment_date'], invoice['invoice_number']))
            print(f"✅ Factura pagada {invoice['invoice_number']} insertada - ${invoice['amount']:,.0f}")
        
        connection.commit()
        print("\n🎉 Datos de prueba para Mauricio Martínez insertados exitosamente!")
        print(f"📊 Resumen:")
        print(f"   - Cliente: Mauricio Martínez (ID: {customer_id})")
        print(f"   - Facturas pendientes: {len(invoices_data)}")
        print(f"   - Facturas pagadas: {len(paid_invoices)}")
        print(f"   - Total pendiente: ${sum(inv['amount'] for inv in invoices_data):,.0f}")
        
    except mysql.connector.Error as err:
        print(f"❌ Error insertando datos: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🚀 Insertando datos de prueba para Mauricio Martínez...")
    insert_mauricio_data() 