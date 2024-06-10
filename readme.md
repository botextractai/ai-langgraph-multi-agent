# Multi AI agent system for report writing with LangGraph

This multi-agent example uses OpenAI's ChatGPT 4 model and the LangChain Tavily search tool to write a report about the latest inflation figures in the European Union.

Unlike web search tools, the LangChain Tavily search tool delivers actual search results, rather than just links or raw web (HTML) pages.

This example uses a total of 5 LangGraph agents (nodes). LangGraph is a library for building stateful, multi-agent applications with Large Language Models (LLMs), built on top of (and intended to be used with) LangChain. LangGraph describes and orchestrates agent control flows.

- LangGraph is an extension of LangChain that supports graphs
- Single and multi-agent flows are described and represented as graphs
- LangGraph allows for extremely controlled "flows"
- Built-in persistence allows for "human in the loop" workflows

In this example, each of the 5 agents plays a different role:

1. "plan"
2. "research_plan"
3. "generate"
4. "reflect"
5. "research_critique"

The workflow of this example starts with the "plan" agent (1). This agent defines the task along with any relevant notes or instructions.

The "reseach_plan" agent (2) is then charged with providing information that can be used to write the report. This agent generates a list of search queries that gather relevant information using the Taviliy search tool. It does generate a maximum of 3 queries.

The "generate" agent (3) then writes the actual report. If this agent is called for the first time, then it writes the initial draft to be passed on to the "reflect" agent (4). If this agent is called in later iterations ("revisions"), it also incorporates the feedback provided by the following two agents (4 and 5). The number of revisions can be set in the `main.py` script with the `max_revisions` setting. The default value is 2, which means that the workflow just does 1 full revision loop (including agents 4 and 5).

After the "generate" agent (3), the workflow checks, if the maximum number of revisions (`max_revisions`), has been reached. If yes, then the answer from the "generate" agent (3) is considered final and the workflow gets terminated. If not, then the answer from the "generate" agent (3) is passed on to the "reflect" agent (4) for a loop that includes agents 4 and 5.

The "reflect" agent (4) then makes suggestions on how that the current report can be improved.

The "research_critique" agent (5) then provides additional search queries for the Tavily search tool to collect additional relevant information. It does generate a maximum of 3 queries.

After this, the "generate" agent (3) gets called again to write an improved version of the report that incorporates the additional suggestions and information.

You need an OpenAI API key for this example. [Get your OpenAI API key here](https://platform.openai.com/login). You can insert your OpenAI API key in the `main.py` script, or you can supply your OpenAI API key either via the `.env` file, or through an environment variable called `OPENAI_API_KEY`. If you don't want to use an OpenAI model, then you can also use other models, including local models.

You also need a free Tavily API key for this example. [Get your free Tavily API key here](https://app.tavily.com/sign-in). You can insert your Tavily API key in the `main.py` script, or you can supply your Tavily API key either via the `.env` file, or through an environment variable called `TAVILY_API_KEY`.

| >>>>> The final answer will look similar to this example: <<<<< |
| --------------------------------------------------------------- |

## Report on the Latest Inflation Figures in the European Union

### 1. Introduction

Inflation represents the rate at which the general level of prices for goods and services rises, eroding purchasing power. In the context of the European Union (EU), monitoring inflation is crucial due to its direct impact on citizens' cost of living, monetary policy, and overall economic stability.

### 2. Methodology

This report utilizes data primarily sourced from Eurostat and the European Central Bank (ECB). Inflation rates are calculated using the Harmonised Index of Consumer Prices (HICP), which provides a consistent method for comparing inflation rates across EU member states.

### 3. Current Inflation Trends in the European Union

As of November 2023, the inflation rate in the EU stood at 3.6%. This represents a slight decrease from the peak rates observed in late 2022 but remains above the ECB's target of 2%. Graphical trends indicate a gradual stabilization of prices, although certain categories remain volatile.

### 4. Analysis by Country

- **Germany**: Reported a moderate inflation rate of 3.2%, reflecting robust monetary policies.
- **France**: Inflation here is slightly higher at 3.8%, influenced by rising food prices.
- **Italy and Spain**: These countries show varied rates of 4.1% and 3.9% respectively, driven by differences in energy costs and domestic demand.
- **Hungary**: Stands out with a significantly higher rate of 9.6%, attributed to external economic pressures and fiscal policies.

### 5. Sectoral Analysis

- **Energy**: Despite global reductions in energy prices, this sector shows elevated inflation levels due to previous supply constraints.
- **Food**: High inflation persists in this sector, impacted by adverse weather conditions and global supply chain disruptions.
- **Services**: Inflation in services has been relatively stable, reflecting slower recovery in consumer demand post-pandemic.

### 6. Impact of Inflation

The sustained higher inflation rates have eroded consumer purchasing power, particularly affecting lower-income households. In response, the ECB has adjusted interest rates to temper inflation, influencing borrowing costs and economic growth.

### 7. Comparative Analysis

When compared to major economies like the US (inflation at 4.1%) and the UK (inflation at 4.5%), the EU's inflation rate is relatively lower, reflecting tighter monetary controls and differing impacts from global economic conditions.

### 8. Future Outlook

Economic forecasts suggest a gradual decrease in inflation rates within the EU, approaching the target of 2% by late 2025. This outlook assumes continued economic recovery and stability in energy prices. However, geopolitical tensions and supply chain issues pose potential risks.

### 9. Conclusion

The EU faces a complex inflation landscape, influenced by both internal policies and external factors. Policymakers must continue to balance growth with inflation control, adapting strategies as global economic conditions evolve.

### 10. Appendices and References

- **Appendix A**: Inflation Rate Charts by Country
- **Appendix B**: Sectoral Inflation Analysis
- **References**: A comprehensive list of data sources from Eurostat, ECB, and other economic research bodies.

This structured analysis provides a detailed overview of the current inflation dynamics within the EU, offering insights that can guide economic decision-making and policy formulation.
