# DB Assistant

An Open-Source Text-to-SQL Library for Analyzing and Visualizing Data in Large Databases.

## Why Use DBAssistant Instead of Other Tools?

- **Speed Through Adaptive Learning**: In larger databases, agents often require multiple attempts to identify correct schemata and tables. DBAssistant accelerates future requests by **learning from prior interactions**. With user feedback, it refines its understanding of schemas and tables, reducing redundant steps and delivering faster results over time.
- **Accuracy via Focused Architecture**: Unlike most tools that rely on complex multi-agent orchestration, DBAssistant has a **streamlined single-agent design**. By mechanistically curating the model's context window with relevant information, it minimizes errors caused by too many degrees of freedom. This approach works best, especially in large and complex or poorly documented databases.

## How DBAssistant Works

DBAssistant combines OpenAI's Assistant API function calling abilities along with a code execution environment.

### Phase 1: Initial Database Exploration

Upon connecting to a database, DBAssistant performs an automated analysis that includes:

- **Schema Summarization**: Generates concise summary files for each schema, explaining its purpose and the role of its tables.
- **Assistant Description**: Writes a one-line summary of each schema to use for the assistant's initial context during a user request.

### Phase 2: Handling User Requests

![DBAssistant workflow diagram](/dbdiag.svg)

When a user submits a query, DBAssistant follows a structured, collaborative process:

1. **Schema Identification**: Identifies relevant schemas for the task and confirms selections with the user. Once the user confirms, the program injects pre-generated schema summaries into the context window to guide the agent.
2. **Table Selection**: Chooses specific tables based on the enriched context and asks for user approval.
3. **Query Execution**: Generates and runs the SQL query, saving results locally (or via OpenAI's Code Interpreter) to preserve context space.
4. **Data Processing & Visualization**: Uses code execution to analyze results, creating tables, graphs, or other outputs as requested.
5. **Continuous Learning**: Before the thread is closed, the assistant is automatically prompted to tell the user what it learned about each schema. If the user approves, the new learnings are added to the pre-generated schema summaries and used in the next runs.

## Features

- Natural language interaction with your database
- Data visualization capabilities
- SQL query generation and execution
- Table schema exploration

## Installation

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd dbassistant
   ```

2. Install the package in development mode:

   ```bash
   pip install -e .
   ```

3. Create a `.env` file with your OpenAI API key and database connection string:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   DB_URI=your_database_connection_string
   ```

## Usage

### Important: First-Time Setup

When setting up the tool for the first time with a new database, you should run the Database Explorer first. This tool will explore your database schema and create the necessary context files for the assistant to work properly:

```bash
python -m scripts.run_dbexplorer
```

The Database Explorer will analyze your database structure and generate helpful context for the assistant, including table summaries and relationships.

### Running the Database Assistant

After running the Database Explorer, you can run the assistant in two ways:

1. Using the entry point script:

   ```bash
   python run_assistant.py
   ```

2. As a module:

   ```bash
   python -m scripts.run_dbassistant
   ```
