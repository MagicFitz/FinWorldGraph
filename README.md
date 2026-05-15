# FinWorldGraph

## Mission Shift

The pipeline center is now **"compiling an agent-perceivable world state"** rather than only building a financial graph.

Old framing:

```text
News → Event Extraction → WorldGraph → GNN → Agent → Market Simulation
```

New framing:

```text
Heterogeneous Texts + Market Observations + Agent Context
        ↓
Agent-Conditioned World-State Compilation
        ↓
Shared World State W_t + Agent-specific PerceptionPack P_{a,t}
        ↓
Belief Update / Action / Simulation Evaluation
```

**Core transition:** WorldGraph becomes an intermediate representation in world-state compilation; **PerceptionPack** is a key task output.

## Task Definition

Given:

- `D_{<=t}`: multi-source financial texts (news, announcements, commentary, reports, social posts)
- `M_{<=t}`: market observations (price, volume, volatility, sector moves)
- `A`: heterogeneous agents (profiles, portfolios, memory, network positions, access rights)

Output:

- `W_t`: shared temporal world state
- `P_{a,t}`: agent-conditioned perception pack

## 9-Layer Pipeline

1. **Layer 0: Task Configuration**
   - Defines simulation window, universe, and heterogeneous agent set.
   - Agent heterogeneity is configured from role + portfolio + memory + network position + source access.

2. **Layer 1: Raw Data Collection**
   - Textual Evidence Stream
   - Market Observation Stream
   - Entity Backbone
   - Agent Context
   - Market data is treated as part of state (e.g., `MarketMove` nodes), not only as labels.

3. **Layer 2: Document Normalization**
   - Converts source documents to standardized evidence units.
   - Required fields include `publish_time`, `crawl_time`, `source_type`, `source_reliability`, `visible_to`, and `time_validity`.

4. **Layer 3: Text-to-Frame Extraction**
   - Extracts `EntityFrame`, `EventFrame`, `RelationFrame`, and `NarrativeFrame`.
   - Repositions extraction as **Text-to-State Frame Extraction**.

5. **Layer 4: Event Canonicalization**
   - Consolidates document-level mentions into canonical temporal events.
   - Includes event coreference, temporal grounding, and uncertainty aggregation.

6. **Layer 5: World-State Compilation**
   - Compiles shared world state rather than "building a knowledge graph".
   - Supports both:
     - append-only Event Log
     - Temporal Heterogeneous Graph snapshot

7. **Layer 6: Agent-Conditioned Projection**
   - Projects `W_t` to `P_{a,t}` via:

     ```text
     P_{a,t} = Π(W_t, C_a, H_{a,<t})
     ```

   - `PerceptionPack` is structured, evidence-grounded, and explains visibility/salience/hidden information.

8. **Layer 7: Simulation Interface**
   - Agent consumes `PerceptionPack` (not raw text).
   - Decision pipeline is separated into:
     - belief update
     - action decision

9. **Layer 8: Evaluation & Trace Logging**
   - Three evaluation levels:
     - Compilation quality (`D_{<=t} -> W_t`)
     - Perception utility (`W_t -> P_{a,t}`)
     - Simulation validity (`P_{a,t} -> belief/action/outcome`)

## Legacy-to-New Module Mapping

| Legacy Module | New Position | Notes |
| --- | --- | --- |
| News2WorldGraph | Text-to-State Frame Extractor | Extract entities/events/relations/narratives |
| FinanceGraph | Entity Backbone / Market Entity Layer | Base entities for companies, instruments, sectors, ETFs |
| News-Price-Connector | Event-MarketMove Grounder | Link events and observed market moves; avoid overclaiming causality |
| WorldGraph | Shared Temporal World State (`W_t`) | One representation of compiled state |
| Agent-World-Preceptor | PerceptionPack Compiler | Generates agent-specific perception |
| GNN Module | Graph-aware State Encoder | Supports link completion, ranking, and distribution |
| Event Sandbox | Downstream Evaluation Testbed | Tests quality of language-state interface |
| Market Simulation | Application / Validation Environment | Validation context, not core contribution |

## Suggested Data Model (MVP)

Initial relational tables:

- `documents`
- `evidence_spans`
- `entities`
- `instruments`
- `entity_links`
- `event_mentions`
- `canonical_events`
- `event_relations`
- `narratives`
- `market_moves`
- `world_state_snapshots`
- `agent_profiles`
- `agent_memories`
- `perception_packs`
- `agent_belief_updates`
- `agent_actions`
- `simulation_runs`
- `evaluation_records`

Key first-class tables:

- `documents`
- `canonical_events`
- `event_relations`
- `market_moves`
- `perception_packs`

## MVP Scope (V1)

Use a constrained, clean demo:

- 20 stocks
- 1 month of news + announcements
- daily or 30-minute market observations
- 3 agent archetypes:
  - value investor
  - momentum trader
  - sector/theme trader

V1 outputs:

- daily shared world state snapshots
- daily agent-specific `PerceptionPack`s
- logged belief updates
- ablation between raw-text prompting vs `PerceptionPack` prompting

V1 implementation strategy:

- prioritize normalization + schema extraction + mention clustering + canonical event generation + state snapshots + agent-conditioned top-k perception
- defer GNN-heavy training; start with retrieval/rule-based reranking (e.g., exposure score, source access filter, temporal decay), then add graph-aware reranking in V2

## One-Sentence Contribution

> Our pipeline converts heterogeneous financial texts into evidence-grounded event, entity, relation, and narrative frames; consolidates them into a shared temporal world state; and projects this state into agent-conditioned PerceptionPacks based on each agent's portfolio, role, memory, network position, and information access. The resulting PerceptionPacks serve as the observation layer for downstream belief updates and market simulation.

中文版本：

> 本系统将多源金融文本编译为带证据的事件、实体、关系和叙事结构，进一步整合为共享时序世界状态，并根据每个 Agent 的持仓、角色、记忆、网络位置和信息权限投影成个体化 PerceptionPack。PerceptionPack 作为下游信念更新与市场仿真的观察层。
