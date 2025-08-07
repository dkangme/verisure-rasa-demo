# Product Context: Verisure Billing Assistant

## Why This Project Exists

### Problem Statement
Verisure's billing department needs an automated way to:
1. **Contact customers** about pending invoices
2. **Schedule payments** efficiently
3. **Handle disputes** and financial difficulties
4. **Log all interactions** for compliance and follow-up

### Business Value
- **Automated Customer Service**: Reduce manual calls and improve efficiency
- **Payment Scheduling**: Increase on-time payments through automated scheduling
- **Compliance**: Complete audit trail of all customer interactions
- **Customer Experience**: 24/7 availability for billing inquiries

## How It Should Work

### 1. Customer Journey
```
Customer receives call → Identity verification → Invoice information → Payment scheduling → Confirmation
```

### 2. Key Interactions

#### Identity Verification
- **Bot**: "¿hablo con Dennis Kangme?"
- **Customer**: "Sí" or "No"
- **Result**: Proceed with invoice info or end call

#### Payment Scheduling
- **Bot**: "¿Me puede indicar la fecha que con seguridad pagará la factura?"
- **Customer**: "mañana", "el próximo jueves", "fin de mes"
- **Result**: Convert to specific date and register in database

#### Dispute Handling
- **Bot**: "¿Me puede indicar la razón por la que no puede pagar?"
- **Customer**: "Ya la pagué", "Estoy sin dinero"
- **Result**: Classify and provide appropriate response

### 3. User Experience Goals
- **Natural Language**: Accept relative dates and convert to specific dates
- **Friendly Tone**: Professional but approachable
- **Clear Communication**: Precise and concise messages
- **Bilingual Support**: Spanish and English

### 4. Success Metrics
- **Payment Scheduling Rate**: % of customers who schedule payments
- **Interaction Completion**: % of conversations that reach conclusion
- **Database Accuracy**: All interactions properly logged
- **Date Processing**: Accurate conversion of relative to specific dates

## Target Users
- **Primary**: Verisure customers with pending invoices
- **Secondary**: Verisure billing department staff
- **Demo Focus**: Dennis Kangme (demo customer)

## Integration Points
- **MariaDB Database**: Customer, invoice, and interaction data
- **Rasa Actions**: Custom business logic
- **Environment Variables**: Database credentials and API keys 