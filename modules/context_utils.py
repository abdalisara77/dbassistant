

def get_dbexplorer_context_toolkit():
    return {
        "get_context_for_schemata": get_context_for_schemata,
        "create_context_file": create_context_file,
        "add_context_to_file": add_context_to_file,
        "add_schema_one_liners": add_schema_one_liners
    }


def get_dbassistant_context_toolkit():
    return {
        "get_context_for_schemata": get_context_for_schemata,
        "add_context_to_file": add_context_to_file,
    }


def get_context_for_schemata(schemata: list[str]):
    context = ""
    for schema in schemata:
        # read the schema context from context_files
        schema_file = f"context_files/{schema}.txt"
        with open(schema_file, "r") as f:
            schema_context = f.read()
        context = context + f"\n schema name: '{schema}'" + schema_context

    return context


def create_context_file(schema: str, context: str):
    with open(f"context_files/{schema}.txt", "w") as f:
        f.write(context)
    return


def add_context_to_file(schema: str, context: str):
    with open(f"context_files/{schema}.txt", "a") as f:
        f.write(context)
    return


def add_schema_one_liners(oneliner: str):
    with open(f"instructions/db_assistant_instructs.txt", "a") as f:
        f.write(oneliner)
    return


