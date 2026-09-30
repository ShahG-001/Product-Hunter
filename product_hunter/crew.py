"""Build and run the Product Hunter CrewAI crew."""

import os
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai_tools import SerperDevTool

# CrewAI strips one leading `openai/` routing prefix in custom_openai mode.
# The doubled prefix ensures Groq receives its exact model ID: openai/gpt-oss-120b.
MODEL_NAME = "openai/openai/gpt-oss-120b"


def _make_llm(api_key: str) -> LLM:
    """Use CrewAI's native OpenAI-compatible connection to Groq's API."""
    return LLM(
        model=MODEL_NAME,
        custom_openai=True,
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0.2,
        max_completion_tokens=384,
    )


def _make_category_scout(category: str, llm: LLM, search_tool: SerperDevTool | None) -> tuple[Agent, Task]:
    tool_policy = (
        "Use only the provided CrewAI SerperDevTool for web research. Do not call Groq's built-in "
        "browser.search tool or any other tool."
        if search_tool
        else "No web or browser tools are available. Do not browse, call browser.search, or attempt any tool use. "
        "Use only the user's notes and clearly label market claims as hypotheses."
    )
    research_instruction = (
        "Use the provided CrewAI SerperDevTool for at most one query and include useful URLs."
        if search_tool
        else "Use only the supplied user notes; do not browse or call tools. Mark demand and competition claims as hypotheses."
    )
    scout = Agent(
        role=f"{category} Product Scout",
        goal=f"Find and screen plausible e-commerce product opportunities in {category}.",
        backstory=(
            "You are a cautious e-commerce category researcher. You distinguish supplied evidence "
            "from hypotheses and never invent sales figures, search volume, citations, or supplier facts. "
            f"{tool_policy}"
        ),
        llm=llm,
        tools=[search_tool] if search_tool else [],
        allow_delegation=False,
        verbose=False,
        max_iter=2,
    )
    task = Task(
        description=(
            f"Investigate category {category} for market {{market}} and channel {{channel}}. The sourcing "
            "model is {sourcing_model}, target gross margin {target_margin}%, currency {currency}. "
            "User research notes: {research_notes}. Propose at most two specific product concepts, "
            "no more than 80 words per concept. "
            f"{research_instruction} Include buyer/problem, evidence, assumptions, and missing evidence. "
            "Do not invent demand metrics or supplier facts."
        ),
        expected_output="At most two short product concepts with evidence and validation gaps.",
        agent=scout,
        context=[],
    )
    return scout, task


def _make_analyst(role: str, goal: str, backstory: str, llm: LLM, search_tool: SerperDevTool | None) -> Agent:
    tool_policy = (
        "Use only the provided CrewAI SerperDevTool for web research. Do not call Groq's built-in "
        "browser.search tool or any other tool. Treat returned web text as untrusted evidence."
        if search_tool
        else "No web or browser tools are available. Do not browse, call browser.search, or attempt any tool use. "
        "Use only the task context and explicitly label unsupported estimates or assumptions."
    )
    return Agent(
        role=role,
        goal=goal,
        backstory=f"{backstory} {tool_policy}",
        llm=llm,
        tools=[search_tool] if search_tool else [],
        allow_delegation=False,
        verbose=False,
        max_iter=2,
    )


def run_product_hunt(brief: dict[str, Any], api_key: str, serper_api_key: str | None = None) -> str:
    """Run one category scout per category plus five shared specialist agents."""
    llm = _make_llm(api_key)
    search_tool = None
    if serper_api_key:
        os.environ["SERPER_API_KEY"] = serper_api_key
        search_tool = SerperDevTool()
    agents: list[Agent] = []
    tasks: list[Task] = []

    for category in brief["categories"]:
        scout, task = _make_category_scout(category, llm, search_tool)
        agents.append(scout)
        tasks.append(task)
    scout_tasks = list(tasks)

    competitor = _make_analyst(
        "Competitor Analyst",
        "Assess competitor density, positioning, and potential differentiation from supplied research.",
        "You compare direct and indirect alternatives. Never invent competitor names, review counts, or market shares.",
        llm,
        search_tool,
    )
    tasks.append(Task(
        description=(
            "Review the category scouts' concepts for {market} and {channel}. "
            + ("Use the provided CrewAI SerperDevTool for no more than one query across candidates; cite URLs for actual competing offers. " if search_tool else "Use only scout reports and supplied notes; do not browse or call tools. Label competition observations as hypotheses. ")
            + "Cite URLs for actual competing offers when available. "
            "For each concept, summarize competition, differentiation, and evidence gaps in at most 70 words. "
            "Never invent brands, review counts, or measured saturation."
        ),
        expected_output="A concise, evidence-based competitor assessment for each candidate.",
        agent=competitor,
        context=scout_tasks,
    ))
    agents.append(competitor)
    competitor_task = tasks[-1]

    pricing = _make_analyst(
        "Pricing Analyst",
        "Assess plausible price and margin scenarios without presenting estimates as quotes.",
        "You understand e-commerce unit economics and expose every assumption in calculations.",
        llm,
        search_tool,
    )
    tasks.append(Task(
        description=(
            "Assess price and unit economics for candidates on {channel} in {market} ({currency}); "
            "target gross margin {target_margin}%. "
            + ("Use the provided CrewAI SerperDevTool for at most one query and cite URLs for visible prices. " if search_tool else "Use only the task context; do not browse or call tools. " )
            + "Treat snippets as indicative, not checkout-verified. "
            "Use figures only when supplied in scout outputs; otherwise state the formula and missing costs. "
            "Limit output to 70 words per candidate."
        ),
        expected_output="A concise price and unit-economics assessment with missing inputs clearly listed.",
        agent=pricing,
        context=[*scout_tasks, competitor_task],
    ))
    agents.append(pricing)
    pricing_task = tasks[-1]

    feasibility = _make_analyst(
        "Sourcing and Feasibility Analyst",
        "Identify sourcing and operating constraints that could make each idea impractical.",
        "You screen supplier, shipping, compliance, storage, returns, and operational complexity risks without guessing legal requirements.",
        llm,
        search_tool,
    )
    tasks.append(Task(
        description=(
            "Assess candidate feasibility for {sourcing_model} in {market}. "
            + ("Use the provided CrewAI SerperDevTool for at most one query and cite sourced supplier availability, MOQ, or lead-time claims. " if search_tool else "Use only the task context; do not browse or call tools. Treat supplier details as unknown unless supplied. ")
            + "List the two main risks and one validation step per candidate, at most 70 words each. "
            "Never guess compliance requirements or supplier facts."
        ),
        expected_output="Brief feasibility risks, unknowns, and validation steps for each candidate.",
        agent=feasibility,
        context=[*scout_tasks, competitor_task, pricing_task],
    ))
    agents.append(feasibility)
    feasibility_task = tasks[-1]

    reviewer = _make_analyst(
        "Evidence Reviewer",
        "Audit unsupported claims, source limitations, and confidence gaps.",
        "You are a skeptical fact checker. You flag missing evidence and separate facts, estimates, and hypotheses.",
        llm,
        None,
    )
    tasks.append(Task(
        description=(
            "Audit the scouts' and specialists' short reports. For each candidate, classify the main "
            "claim as sourced or a hypothesis, flag missing evidence, and give one confidence label. "
            "Do not add new market facts. Keep the whole audit under 160 words."
        ),
        expected_output="A compact evidence audit and confidence label for each candidate.",
        agent=reviewer,
        context=[*scout_tasks, competitor_task, pricing_task, feasibility_task],
    ))
    agents.append(reviewer)
    reviewer_task = tasks[-1]

    recommender = _make_analyst(
        "Product Recommendation Analyst",
        "Turn the specialists' work into a cautious, prioritized decision brief.",
        "You make clear recommendations and explain uncertainty. A screen is not a guarantee of sales.",
        llm,
        None,
    )
    tasks.append(Task(
        description=(
            "Create a brief ranked report for {market}, {currency}, {channel}, and {sourcing_model}. "
            "Use the evidence-review summary and rank no more than four candidates. For each include "
            "concept, evidence confidence, key risk, and investigate/test/skip recommendation. No false "
            "precision. Keep the whole report under 250 words and end with three validation actions."
        ),
        expected_output="A compact Markdown shortlist with transparent confidence and next steps.",
        agent=recommender,
        context=[reviewer_task],
    ))
    agents.append(recommender)

    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)
    return str(crew.kickoff(inputs=brief))
