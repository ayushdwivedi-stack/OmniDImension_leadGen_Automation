# CRM Automation - OmniDimension Call Dispatcher

Automated system that monitors a CSV file for new leads and automatically dispatches calls via OmniDimension's API.

## Features

- 📊 Monitors input CSV for new leads in real-time
- 📞 Automatically dispatches calls via OmniDimension API
- ✅ Tracks processed leads to avoid duplicates
- ⚙️ Configurable polling interval
- 🚀 Simple and lightweight

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
OMNIDIM_API_KEY=your_api_key_here
AGENT_ID=your_agent_id_here

INPUT_CSV_PATH=leads_input.csv
POLL_INTERVAL=10
```

**Configuration Options:**
- `OMNIDIM_API_KEY`: Your API key from OmniDim dashboard (required)
- `AGENT_ID`: Your agent/assistant ID - numeric ID (required)
- `INPUT_CSV_PATH`: Path to input CSV file (default: `leads_input.csv`)
- `POLL_INTERVAL`: Seconds between checks for new leads (default: `10`)

## Usage

### Input CSV Format

Your input CSV file should have the "phone_number"  column rest are optional, for eg:-

| Column | Required | Description |
|--------------|----------|-------------|
| phone_number | Yes      | Phone number with country code (e.g., +918376069116) |
| name         | Optional | Lead's name  |
| email        | Optional | Lead's email |

**Example CSV:**

```csv
lead_id,phone_number,name,email
1,+918376069116,John Doe,john@example.com
2,+919873815099,Jane Smith,jane@example.com
```

### Running the Automation

```bash
python automation.py
```

**What happens:**
1. Monitors the input CSV file continuously
2. Detects new leads (by checking lead_id)
3. Dispatches a call for each new lead
4. Marks the lead as processed to avoid duplicate calls
5. Waits 2 seconds between calls to avoid rate limits

### Adding New Leads

Simply add new rows to your input CSV file. The automation will automatically detect and process them within the polling interval.

## API Integration

This implementation makes direct HTTP calls to the OmniDimension API:

**Endpoint:** `POST https://backend.omnidim.io/api/v1/calls/dispatch`

**Authentication:** Bearer token (your API key)

**Payload:**
```json
{
  "agent_id": 12345,
  "to_number": "+918376069116",
  "call_context": {
    "customer_name": "John Doe",
    "email": "john@example.com",
    "lead_id": "1"
  }
}
```

## Best Practices

- ✅ Test with a small batch of leads first
- ✅ Ensure phone numbers include country codes
- ✅ Keep the CSV file accessible to the automation script
- ✅ Monitor the console output for any errors
- ✅ Ensure you have consent for automated calls
- ✅ Comply with Do-Not-Call regulations
