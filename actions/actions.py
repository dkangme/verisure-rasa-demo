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
        # Get the latest message from the user
        latest_message = tracker.latest_message.get('text', '').lower()
        
        # Look for patterns like "soy [nombre]", "hablo con [nombre]", etc.
        name_patterns = [
            r'soy\s+([a-zA-Z\s]+)',
            r'habla\s+con\s+([a-zA-Z\s]+)',
            r'con\s+([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+kangme',
            r'([a-zA-Z\s]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, latest_message)
            if match:
                name = match.group(1).strip().title()
                return [SlotSet("client_name", name)]
        
        # If no name found, use default
        return [SlotSet("client_name", "Dennis")]


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
            dispatcher.utter_message(response="utter_invoice_date_info")
            dispatcher.utter_message(response="utter_ask_reason")
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
        """Update the invoice in the database with the payment date"""
        try:
            connection = get_database_connection()
            if connection:
                cursor = connection.cursor()
                
                # Update the invoice with the payment date
                update_query = """
                UPDATE invoices 
                SET payment_date = %s, status = 'payment_scheduled'
                WHERE customer_id = (SELECT id FROM customers WHERE name = %s)
                AND status = 'pending'
                ORDER BY due_date ASC
                LIMIT 1
                """
                
                client_name = tracker.get_slot("client_name") or "Dennis Kangme"
                cursor.execute(update_query, (payment_date, client_name))
                connection.commit()
                cursor.close()
                connection.close()
                
                print(f"Updated invoice payment date to {payment_date} for {client_name}")
                
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
        client_name = tracker.get_slot("client_name") or "Dennis"
        
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
            dispatcher.utter_message(response="utter_payment_dispute", client_name=client_name)
        else:
            reason_type = "other"
            dispatcher.utter_message(response="utter_financial_difficulty", client_name=client_name)
        
        # Log the interaction to database
        self.log_interaction(tracker, "reason_classified", reason_type)
        
        return [SlotSet("reason_type", reason_type)]


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
