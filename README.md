# text2sql-agent 🚀

A powerful text-to-SQL agent that converts natural language queries into SQL statements using LangGraph and LangChain

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

## 🧪 Testing

Run all tests:

```bash
uv run pytest tests/
```

Run specific test categories:

- **Unit tests** (single nodes and utilities):
  ```bash
  uv run pytest -m single_node
  uv run pytest -m utils
  ```

- **Integration tests**:
  ```bash
  uv run pytest -m integration
  ```

- **Offline evaluations** (agent performance evaluation):
  ```bash
  uv run pytest -m evaluator
  ```

### GitHub Actions Environment Setup

If you enable the GitHub Actions workflow, make sure to set the following environment variable in your repository secrets:

- **`OPENAI_API_KEY`**: Your OpenAI API key
- **`LANGSMITH_API_KEY`**: Your LangSmith API key
- **`LANGSMITH_TRACING=true`**: Enable LangSmith tracing


The workflow will automatically run tests and evaluations on pull requests and pushes to main/develop branches

## 🔄 CI/CD Pipeline

CI/CD pipeline to ensure quality and reliability through multiple testing layers and evaluations

```mermaid
graph TD
    A1[Code or Graph Change] --> B1[Trigger CI Pipeline]
    A2[Prompt Commit in PromptHub] --> B1
    A3[Online Evaluation Alert] --> B1

    B1 --> C1[Run Unit Tests on Nodes]
    B1 --> C2[Run Integration Tests]
    B1 --> C3[Run End to End Tests on Graph]

    C1 --> D1[Run Offline Evaluations]
    C2 --> D1
    C3 --> D1

    D1 --> E1[Evaluate with OpenEvals or AgentEvals]
    D1 --> E2[Assertions: Hard and Soft]

    E1 --> F1[Push to Staging Deployment - Spin new Docker deployment in LGP as Development Type]
    E2 --> F1

    F1 --> G1[Run Online Evaluations on Live Data]
    G1 --> H1[Attach Scores to Traces]

    H1 --> I1[If Quality Below Threshold]
    I1 --> J1[Send to Annotation Queue]
    I1 --> J2[Trigger Alert via Webhook]
    I1 --> J3[Push Trace to Golden Dataset]

    F1 --> K1[Promote to Production if All Pass - Spin Production Deployment in LGP]

    J2 --> L1[Slack or PagerDuty Notification]

    subgraph Manual Review
        J1 --> M1[Human Labeling]
        M1 --> J3
    end

```

### Pipeline Stages

1. **Trigger Sources**: Code changes, graph modifications, prompt updates, or online evaluation alerts
2. **Testing Layers**: Unit tests for individual nodes, integration tests, and end-to-end graph testing
3. **Evaluation**: Offline evaluations using OpenEvals/AgentEvals with hard and soft assertions
4. **Staging**: Deployment to staging environment for live data testing
5. **Quality Gates**: Online evaluations on production-like data with trace scoring
6. **Production**: Promotion to production if all quality thresholds are met
7. **Monitoring**: Continuous monitoring with alerts and manual review processes

## 📚 Examples

Check out the `examples/` directory for usage examples and demonstrations of the text-to-SQL agent capabilities.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
