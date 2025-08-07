from typing import Any, Dict, List, Text
import os
import mysql.connector
from datetime import datetime, timedelta
import re
import calendar

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher


class ActionExtractClientName(Action):
    def name(self) -> Text:
        return "action_extract_client_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        latest_message = tracker.latest_message.get('text', '').lower()
        
        # First, try to get the client_name from extracted entities
        entities = tracker.latest_message.get('entities', [])
        for entity in entities:
            if entity['entity'] == 'client_name':
                client_name = entity['value'].strip().title()
                self.log_interaction(tracker, "client_name_extracted_from_entity", client_name)
                return [SlotSet("client_name", client_name)]
        
        # If no entity found, try to extract name from the message using regex
        name_pattern = r'soy\s+([a-zA-Z\s]+)'
        match = re.search(name_pattern, latest_message)
        
        if match:
            client_name = match.group(1).strip().title()
        else:
            # Default to Dennis Kangme if no name found
            client_name = "Dennis Kangme"
        
        # Log the interaction
        self.log_interaction(tracker, "client_name_extracted_from_text", client_name)
        
        return [SlotSet("client_name", client_name)]


class ActionCheckIdentity(Action):
    def name(self) -> Text:
        return "action_check_identity"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get the latest message from the user
        latest_message = tracker.latest_message.get('text', '').lower()
        
        # Check if the user confirms being Dennis
        confirm_keywords = ['si', 'sí', 'yes', 'correcto', 'correct', 'soy dennis', 'soy dennis kangme']
        deny_keywords = ['no', 'no soy', 'no es', 'incorrecto', 'incorrect']
        
        is_dennis = any(keyword in latest_message for keyword in confirm_keywords)
        
        # Log the interaction to database
        self.log_interaction(tracker, "identity_check", f"is_dennis={is_dennis}")
        
        return [SlotSet("is_dennis", is_dennis)]


class ActionHandleIdentityResponse(Action):
    def name(self) -> Text:
        return "action_handle_identity_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        is_dennis = tracker.get_slot("is_dennis")
        client_name = tracker.get_slot("client_name") or "Dennis"
        
        if is_dennis:
            dispatcher.utter_message(response="utter_invoice_pending_info", client_name=client_name)
        else:
            dispatcher.utter_message(response="utter_wrong_person")
        
        return []


class ActionHandlePaymentResponse(Action):
    def name(self) -> Text:
        return "action_handle_payment_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        latest_message = tracker.latest_message.get('text', '').lower()
        client_name = tracker.get_slot("client_name") or "Dennis"
        
        # Check if user can pay
        can_pay_keywords = ['si', 'sí', 'yes', 'puedo', 'claro', 'puedo pagar']
        cannot_pay_keywords = ['no', 'no puedo', 'no tengo', 'no puedo pagar']
        ask_date_keywords = ['fecha', 'cuándo', 'cuando', 'qué fecha', 'que fecha']
        
        can_pay = any(keyword in latest_message for keyword in can_pay_keywords)
        cannot_pay = any(keyword in latest_message for keyword in cannot_pay_keywords)
        ask_date = any(keyword in latest_message for keyword in ask_date_keywords)
        
        if can_pay:
            dispatcher.utter_message(response="utter_ask_payment_date")
        elif cannot_pay:
            dispatcher.utter_message(response="utter_ask_reason")
        elif ask_date:
            # Use the new action to get dynamic invoice date info
            return [FollowupAction("action_get_invoice_date_info")]
        else:
            # Default to asking for payment date
            dispatcher.utter_message(response="utter_ask_payment_date")
        
        # Log the interaction to database
        self.log_interaction(tracker, "payment_response", f"can_pay={can_pay}, cannot_pay={cannot_pay}, ask_date={ask_date}")
        
        return []


class ActionHandleDateQuestion(Action):
    def name(self) -> Text:
        return "action_handle_date_question"

    def convert_relative_date(self, date_text: str) -> str:
        """Convert relative date expressions to specific dates"""
        today = datetime.now()
        date_text = date_text.strip().lower()
        
        # Tomorrow
        if any(word in date_text for word in ['mañana', 'tomorrow', 'mañ']):
            target_date = today + timedelta(days=1)
            return target_date.strftime('%Y-%m-%d')
        
        # Next week patterns
        if 'próximo' in date_text or 'proximo' in date_text or 'que viene' in date_text:
            # Find the day of the week
            days = {
                'lunes': 0, 'monday': 0,
                'martes': 1, 'tuesday': 1,
                'miércoles': 2, 'miercoles': 2, 'wednesday': 2,
                'jueves': 3, 'thursday': 3,
                'viernes': 4, 'friday': 4,
                'sábado': 5, 'sabado': 5, 'saturday': 5,
                'domingo': 6, 'sunday': 6
            }
            
            for day_name, day_num in days.items():
                if day_name in date_text:
                    # Calculate next occurrence of this day
                    days_ahead = day_num - today.weekday()
                    if days_ahead <= 0:  # Target day already happened this week
                        days_ahead += 7
                    target_date = today + timedelta(days=days_ahead)
                    return target_date.strftime('%Y-%m-%d')
        
        # Specific day of the week
        days = {
            'lunes': 0, 'monday': 0,
            'martes': 1, 'tuesday': 1,
            'miércoles': 2, 'miercoles': 2, 'wednesday': 2,
            'jueves': 3, 'thursday': 3,
            'viernes': 4, 'friday': 4,
            'sábado': 5, 'sabado': 5, 'saturday': 5,
            'domingo': 6, 'sunday': 6
        }
        
        for day_name, day_num in days.items():
            if day_name in date_text:
                # Calculate next occurrence of this day
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime('%Y-%m-%d')
        
        # End of month
        if any(word in date_text for word in ['fin de mes', 'final de mes', 'end of month']):
            # Get the last day of current month
            last_day = calendar.monthrange(today.year, today.month)[1]
            target_date = today.replace(day=last_day)
            return target_date.strftime('%Y-%m-%d')
        
        # Next month
        if any(word in date_text for word in ['próximo mes', 'proximo mes', 'next month']):
            if today.month == 12:
                target_date = today.replace(year=today.year + 1, month=1)
            else:
                target_date = today.replace(month=today.month + 1)
            return target_date.strftime('%Y-%m-%d')
        
        # Try to parse as a specific date (DD/MM or DD-MM)
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})',  # DD/MM
            r'(\d{1,2})-(\d{1,2})',  # DD-MM
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                day, month = int(match.group(1)), int(match.group(2))
                try:
                    target_date = today.replace(day=day, month=month)
                    return target_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        return None

    def format_date_spanish(self, date_str: str) -> str:
        """Format date in Spanish format like 'viernes 8 de agosto'"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Spanish day names
            days = {
                0: 'lunes',
                1: 'martes', 
                2: 'miércoles',
                3: 'jueves',
                4: 'viernes',
                5: 'sábado',
                6: 'domingo'
            }
            
            # Spanish month names
            months = {
                1: 'enero',
                2: 'febrero',
                3: 'marzo',
                4: 'abril',
                5: 'mayo',
                6: 'junio',
                7: 'julio',
                8: 'agosto',
                9: 'septiembre',
                10: 'octubre',
                11: 'noviembre',
                12: 'diciembre'
            }
            
            day_name = days[date_obj.weekday()]
            day_number = date_obj.day
            month_name = months[date_obj.month]
            
            return f"{day_name} {day_number} de {month_name}"
            
        except Exception as e:
            print(f"Error formatting date: {e}")
            return date_str

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        latest_message = tracker.latest_message.get('text', '').lower()
        client_name = tracker.get_slot("client_name") or "Dennis"
        
        # Convert relative date to specific date
        specific_date = self.convert_relative_date(latest_message)
        
        if specific_date:
            # Format date in Spanish
            formatted_date = self.format_date_spanish(specific_date)
            
            # Log the interaction to database with specific date
            self.log_interaction(tracker, "payment_date_confirmed", specific_date)
            
            # Update the invoice in the database with the payment date
            self.update_invoice_payment_date(tracker, specific_date)
            
            dispatcher.utter_message(response="utter_payment_confirmed", payment_date=formatted_date, client_name=client_name)
            return [SlotSet("payment_date", specific_date)]
        else:
            # If we can't parse the date, store the original response
            self.log_interaction(tracker, "payment_date_confirmed", latest_message)
            dispatcher.utter_message(response="utter_payment_confirmed", payment_date=latest_message, client_name=client_name)
            return [SlotSet("payment_date", latest_message)]

    def update_invoice_payment_date(self, tracker: Tracker, payment_date: str):
        """Update ALL pending invoices in the database with the payment date"""
        try:
            connection = get_database_connection()
            if connection:
                cursor = connection.cursor()
                
                # Update ALL pending invoices with the payment date
                update_query = """
                UPDATE invoices 
                SET payment_date = %s, status = 'payment_scheduled'
                WHERE customer_id = (SELECT id FROM customers WHERE name = %s)
                AND status = 'pending'
                AND payment_date IS NULL
                """
                
                client_name = tracker.get_slot("client_name") or "Dennis Kangme"
                cursor.execute(update_query, (payment_date, client_name))
                rows_updated = cursor.rowcount
                connection.commit()
                cursor.close()
                connection.close()
                
                print(f"Updated {rows_updated} invoices with payment date {payment_date} for {client_name}")
                
        except Exception as e:
            print(f"Error updating invoice payment date: {e}")


class ActionClassifyReason(Action):
    def name(self) -> Text:
        return "action_classify_reason"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        latest_message = tracker.latest_message.get('text', '').lower()
        client_name = tracker.get_slot("client_name") or "Dennis Kangme"
        
        # Classify the reason type
        financial_difficulty = any(word in latest_message for word in 
                                 ['sin dinero', 'cesante', 'enfermo', 'desempleado', 'sin trabajo'])
        
        payment_dispute = any(word in latest_message for word in 
                            ['ya pagué', 'ya la pagué', 'no es mi deuda', 'no debo', 'ya pague'])
        
        if financial_difficulty:
            reason_type = "financial_difficulty"
            dispatcher.utter_message(response="utter_financial_difficulty", client_name=client_name)
        elif payment_dispute:
            reason_type = "payment_dispute"
            # Update invoice status to disputed
            self.update_invoice_dispute_status(tracker)
            dispatcher.utter_message(response="utter_payment_dispute", client_name=client_name)
        else:
            reason_type = "other"
            dispatcher.utter_message(response="utter_financial_difficulty", client_name=client_name)
        
        # Log the interaction to database
        self.log_interaction(tracker, "reason_classified", reason_type)
        
        return [SlotSet("reason_type", reason_type)]

    def update_invoice_dispute_status(self, tracker: Tracker):
        """Update ALL pending invoices to disputed status"""
        try:
            connection = get_database_connection()
            if connection:
                cursor = connection.cursor()
                
                # Update ALL pending invoices to disputed status
                update_query = """
                UPDATE invoices 
                SET status = 'disputed'
                WHERE customer_id = (SELECT id FROM customers WHERE name = %s)
                AND status = 'pending'
                AND payment_date IS NULL
                """
                
                client_name = tracker.get_slot("client_name") or "Dennis Kangme"
                cursor.execute(update_query, (client_name,))
                rows_updated = cursor.rowcount
                connection.commit()
                cursor.close()
                connection.close()
                
                print(f"Updated {rows_updated} invoices to disputed status for {client_name}")
                
        except Exception as e:
            print(f"Error updating invoice dispute status: {e}")


class ActionCheckSufficientFunds(Action):
    def name(self) -> Text:
        return "action_check_sufficient_funds"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This action is kept for compatibility but not used in the new flow
        balance = 1000
        transfer_amount = tracker.get_slot("amount")
        has_sufficient_funds = transfer_amount <= balance
        return [SlotSet("has_sufficient_funds", has_sufficient_funds)]


class ActionGetPendingInvoicesInfo(Action):
    def name(self) -> Text:
        return "action_get_pending_invoices_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        client_name = tracker.get_slot("client_name") or "Dennis Kangme"
        print(f"DEBUG: ActionGetPendingInvoicesInfo called for client: {client_name}")
        
        try:
            connection = get_database_connection()
            if connection:
                cursor = connection.cursor()
                
                # Get pending invoices for the customer
                query = """
                SELECT COUNT(*) as invoice_count, SUM(amount) as total_amount
                FROM invoices i
                JOIN customers c ON i.customer_id = c.id
                WHERE c.name = %s AND i.status = 'pending' AND i.payment_date IS NULL
                """
                
                print(f"DEBUG: Executing query with client_name: {client_name}")
                cursor.execute(query, (client_name,))
                result = cursor.fetchone()
                print(f"DEBUG: Query result: {result}")
                
                cursor.close()
                connection.close()
                
                if result and result[0] > 0:
                    invoice_count = result[0]
                    total_amount = float(result[1]) if result[1] else 0.0
                    
                    # Format the total amount as a string with proper formatting
                    formatted_total = f"${total_amount:,.0f}"
                    
                    print(f"DEBUG: Found {invoice_count} invoices, total: {formatted_total}")
                    
                    # Log the interaction
                    self.log_interaction(tracker, "pending_invoices_info", f"count={invoice_count}, total={total_amount}")
                    
                    # Set slots with the information
                    return [
                        SlotSet("pending_invoice_count", str(invoice_count)),
                        SlotSet("pending_invoice_total", formatted_total)
                    ]
                else:
                    # No pending invoices found
                    print(f"DEBUG: No pending invoices found for {client_name}")
                    self.log_interaction(tracker, "pending_invoices_info", "no_pending_invoices")
                    return [
                        SlotSet("pending_invoice_count", "0"),
                        SlotSet("pending_invoice_total", "$0")
                    ]
                    
        except Exception as e:
            print(f"DEBUG: Error getting pending invoices info: {e}")
            # Fallback to default values
            return [
                SlotSet("pending_invoice_count", "1"),
                SlotSet("pending_invoice_total", "$55,000")
            ]


class ActionGetInvoiceDateInfo(Action):
    def name(self) -> Text:
        return "action_get_invoice_date_info"

    def format_date_spanish(self, date_str: str) -> str:
        """Format date in Spanish format"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            months = {
                1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
                7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
            }
            return f"{date_obj.day} de {months[date_obj.month]} de {date_obj.year}"
        except:
            return date_str

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        client_name = tracker.get_slot("client_name") or "Dennis Kangme"
        print(f"DEBUG: ActionGetInvoiceDateInfo called for client: {client_name}")
        
        try:
            connection = get_database_connection()
            if connection:
                cursor = connection.cursor()
                
                # Get the most recent pending invoice for the customer
                query = """
                SELECT i.issue_date, i.due_date, i.invoice_number
                FROM invoices i
                JOIN customers c ON i.customer_id = c.id
                WHERE c.name = %s AND i.status = 'pending' AND i.payment_date IS NULL
                ORDER BY i.due_date ASC
                LIMIT 1
                """
                
                print(f"DEBUG: Executing invoice date query for client: {client_name}")
                cursor.execute(query, (client_name,))
                result = cursor.fetchone()
                print(f"DEBUG: Invoice date query result: {result}")
                
                cursor.close()
                connection.close()
                
                if result:
                    issue_date, due_date, invoice_number = result
                    
                    # Format dates in Spanish
                    formatted_issue_date = self.format_date_spanish(str(issue_date))
                    formatted_due_date = self.format_date_spanish(str(due_date))
                    
                    # Create dynamic response
                    response_text = f"La factura {invoice_number} fue emitida el {formatted_issue_date} con fecha de vencimiento {formatted_due_date}."
                    
                    print(f"DEBUG: Generated response: {response_text}")
                    
                    # Log the interaction
                    self.log_interaction(tracker, "invoice_date_info", f"issue_date={issue_date}, due_date={due_date}")
                    
                    # Send the response directly
                    dispatcher.utter_message(text=response_text)
                    
                    return []
                else:
                    # No pending invoices found, use default response
                    print(f"DEBUG: No pending invoices found for {client_name}, using default response")
                    self.log_interaction(tracker, "invoice_date_info", "no_pending_invoices")
                    dispatcher.utter_message(response="utter_invoice_date_info")
                    return []
                    
        except Exception as e:
            print(f"DEBUG: Error getting invoice date info: {e}")
            # Fallback to default response
            dispatcher.utter_message(response="utter_invoice_date_info")
            return []


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


def log_interaction(tracker: Tracker, interaction_type: str, data: str = None):
    """Log interaction to database"""
    try:
        connection = get_database_connection()
        if connection:
            cursor = connection.cursor()
            
            # Create interactions table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS interactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255),
                interaction_type VARCHAR(100),
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            
            # Insert interaction
            insert_query = """
            INSERT INTO interactions (session_id, interaction_type, data)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (tracker.sender_id, interaction_type, data))
            connection.commit()
            cursor.close()
            connection.close()
            
    except Exception as e:
        print(f"Error logging interaction: {e}")


# Add the log_interaction method to the Action classes
ActionExtractClientName.log_interaction = staticmethod(log_interaction)
ActionCheckIdentity.log_interaction = staticmethod(log_interaction)
ActionHandleIdentityResponse.log_interaction = staticmethod(log_interaction)
ActionHandlePaymentResponse.log_interaction = staticmethod(log_interaction)
ActionHandleDateQuestion.log_interaction = staticmethod(log_interaction)
ActionClassifyReason.log_interaction = staticmethod(log_interaction)
ActionCheckSufficientFunds.log_interaction = staticmethod(log_interaction)
ActionGetPendingInvoicesInfo.log_interaction = staticmethod(log_interaction)
ActionGetInvoiceDateInfo.log_interaction = staticmethod(log_interaction)
