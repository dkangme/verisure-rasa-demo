# Technical Context: Verisure Billing Assistant

## Technology Stack

### 1. Core Framework
- **Rasa Pro**: Conversational AI framework
- **Version**: Latest stable (with CALM disabled)
- **Language**: Python 3.10+
- **Architecture**: NLU + Dialogue Management + Action Server

### 2. Database
- **MariaDB**: Relational database
- **Version**: 10.x
- **Connection**: `mysql.connector-python`
- **Schema**: 3 main tables (customers, invoices, interactions)

### 3. Development Environment
- **OS**: macOS (darwin 24.5.0)
- **Shell**: zsh
- **Virtual Environment**: `.venv` (Python 3.10)
- **Package Manager**: pip

## Project Structure

```
verisure-rasa-demo/
├── actions/
│   ├── __init__.py
│   └── actions.py          # Custom business logic
├── data/
│   ├── flows.yml           # Conversation flows
│   ├── nlu.yml            # Training examples
│   ├── patterns.yml       # Common patterns
│   └── rules.yml          # Conversation rules
├── models/                # Trained Rasa models
├── .venv/                 # Python virtual environment
├── config.yml             # Rasa configuration
├── credentials.yml        # External service credentials
├── domain.yml            # Central configuration
├── endpoints.yml          # Service endpoints
├── database_config.py     # Database setup script
├── requirements.txt       # Python dependencies
├── setup.py              # Automated setup
├── test_bot.py           # Testing script
├── README.md             # Project documentation
└── .env                  # Environment variables
```

## Dependencies

### 1. Python Packages
```txt
rasa>=3.6.0
mysql-connector-python>=8.0.0
python-dotenv>=0.19.0
```

### 2. System Dependencies
- **MariaDB**: Database server
- **Python 3.10+**: Runtime environment
- **Git**: Version control

### 3. Environment Variables
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=verisure_demo
OPENAI_API_KEY=your_openai_api_key
RASA_TOKEN=your_rasa_token
```

## Database Schema

### 1. Customers Table
```sql
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Invoices Table
```sql
CREATE TABLE invoices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    invoice_number VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    status ENUM('pending', 'paid', 'payment_scheduled') DEFAULT 'pending',
    payment_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### 3. Interactions Table
```sql
CREATE TABLE interactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255) NOT NULL,
    customer_id INT NULL,
    interaction_type VARCHAR(100) NOT NULL,
    data TEXT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

## Configuration Files

### 1. config.yml
```yaml
language: en
pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
  - name: DIETClassifier
  - name: EntitySynonymMapper
  - name: ResponseSelector
policies:
  - name: FlowPolicy
  - name: RulePolicy
assistant_id: 20250806-215326-olive-flag
```

### 2. domain.yml
```yaml
intents:
  - start
  - confirm_identity
  - deny_identity
  - can_pay
  - cannot_pay
  - ask_invoice_date
  - payment_date_response
  - financial_difficulty
  - payment_dispute
  - nlu_fallback
  - out_of_scope

slots:
  client_name:
    type: text
    mappings:
    - type: custom
  is_dennis:
    type: bool
    mappings:
    - type: custom
  payment_response:
    type: text
    mappings:
    - type: custom
  payment_date:
    type: text
    mappings:
    - type: custom
  reason_type:
    type: text
    mappings:
    - type: custom
  invoice_date:
    type: text
    mappings:
    - type: custom

responses:
  utter_greeting_and_identity_check:
    - text: "Hola soy veriBot el asistente digital de Verisure. Quisiera entregarle información importante de sus facturas, ¿hablo con {client_name}?"
  utter_wrong_person:
    - text: "Lamento molestarlo, registraré en nuestros sistemas esta información. Que tenga un buen día."
  utter_invoice_pending_info:
    - text: "Buenos días don {client_name}, le informo que tiene pendiente de pago una factura por un monto de $55.000. Quisiera saber si podrá pagarla dentro de los siguientes 5 días."
  utter_payment_confirmed:
    - text: "Perfecto don {client_name}, registro {payment_date} como su día de pago. Que tenga buen día."

actions:
  - action_extract_client_name
  - action_check_identity
  - action_handle_identity_response
  - action_handle_payment_response
  - action_handle_date_question
  - action_classify_reason
  - action_check_sufficient_funds
```

## Development Setup

### 1. Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd verisure-rasa-demo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python database_config.py

# Train model
rasa train
```

### 2. Running the Bot
```bash
# Terminal 1: Start action server
source .venv/bin/activate
rasa run actions

# Terminal 2: Start Rasa shell
source .venv/bin/activate
rasa shell
```

### 3. Testing
```bash
# Run automated tests
python test_bot.py

# Manual testing
rasa shell
```

## Key Technical Decisions

### 1. CALM Disabled
- **Reason**: Interfered with rule/flow execution
- **Impact**: Manual intent classification required
- **Benefit**: More predictable conversation flow

### 2. MariaDB Choice
- **Reason**: Reliable, widely supported
- **Alternative**: PostgreSQL, MySQL
- **Benefit**: Easy setup and maintenance

### 3. Custom Actions
- **Pattern**: Business logic in Python actions
- **Benefit**: Full control over conversation flow
- **Trade-off**: More complex than pure Rasa flows

### 4. Environment Variables
- **Pattern**: Configuration in .env file
- **Benefit**: Secure credential management
- **Usage**: Database and API credentials

## Performance Considerations

### 1. Database Optimization
- **Indexes**: Primary keys and foreign keys
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Efficient SELECT and UPDATE queries

### 2. Rasa Performance
- **Model Training**: Regular retraining with new data
- **Intent Recognition**: Optimized training examples
- **Action Response Time**: Efficient custom actions

### 3. Scalability
- **Horizontal Scaling**: Multiple action server instances
- **Database Scaling**: Read replicas for high load
- **Caching**: Redis for session data (future enhancement)

## Security Considerations

### 1. Database Security
- **Credentials**: Stored in environment variables
- **Connection**: SSL/TLS encryption
- **Access Control**: Limited database user permissions

### 2. API Security
- **Authentication**: Rasa token for API access
- **Input Validation**: Sanitize user inputs
- **Error Handling**: Don't expose sensitive information

### 3. Data Privacy
- **PII Protection**: Encrypt sensitive customer data
- **Audit Trail**: Complete interaction logging
- **Data Retention**: Implement data retention policies 