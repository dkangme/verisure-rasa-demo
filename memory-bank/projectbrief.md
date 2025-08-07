# Project Brief: Verisure Billing Assistant Demo

## Project Overview
This is a Rasa-based conversational AI demo for Verisure's billing department. The bot handles customer interactions regarding pending invoices, payment scheduling, and dispute resolution.

## Core Requirements

### 1. Conversational Flow
- **Primary Flow**: Customer identity verification → Invoice information → Payment scheduling
- **Secondary Flows**: Dispute resolution, financial difficulty handling
- **Language**: Spanish and English support
- **Target**: Verisure customers

### 2. Database Integration
- **Database**: MariaDB
- **Tables**: `customers`, `invoices`, `interactions`
- **Purpose**: Store customer data, invoice information, and conversation logs

### 3. Key Features
- **Identity Verification**: Simple yes/no confirmation
- **Payment Scheduling**: Convert relative dates to specific dates
- **Date Formatting**: Display dates in Spanish format (e.g., "viernes 8 de agosto")
- **Fallback Handling**: Generic but useful responses
- **Interaction Logging**: All conversations logged to database

### 4. Technical Stack
- **Framework**: Rasa Pro (with CALM disabled)
- **Database**: MariaDB
- **Language**: Python
- **NLU**: Intent classification and entity extraction
- **Actions**: Custom Python actions for business logic

### 5. Success Criteria
- ✅ Flows execute correctly without fallbacks
- ✅ Database updates work properly
- ✅ Date processing and formatting works
- ✅ Identity verification functions
- ✅ Payment scheduling implemented
- ✅ Interaction logging complete

## Project Status: COMPLETED ✅

All core requirements have been successfully implemented and tested. 