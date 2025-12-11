# AI Telephony Agent with RAG Integration

An advanced AI phone agent powered by LiveKit, integrating RAG (Retrieval Augmented Generation) for FAQ handling, CRM lookups, bookings, renewals, and intelligent escalation.

## Features

- **RAG-Powered FAQ System**: Answers customer questions using a vector database knowledge base
- **CRM Integration**: Looks up customer information from a searchable CRM database
- **Booking Management**: Handles service bookings and appointment scheduling
- **Renewal Processing**: Manages service and subscription renewals
- **Intelligent Triage & Escalation**: Smart routing and escalation based on issue complexity and urgency
- **Multi-level Confidence**: Escalates to humans when confidence is low
- **Fallback Logic**: Comprehensive error handling and escalation paths

## Architecture

```
┌─────────────────┐
│  Phone Call     │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ LiveKit  │
    │  Agent   │
    └────┬─────┘
         │
    ┌────▼──────────────────────────┐
    │   TelephonyAgent (Agent)      │
    │                               │
    │  ┌─────────────────────────┐  │
    │  │ Function Tools:         │  │
    │  │ - lookup_faq()         │  │
    │  │ - lookup_customer_crm()│  │
    │  │ - handle_booking()     │  │
    │  │ - handle_renewal()     │  │
    │  │ - triage_and_escalate()│  │
    │  └─────────────────────────┘  │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────┐
    │   RAGService      │
    │   (Qdrant + AI)   │
    └───────────────────┘
```

## Prerequisites

- Python 3.9+
- LiveKit Cloud account or self-hosted LiveKit server
- OpenAI API key
- Deepgram API key (for Speech-to-Text)
- Cartesia API key (for Text-to-Speech)
- Qdrant instance (local or cloud)

## Installation

1. **Clone and navigate to the project:**
   ```bash
   cd calling
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys and configuration.

4. **Start Qdrant (if running locally):**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

## Setup

### 1. Initialize RAG Collections

Edit `setup_rag.py` to load your FAQ and CRM data:

```python
# Load FAQ from website
rag_service.load_data_to_qdrant(
    collection_name=FAQ_COLLECTION,
    url_link="https://your-company.com/faq"
)

# Load FAQ from PDF
rag_service.load_data_to_qdrant(
    collection_name=FAQ_COLLECTION,
    pdf_file="path/to/faq.pdf"
)

# Load CRM data from Excel
rag_service.load_data_to_qdrant(
    collection_name=CRM_COLLECTION,
    excel_file="path/to/customers.xlsx"
)
```

Then run the setup:
```bash
python setup_rag.py
```

### 2. Configure LiveKit

Update your `dispatch-rule.json` and `inbound-trunk.json` with your LiveKit configuration.

## Usage

### Start the Agent

```bash
python agent.py start
```

The agent will:
1. Connect to LiveKit
2. Wait for incoming calls
3. Greet callers and offer assistance
4. Use appropriate tools based on conversation

### Available Function Tools

#### 1. **lookup_faq(question: str)**
Searches the FAQ knowledge base using semantic search.

**Features:**
- Returns top 3 relevant answers
- Confidence scoring (escalates if < 70%)
- Automatic escalation on no results

**Example:**
```
Customer: "What are your business hours?"
Agent: [Calls lookup_faq("What are your business hours?")]
```

#### 2. **lookup_customer_crm(customer_identifier: str)**
Retrieves customer information from CRM database.

**Features:**
- Searches by ID, phone, email, or name
- Updates call context with customer info
- Requests verification if not found

**Example:**
```
Customer: "I need help with my account, ID 12345"
Agent: [Calls lookup_customer_crm("12345")]
```

#### 3. **handle_booking_request(service_type: str, preferred_date: str, customer_notes: str)**
Processes booking and appointment requests.

**Features:**
- Generates confirmation numbers
- Stores booking details
- Flags for human confirmation

**Example:**
```
Customer: "I'd like to book a consultation for next Monday"
Agent: [Calls handle_booking_request("consultation", "next Monday", None)]
```

#### 4. **handle_renewal_request(service_name: str, renewal_type: str)**
Manages service renewals.

**Features:**
- Checks customer authentication
- Validates renewal eligibility
- Escalates for payment processing

**Example:**
```
Customer: "I need to renew my premium subscription"
Agent: [Calls handle_renewal_request("premium subscription", "standard")]
```

#### 5. **triage_and_escalate(issue_description: str, urgency: str)**
Intelligently routes and escalates issues.

**Features:**
- Keyword-based escalation logic
- Department routing
- Automatic FAQ lookup for technical issues
- Urgency-based prioritization

**Escalation Categories:**
- Critical: Emergency, fraud, legal issues
- Billing: Payment, refund, billing issues
- Technical: Errors, bugs, not working
- General: All other escalations

**Example:**
```
Customer: "I have an urgent billing dispute"
Agent: [Calls triage_and_escalate("urgent billing dispute", "high")]
```

## Escalation Logic

The agent automatically escalates in these scenarios:

1. **Low Confidence**: FAQ answers with confidence < 70%
2. **No Results**: No relevant information found
3. **Critical Keywords**: Emergency, fraud, legal, security breach
4. **Payment Issues**: Billing, refunds, charges
5. **Customer Request**: Explicitly asks for human agent
6. **Technical Errors**: System failures or exceptions

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_URL` | Qdrant instance URL | `http://localhost:6333` |
| `QDRANT_API_KEY` | Qdrant API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `DEEPGRAM_API_KEY` | Deepgram API key | - |
| `CARTESIA_API_KEY` | Cartesia API key | - |
| `FAQ_COLLECTION_NAME` | FAQ collection name | `faq_knowledge_base` |
| `CRM_COLLECTION_NAME` | CRM collection name | `crm_database` |

### Agent Personality

Modify the `instructions` in `agent.py` to customize the agent's personality and behavior:

```python
agent = TelephonyAgent(
    instructions="""Your custom instructions here..."""
)
```

## Data Sources

The RAG system supports multiple data sources:

- **PDFs**: Product manuals, FAQs, policies
- **Websites**: Company website, help center, documentation
- **Excel**: Customer data, service catalogs, pricing tables

## Production Considerations

### Security
- ✅ Implement proper authentication for CRM lookups
- ✅ Encrypt sensitive customer data
- ✅ Comply with data privacy regulations (GDPR, CCPA)
- ✅ Secure API keys and credentials

### CRM Integration
- Connect to real CRM APIs (Salesforce, HubSpot, etc.)
- Implement proper error handling and retry logic
- Cache frequently accessed data
- Use webhooks for real-time updates

### Booking System
- Integrate with calendar/scheduling APIs
- Implement availability checking
- Send confirmation emails/SMS
- Handle cancellations and rescheduling

### Payment Processing
- Integrate with payment gateways (Stripe, PayPal)
- Implement PCI compliance measures
- Use secure payment links
- Handle refunds and disputes

### Monitoring
- Log all interactions for quality assurance
- Track escalation rates and reasons
- Monitor response times and accuracy
- Set up alerts for system failures

### Performance
- Use async loading for large datasets
- Implement caching for frequently asked questions
- Optimize vector search parameters
- Monitor token usage and costs

## Troubleshooting

### Agent Not Connecting
- Check LiveKit credentials in `.env`
- Verify network connectivity
- Review logs for connection errors

### RAG Not Finding Answers
- Ensure collections are populated: `python setup_rag.py`
- Check Qdrant is running: `curl http://localhost:6333/health`
- Verify data was loaded successfully

### Low Confidence Scores
- Add more training data to collections
- Adjust confidence threshold in `lookup_faq()`
- Improve data quality and chunk sizes

### Function Tools Not Working
- Check tool definitions have proper decorators
- Verify RunContext is imported
- Review agent instructions for tool usage

## Development

### Adding New Function Tools

1. Add method to `TelephonyAgent` class:
```python
@function_tool()
async def your_new_tool(
    self,
    context: RunContext,
    param: str,
) -> dict[str, Any]:
    """Tool description."""
    # Implementation
    return {"status": "success"}
```

2. Update agent instructions to include the new tool

3. Test with sample calls

### Testing

Test individual function tools:
```python
from agent import rag_service

# Test FAQ search
results = rag_service.retrieval_based_search(
    query="your test question",
    collection_name="faq_knowledge_base",
    top_k=3
)
print(results)
```

## Support

For issues and questions:
1. Check logs for error messages
2. Verify all API keys are valid
3. Ensure data is loaded into Qdrant
4. Review LiveKit dashboard for call status

## License

[Your License Here]

## Credits

Built with:
- [LiveKit](https://livekit.io/) - Real-time communication platform
- [OpenAI](https://openai.com/) - LLM and embeddings
- [Qdrant](https://qdrant.tech/) - Vector database
- [Deepgram](https://deepgram.com/) - Speech-to-text
- [Cartesia](https://cartesia.ai/) - Text-to-speech

