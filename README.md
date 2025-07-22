# text2sql-agent 🚀

A powerful text-to-SQL agent that converts natural language queries into SQL statements using LangGraph and LangChain.

## 🛠️ Prerequisites

- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

## 🚀 Quick Start

### 1. Install Dependencies

First, ensure you have `uv` installed. Then run:

```bash
uv sync
```

This will create a virtual environment and install all project dependencies.

### 2. Environment Configuration

Copy the example environment file and configure your variables:

```bash
cp .env.example .env
```

Edit the `.env` file and add your required environment variables.

### 3. Run LangGraph Studio

Start the LangGraph development server to visualize your agent:

```bash
uv run langgraph dev
```

This will start the LangGraph Studio interface where you can interact with and debug your text-to-SQL agent.

## 📁 Project Structure

```
text2sql-agent/
├── agents/           # Agent implementations
├── examples/         # Usage examples
├── helpers/          # Utility functions
└── langgraph.json    # LangGraph configuration
```

## 🔧 Development

- **Virtual Environment**: Managed by `uv` - no need to manually activate
- **Dependencies**: All managed through `pyproject.toml` and `uv.lock`
- **Environment Variables**: Configure in `.env` file

## 📚 Examples

Check out the `examples/` directory for usage examples and demonstrations of the text-to-SQL agent capabilities.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

