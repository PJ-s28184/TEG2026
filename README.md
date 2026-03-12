# Capstone Project: Interaktywny Doradca Podatkowy AI

## What You'll Build
An AI-powered interactive tax advisory system that helps users understand tax obligations, deductions, and reporting requirements. 
The system will demonstrate the advantages of combining **RAG (Retrieval Augmented Generation)** and **structured tax knowledge graphs** to answer complex tax-related questions.

The application will simulate a **digital tax advisor** capable of analyzing user situations and providing guidance based on tax regulations.

---

# Learning Goals

- Implement **RAG systems using LLMs**
- Build a **tax knowledge base from legal documents**
- Design a **tax rule engine and reasoning system**
- Create **natural language financial advisory interfaces**
- Compare AI advisory responses with traditional rule-based systems

---

# Project Overview

## Problem

Understanding tax regulations is difficult for individuals and small businesses because:

- Tax law documents are complex and difficult to interpret
- Many taxpayers do not know what deductions they qualify for
- Regulations change frequently
- Professional tax advisors are expensive
- People often need quick answers to questions like:
  - *"Can I deduct home office expenses?"*
  - *"How much tax will I pay if I earn X?"*

---

## Solution

Build an **AI-powered tax advisor** that:

- Extracts knowledge from **tax regulations and legal documents**
- Answers tax-related questions in **natural language**
- Suggests **possible deductions and tax optimizations**
- Simulates **real-world taxpayer scenarios**
- Provides explanations and references to tax regulations

---

# Project Phases (10 weeks)

---

# Phase 1: Foundation (Weeks 1–2)

### Goal
Set up the system infrastructure and build the tax knowledge base.

### Tasks

- Collect tax regulation documents (PDFs or official guides)
- Extract structured knowledge using LLMs
- Build a **tax knowledge database**
- Prepare sample taxpayer scenarios

### Deliverables

- Structured tax knowledge dataset
- Document ingestion pipeline
- 20+ tax rule documents processed
- Basic RAG system

---

# Phase 2: Tax Reasoning Engine (Weeks 3–5)

### Goal
Develop logic for analyzing tax scenarios.

### Tasks

- Implement taxpayer profile structure
- Parse user financial situations
- Implement deduction detection logic
- Calculate approximate tax obligations
- Add reasoning explanations

### Deliverables

- Tax scenario parser
- Deduction recommendation system
- Tax estimation module
- Explanation generator

---

# Phase 3: Interactive Advisory System (Weeks 6–8)

### Goal
Create a user interface and demonstrate AI advisory capabilities.

### Tasks

- Build conversational interface
- Implement tax query system
- Create scenario simulations
- Build comparison with rule-based approach
- Add explanation references to legal documents

### Example Queries to Support

- "What tax deductions can freelancers use?"
- "Can I deduct my home office?"
- "How much tax will I pay if I earn 100,000 PLN?"
- "What documents do I need for a tax return?"
- "What tax benefits exist for students?"

### Deliverables

- Conversational tax assistant
- Interactive query system
- Comparison between AI advisor and rule-based logic
- Simple dashboard

---

# Phase 4: Evaluation (Weeks 9–10)

### Goal
Evaluate system accuracy and present results.

### Tasks

- Test system on multiple tax scenarios
- Evaluate response accuracy
- Document system architecture
- Prepare demonstration
- Create final presentation

### Deliverables

- System evaluation report
- Technical documentation
- Demonstration video
- Final presentation

---

# Success Criteria

## Minimum Requirements

- Build a tax knowledge base from legal documents
- Answer at least **15 tax-related queries correctly**
- Simulate **5 different taxpayer scenarios**
- Provide explanations referencing tax regulations
- Complete system documentation and demo

---

# Advanced Features (Bonus)

- Personalized tax optimization suggestions
- Multi-country tax system support
- Financial planning simulations
- Visual tax calculation breakdowns
- Chat history and scenario tracking

---

# Assessment (100 points)

| Component | Weight | Description |
|----------|--------|-------------|
| Technical Implementation | 40% | Code quality, architecture, performance |
| Knowledge Base Design | 20% | Tax data modeling and retrieval |
| Advisory Logic | 20% | Accuracy of tax suggestions and reasoning |
| Documentation | 10% | Technical documentation and user guide |
| Presentation | 10% | Demonstration and explanation of system |

---

# Business Scenarios to Solve

Your system must support realistic tax advisory questions such as:

**Tax Estimation**  
"How much tax will I pay if I earn 120,000 PLN?"

**Deduction Analysis**  
"What expenses can freelancers deduct?"

**Tax Optimization**  
"What is the best tax form for a small business?"

**Document Requirements**  
"What documents are needed for annual tax filing?"

**Eligibility Analysis**  
"Do I qualify for tax benefits as a student?"

---

# Getting Started

## Data Sources

Use official or simulated tax documents such as:

- Government tax guides
- Legal tax regulations
- Sample tax forms
- Financial advisory documents

---

# Tech Stack

### Required

- Python
- OpenAI API or other LLM
- LangChain or LlamaIndex
- Vector database (FAISS / Chroma / Pinecone)

### Optional

- Neo4j knowledge graph
- Streamlit interface
- FastAPI backend
- PostgreSQL for structured data

---

# Extension Areas

Extend the system to support:

- Tax law updates
- Multiple income sources
- Business tax calculations
- Financial planning advice
- Advanced reasoning over legal documents

---

# Resources & Support

Documentation sources:

- LangChain documentation
- OpenAI API documentation
- Government tax resources
- Legal tax publications

Timeline: **10 weeks with milestone reviews**

---

# Success Tips

- Start with a **simple tax question-answering system**
- Focus on **clear explanations**, not just answers
- Build realistic taxpayer scenarios
- Validate answers using **real tax rules**
- Keep the system **practical and understandable**

---

# Goal

Build a professional **AI-powered tax advisory assistant** that demonstrates how modern AI systems can simplify complex legal and financial regulations.  

The final system should show how **AI can assist individuals and small businesses in understanding and managing their taxes.**
