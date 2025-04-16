# DB Assistant

A database assistant powered by OpenAI that helps you interact with your databases using natural language.

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd dbassistant
   ```

2. Install the package in development mode:
   ```
   pip install -e .
   ```

3. Create a `.env` file with your OpenAI API key and database connection string:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DB_URI=your_database_connection_string
   ```

## Usage

### Important: First-time Setup

When setting up the tool for the first time with a new database, you should run the Database Explorer first. This tool will explore your database schema and create the necessary context files for the assistant to work properly:

```
python -m scripts.run_dbexplorer
```

The Database Explorer will analyze your database structure and generate helpful context for the assistant, including table summaries and relationships.

### Running the Database Assistant

After running the Database Explorer, you can run the assistant in two ways:

1. Using the entry point script:
   ```
   python run_assistant.py
   ```

2. As a module:
   ```
   python -m scripts.run_dbassistant
   ```

## Features

- Natural language interaction with your database
- Data visualization capabilities
- SQL query generation and execution
- Table schema exploration