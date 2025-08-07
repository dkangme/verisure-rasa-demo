# System Patterns: Verisure Billing Assistant

## Architecture Overview

### 1. Rasa Core Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   NLU Pipeline  │───▶│  Dialogue Mgmt  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Intent/Entity  │    │  Action Server  │
                       │  Recognition    │    │  (Custom Logic) │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   MariaDB DB    │
                                               │  (Customers,    │
                                               │   Invoices,     │
                                               │  Interactions)  │
                                               └─────────────────┘
```

### 2. Key Design Patterns

#### Intent-Driven Flow Control
- **Primary Intents**: `start`, `confirm_identity`, `deny_identity`, `can_pay`, `cannot_pay`, `payment_date_response`
- **Fallback Intents**: `nlu_fallback`, `out_of_scope`
- **Pattern**: Rules trigger flows based on intent recognition

#### Custom Action Pattern
```python
class ActionHandleDateQuestion(Action):
    def run(self, dispatcher, tracker, domain):
        # 1. Extract user input
        # 2. Convert relative date to specific date
        # 3. Format date in Spanish
        # 4. Update database
        # 5. Send response
```

#### Database Integration Pattern
- **Connection**: `mysql.connector` with environment variables
- **Logging**: Every action logs to `interactions` table
- **Updates**: Invoice status and payment dates updated in real-time

### 3. Conversation Flow Patterns

#### Main Flow Pattern
```
start → identity_check → invoice_info → payment_scheduling → confirmation
```

#### Branching Pattern
```
identity_check
├── confirm_identity → invoice_info → payment_scheduling
└── deny_identity → end_conversation
```

#### Payment Response Pattern
```
payment_scheduling
├── can_pay → date_question → date_processing
├── cannot_pay → reason_question → reason_classification
└── ask_invoice_date → date_info → reason_question
```

### 4. Data Flow Patterns

#### Slot Management
- **Dynamic Slots**: `client_name`, `payment_date`, `reason_type`
- **Session Slots**: `is_dennis`, `payment_response`
- **Pattern**: Slots persist across conversation turns

#### Database Operations
```python
# Pattern: Connect → Execute → Log → Close
connection = get_database_connection()
cursor = connection.cursor()
cursor.execute(query, params)
connection.commit()
cursor.close()
connection.close()
```

### 5. Error Handling Patterns

#### Fallback Strategy
- **NLU Fallback**: Generic response for unrecognized intents
- **Action Fallback**: Graceful handling of database errors
- **Date Processing Fallback**: Store original text if parsing fails

#### Logging Pattern
```python
# Every action logs its execution
self.log_interaction(tracker, "action_type", "data")
```

### 6. Configuration Patterns

#### Environment-Based Configuration
```python
# Pattern: Load from .env file
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
```

#### Rasa Configuration
- **Policies**: FlowPolicy + RulePolicy (CALM disabled)
- **NLU Pipeline**: Standard Rasa pipeline
- **Actions**: Custom actions for business logic

### 7. Testing Patterns

#### Automated Testing
- **Unit Tests**: Individual action testing
- **Integration Tests**: Full conversation flow testing
- **Database Tests**: Verify data persistence

#### Manual Testing
- **Rasa Shell**: Interactive conversation testing
- **Database Verification**: Check data updates
- **Log Analysis**: Review interaction logs

## Technical Decisions

### 1. CALM Disabled
- **Reason**: Interfered with rule/flow execution
- **Alternative**: Manual intent classification and response generation
- **Result**: More predictable conversation flow

### 2. MariaDB Choice
- **Reason**: Reliable, widely supported
- **Schema**: Normalized tables for customers, invoices, interactions
- **Performance**: Indexed queries for fast lookups

### 3. Spanish Date Formatting
- **Pattern**: Convert YYYY-MM-DD to "viernes 8 de agosto"
- **Implementation**: Custom `format_date_spanish()` method
- **Benefit**: More natural user experience

### 4. Rule-Based Flow Control
- **Pattern**: Rules trigger specific actions/flows
- **Benefit**: Clear, predictable conversation paths
- **Alternative**: Pure flow-based (rejected for complexity)

## Component Relationships

### 1. File Dependencies
```
domain.yml ← config.yml
     ↓
data/flows.yml ← data/rules.yml ← data/nlu.yml
     ↓
actions/actions.py ← endpoints.yml
     ↓
database_config.py ← .env
```

### 2. Action Dependencies
```
ActionExtractClientName → ActionCheckIdentity → ActionHandleIdentityResponse
                                    ↓
ActionHandlePaymentResponse → ActionHandleDateQuestion → ActionClassifyReason
```

### 3. Database Dependencies
```
customers ← invoices ← interactions
     ↓           ↓           ↓
customer_id  customer_id  customer_id
``` 