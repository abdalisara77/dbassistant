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

You can run the assistant in two ways:

1. Using the entry point script:
   ```
   python run_assistant.py
   ```

2. As a module:
   ```
   python -m dbassistant.scripts.run_dbassistant
   ```

## Features

- Natural language interaction with your database
- Data visualization capabilities
- SQL query generation and execution
- Table schema exploration