# 🤖 PLATEFUL (Food Donation Assistant Chatbot)

A conversational AI assistant to help connect food donors with recipients, featuring automated logging to Google Sheets. This bot uses natural language to find nearby organizations and streamlines the donation process.

![Demo GIF](https://your-gif-url-here.com/demo.gif)
*A short demo showing the chatbot in action.*

---

## ✨ Features

-   **Natural Language Conversations**: Powered by Google's Gemini Pro and LangChain for intelligent, human-like interactions.
-   **Real-time Organization Search**: Uses the Google Places API to find nearby food banks, charities, and shelters.
-   **Detailed Contact Information**: Fetches phone numbers and websites for easy follow-up.
-   **Automated Google Sheets Logging**: Creates a new row for each identified NGO, pairing it with the donor's details for clear record-keeping.
-   **Stateful Conversation Flow**: Remembers context to guide users through multi-step processes like providing their details.
-   **Easy Setup**: Includes helper scripts and clear instructions for environment and credential setup.

---

## 🔧 Technology Stack

-   **Backend**: Python 3.8+
-   **AI & NLP**: LangChain, LangGraph, Google Gemini Pro
-   **APIs**: Google Places API, Google Geocoding API, Google Sheets API, Google Drive API
-   **Data Logging**: `gspread` for Google Sheets integration

---

## 🚀 Setup and Installation

Follow these steps to get your own instance of the chatbot running locally.

### 1. Prerequisites

-   Python 3.8 or higher
-   Git
-   A Google Cloud Platform (GCP) account

### 2. Clone the Repository

```bash
git clone [https://github.com/your-username/food-donation-chatbot.git](https://github.com/your-username/food-donation-chatbot.git)
cd food-donation-chatbot
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### 4. Install Dependencies

Create a `requirements.txt` file with the following content:

```text
# requirements.txt
googlemaps>=4.10.0
gspread>=5.12.0
oauth2client>=4.1.3
langchain>=0.1.0
langchain-google-genai>=1.0.0
langgraph>=0.0.40
langchain-core>=0.1.0
python-dotenv>=1.0.0
```

Now, install all the packages:
```bash
pip install -r requirements.txt
```

### 5. Google Cloud & API Setup

This is the most critical step.

#### **A. Enable APIs**
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  Enable the following APIs for your project:
    -   **Places API**
    -   **Geocoding API**
    -   **Generative Language API** (or Vertex AI API)
    -   **Google Drive API**
    -   **Google Sheets API**

#### **B. Create API Key**
1.  In the GCP Console, go to **Credentials**.
2.  Click **+ CREATE CREDENTIALS** -> **API key**.
3.  Copy this key. This will be your `GOOGLE_API_KEY`.

#### **C. Create Service Account for Google Sheets**
1.  In **Credentials**, create a new **Service Account**.
2.  Give it a name (e.g., `sheets-editor`) and grant it the **Editor** role.
3.  Open the newly created service account, go to the **KEYS** tab.
4.  Click **ADD KEY** -> **Create new key** -> **JSON**.
5.  A JSON file will be downloaded. **Rename this file to `service_account.json`** and place it in the root of your project folder.

#### **D. Configure the Google Sheet**
1.  Create a new sheet in [Google Sheets](https://sheets.google.com/).
2.  Open the `service_account.json` file and copy the `client_email` value.
3.  Click the **Share** button on your Google Sheet and share it with that email, giving it **Editor** permissions.
4.  From the sheet's URL, copy the **Spreadsheet ID**.

### 6. Configure Environment Variables

Create a file named `.env` in the root of your project folder. Paste the following into it and replace the placeholder values with your actual credentials.

```text
# .env
GOOGLE_API_KEY="paste-your-api-key-here"
GOOGLE_SHEET_ID="paste-your-spreadsheet-id-here"
```

The script is already configured to load these variables automatically.

### 7. Run the Chatbot

You're all set! Run the main script from your terminal:
```bash
python main.py
```

---

## 💬 Usage

Once the bot is running, simply start the conversation naturally. Here are some examples:

-   `"I want to donate food in New Delhi"`
-   `"Where can I find a food bank in Bangalore?"`
-   `"Find donation centers near me in Mumbai"`

The bot will guide you through the process of finding organizations and logging the request.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for bugs, feature requests, or improvements.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
