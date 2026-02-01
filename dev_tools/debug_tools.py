import asyncio
import json
from config.config_loader import load_config
from agent.session_manager import Session

async def main():
    config = load_config(None)
    session = Session(config)
    await session.initialize()

    schemas = session.tool_registry.get_schemas()

    # Find write_file tool
    for schema in schemas:
        if schema["name"] == "write_file":
            print("write_file schema:")
            print(json.dumps(schema, indent=2))
            break

if __name__ == "__main__":
    asyncio.run(main())
