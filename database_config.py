import os
import mysql.connector
from mysql.connector import Error

def create_database_and_tables():
    """Create database and tables for Verisure demo"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS verisure_demo")
            cursor.execute("USE verisure_demo")
            
            # Create customers table
            create_customers_table = """
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_customers_table)
            
            # Create invoices table
            create_invoices_table = """
            CREATE TABLE IF NOT EXISTS invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                invoice_number VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                issue_date DATE NOT NULL,
                due_date DATE NOT NULL,
                status ENUM('pending', 'paid', 'payment_scheduled', 'disputed') DEFAULT 'pending',
                payment_date DATE NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
            """
            cursor.execute(create_invoices_table)
            
            # Create interactions table
            create_interactions_table = """
            CREATE TABLE IF NOT EXISTS interactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255),
                customer_id INT,
                interaction_type VARCHAR(100),
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
            """
            cursor.execute(create_interactions_table)
            
            # Insert demo data
            insert_demo_data(cursor)
            
            connection.commit()
            print("Database and tables created successfully!")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_demo_data(cursor):
    """Insert demo data for testing"""
    # Insert demo customer
    insert_customer = """
    INSERT IGNORE INTO customers (id, name, email, phone) 
    VALUES (1, 'Dennis Kangme', 'dennis@example.com', '+56912345678')
    """
    cursor.execute(insert_customer)
    
    # Insert demo invoice
    insert_invoice = """
    INSERT IGNORE INTO invoices (customer_id, invoice_number, amount, issue_date, due_date, status)
    VALUES (1, 'INV-2025-001', 55000.00, '2025-05-01', '2025-05-23', 'pending')
    """
    cursor.execute(insert_invoice)

if __name__ == "__main__":
    create_database_and_tables() 