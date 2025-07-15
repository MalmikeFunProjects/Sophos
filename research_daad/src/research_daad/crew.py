import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from research_daad.src.research_daad.tools.daad_scraper_handler import scrape_daad_scholarships
from typing import Any, Dict, List, Optional

from research_daad.src.research_daad.utils.llm_handler import LLMHandler
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators



@CrewBase
class ResearchDaad():
    """ResearchDaad crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the crew with optional LLM configuration.

        Args:
            llm_config: Dictionary containing LLM configuration
                Format: {
                    'provider': 'openai',  # or 'anthropic', 'google', 'ollama'
                    'model': 'gpt-4',      # specific model name
                    'temperature': 0.1,    # additional parameters
                    'max_tokens': 3000
                }
        """
        super().__init__()
        self.llm_config = llm_config or self._get_default_llm_config()
        self.llm_handler = LLMHandler.from_config(self.llm_config.copy())
        self.llm = self.llm_handler.get_llm()

    def _get_default_llm_config(self) -> Dict[str, Any]:
        """Get default LLM configuration from environment or use OpenAI as fallback."""
        # Check for environment variables to set default provider
        provider = os.getenv('DEFAULT_LLM_PROVIDER', 'openai').lower()
        model = os.getenv('DEFAULT_LLM_MODEL', None)

        config = {
            'provider': provider,
            'temperature': float(os.getenv('LLM_TEMPERATURE', '0.1')),
            'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '3000'))
        }

        if model:
            config['model'] = model

        return config

    def get_llm(self):
        """Get the configured LLM instance."""
        return self.llm_handler.get_llm()

    def update_llm_config(self, new_config: Dict[str, Any]):
        """Update LLM configuration and recreate handler."""
        self.llm_config.update(new_config)
        self.llm_handler = LLMHandler.from_config(self.llm_config.copy())

    @agent
    def scraper(self) -> Agent:
        """Creates the DAAD scholarship scraper agent"""
        return Agent(
            config=self.agents_config['scraper'],
            tools=[scrape_daad_scholarships],
            verbose=True,
            allow_delegate=False,
            llm=self.llm
        )

    @agent
    def cleaner(self) -> Agent:
        """Creates the scholarship cleaner agent"""
        return Agent(
            config=self.agents_config['cleaner'],
            verbose=True,
            llm=self.llm
        )

    @agent
    def writer(self) -> Agent:
        """Creates the scholarship writer agent"""
        return Agent(
            config=self.agents_config['writer'],
            verbose=True,
            llm=self.llm
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def scraper_task(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_task'],
        )

    @task
    def cleaner_task(self) -> Task:
        return Task(
            config=self.tasks_config['clean_task'],
        )


    @task
    def writer_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_task'],
            output_file='scholarships.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ResearchDaad crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
