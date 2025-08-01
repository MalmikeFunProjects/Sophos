# ResearchDaad Crew

Welcome to the ResearchDaad Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

## Customizing
### Modifying environment variables
**Copy .env.example into .env**
Using google gemini (free model).
- Add your path to google `GOOGLE_APPLICATION_CREDENTIALS`
- Add your google api key `GOOGLE_API_KEY`
- Set default llm provider to `google`
- Set default llm model to `gemini-2.0-flash-lite`

### Customizing the project
- Modify `src/research_daad/config/agents.yaml` to define your agents
- Modify `src/research_daad/config/tasks.yaml` to define your tasks
- Modify `src/research_daad/crew.py` to add your own logic, tools and specific args
- Modify `src/research_daad/main.py` to add custom inputs for your agents and tasks
- Modify `src/research_daad/tools/**` to add your own tools

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
python src/research_daad/main.py
```

This command initializes the research-daad Crew, assembling the agents and assigning them tasks as defined in the configuration.

This example, will run the create a `scholarship.md` file with the output of a research on LLMs in the root folder.

### Running the scraper separately
```bash
python src/research_daad/tools/daad_scraper.py
```
This will create a file `daad_scholarships.json` containing the scraped data

## Understanding Your Crew

The research-daad Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the ResearchDaad Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
