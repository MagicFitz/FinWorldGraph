from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Literal
import math

ObjectType = Literal[
    "document",
    "event",
    "narrative",
    "market_move",
    "entity",
    "instrument",
]


@dataclass
class WorldObject:
    object_id: str
    object_type: ObjectType
    timestamp: datetime
    title: str
    summary: str
    related_entities: list[str] = field(default_factory=list)
    related_instruments: list[str] = field(default_factory=list)
    related_sectors: list[str] = field(default_factory=list)
    related_narratives: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    evidence_doc_ids: list[str] = field(default_factory=list)
    evidence_spans: list[dict[str, Any]] = field(default_factory=list)
    polarity: float | None = None
    magnitude: float | None = None
    uncertainty: float | None = None
    source_reliability: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentContext:
    agent_id: str
    role: str
    portfolio: list[str]
    watchlist: list[str]
    preferred_sectors: list[str]
    source_access: list[str]
    information_channels: list[str]
    network_position: dict[str, float]
    risk_preference: float
    memory_half_life_hours: float
    attention_budget: dict[str, int]
    role_interest_weights: dict[str, float]


@dataclass
class AgentHistory:
    seen_object_ids: set[str]
    previous_beliefs: dict[str, Any]
    previous_actions: list[dict[str, Any]]
    memory_items: list[dict[str, Any]]


class VisibilityFilter:
    def __init__(self, channel_delays: dict[str, float]):
        self.channel_delays = channel_delays

    def is_visible(self, obj: WorldObject, agent: AgentContext, current_time: datetime) -> tuple[bool, list[str]]:
        if obj.timestamp > current_time:
            return False, ["future_information"]

        if obj.source_ids:
            if not any(src in agent.source_access for src in obj.source_ids):
                return False, ["source_not_accessible"]

        max_delay_minutes = 0.0
        for src in obj.source_ids:
            max_delay_minutes = max(max_delay_minutes, self.channel_delays.get(src, 0.0))

        visible_time = obj.timestamp + timedelta(minutes=max_delay_minutes)
        if visible_time > current_time:
            return False, ["not_arrived_due_to_channel_delay"]

        return True, ["time_visible", "source_accessible"]


def recall_candidates(visible_objects: list[WorldObject], agent: AgentContext, history: AgentHistory, max_candidates: int = 100) -> list[WorldObject]:
    candidates: list[WorldObject] = []
    portfolio_set = set(agent.portfolio)
    watchlist_set = set(agent.watchlist)
    sector_set = set(agent.preferred_sectors)

    for obj in visible_objects:
        instruments = set(obj.related_instruments)
        sectors = set(obj.related_sectors)

        direct_portfolio_hit = bool(instruments & portfolio_set)
        watchlist_hit = bool(instruments & watchlist_set)
        sector_hit = bool(sectors & sector_set)

        is_market_move = obj.object_type == "market_move"
        is_new = obj.object_id not in history.seen_object_ids

        if direct_portfolio_hit or watchlist_hit or sector_hit or is_market_move or is_new:
            candidates.append(obj)

    return candidates[:max_candidates]


def portfolio_exposure_score(obj: WorldObject, agent: AgentContext) -> float:
    if not obj.related_instruments:
        return 0.0
    instruments = set(obj.related_instruments)
    if instruments & set(agent.portfolio):
        return 1.0
    if instruments & set(agent.watchlist):
        return 0.6
    return 0.0


def sector_exposure_score(obj: WorldObject, agent: AgentContext) -> float:
    if not obj.related_sectors:
        return 0.0
    return 1.0 if set(obj.related_sectors) & set(agent.preferred_sectors) else 0.0


def role_affinity_score(obj: WorldObject, agent: AgentContext) -> float:
    event_type = obj.metadata.get("event_type") or obj.metadata.get("move_type")
    if not event_type:
        return 0.3
    return agent.role_interest_weights.get(event_type, 0.3)


def temporal_decay_score(obj: WorldObject, agent: AgentContext, current_time: datetime) -> float:
    age_hours = (current_time - obj.timestamp).total_seconds() / 3600
    half_life = agent.memory_half_life_hours
    if half_life <= 0:
        return 0.0
    return math.exp(-math.log(2) * age_hours / half_life)


def novelty_score(obj: WorldObject, history: AgentHistory) -> float:
    return 0.2 if obj.object_id in history.seen_object_ids else 1.0


def memory_continuity_score(obj: WorldObject, history: AgentHistory) -> float:
    for instrument in set(obj.related_instruments):
        if instrument in history.previous_beliefs:
            return 0.8
    return 0.0


def belief_relevance_score(obj: WorldObject, history: AgentHistory) -> float:
    for inst in obj.related_instruments:
        belief = history.previous_beliefs.get(inst)
        if not belief:
            continue
        old_direction = belief.get("direction")
        obj_polarity = obj.polarity
        if old_direction == "bullish" and obj_polarity and obj_polarity > 0:
            return 0.7
        if old_direction == "bullish" and obj_polarity and obj_polarity < 0:
            return 1.0
    return 0.0


def network_exposure_score(obj: WorldObject, agent: AgentContext) -> float:
    centrality = agent.network_position.get("centrality", 0.5)
    social_media_exposure = agent.network_position.get("social_media_exposure", 0.5)
    source_types = obj.metadata.get("source_types", [])
    if "social_media" in source_types:
        return social_media_exposure
    if "institutional" in source_types:
        return centrality
    return 0.5


def market_move_relevance_score(obj: WorldObject) -> float:
    relation = obj.metadata.get("market_move_relation")
    if relation == "possible_trigger":
        return 1.0
    if relation == "same_sector_move":
        return 0.6
    if relation == "weakly_related":
        return 0.3
    return 0.0


@dataclass
class ProjectionWeights:
    portfolio: float = 0.25
    sector: float = 0.10
    role: float = 0.15
    temporal: float = 0.10
    reliability: float = 0.10
    novelty: float = 0.10
    memory: float = 0.10
    network: float = 0.05
    market_move: float = 0.05


@dataclass
class PerceptionItem:
    object_id: str
    object_type: str
    title: str
    summary: str
    salience_score: float
    feature_scores: dict[str, float]
    relevance_reasons: list[str]
    evidence_doc_ids: list[str]
    evidence_spans: list[dict[str, Any]]
    metadata: dict[str, Any]


@dataclass
class PerceptionPack:
    agent_id: str
    timestamp: datetime
    visible_items: list[PerceptionItem]
    hidden_summary: dict[str, Any]
    pack_metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


def compute_salience_score(obj: WorldObject, agent: AgentContext, history: AgentHistory, current_time: datetime, weights: ProjectionWeights) -> tuple[float, dict[str, float]]:
    features = {
        "portfolio": portfolio_exposure_score(obj, agent),
        "sector": sector_exposure_score(obj, agent),
        "role": role_affinity_score(obj, agent),
        "temporal": temporal_decay_score(obj, agent, current_time),
        "reliability": obj.source_reliability,
        "novelty": novelty_score(obj, history),
        "memory": max(memory_continuity_score(obj, history), belief_relevance_score(obj, history)),
        "network": network_exposure_score(obj, agent),
        "market_move": market_move_relevance_score(obj),
    }

    score = (
        weights.portfolio * features["portfolio"]
        + weights.sector * features["sector"]
        + weights.role * features["role"]
        + weights.temporal * features["temporal"]
        + weights.reliability * features["reliability"]
        + weights.novelty * features["novelty"]
        + weights.memory * features["memory"]
        + weights.network * features["network"]
        + weights.market_move * features["market_move"]
    )

    uncertainty = obj.uncertainty or 0.0
    risk_penalty = (1 - agent.risk_preference) * uncertainty * 0.2
    score = max(0.0, score - risk_penalty)
    return score, features


def select_with_budget(scored_items: list[dict[str, Any]], agent: AgentContext) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used_events: set[str] = set()
    type_counts: dict[str, int] = {}

    for item in sorted(scored_items, key=lambda x: x["score"], reverse=True):
        obj: WorldObject = item["object"]
        obj_type = obj.object_type
        max_count = agent.attention_budget.get(obj_type, 3)

        if type_counts.get(obj_type, 0) >= max_count:
            continue

        canonical_event_id = obj.metadata.get("canonical_event_id")
        if canonical_event_id and canonical_event_id in used_events:
            continue

        selected.append(item)
        type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        if canonical_event_id:
            used_events.add(canonical_event_id)

    return selected


def infer_relevance_reasons(feature_scores: dict[str, float]) -> list[str]:
    reasons: list[str] = []
    if feature_scores.get("portfolio", 0) > 0.8:
        reasons.append("direct_portfolio_exposure")
    elif feature_scores.get("portfolio", 0) > 0.4:
        reasons.append("watchlist_exposure")
    if feature_scores.get("sector", 0) > 0.8:
        reasons.append("preferred_sector_exposure")
    if feature_scores.get("role", 0) > 0.7:
        reasons.append("role_affinity")
    if feature_scores.get("memory", 0) > 0.7:
        reasons.append("belief_or_memory_relevance")
    if feature_scores.get("novelty", 0) > 0.8:
        reasons.append("new_information")
    if feature_scores.get("market_move", 0) > 0.7:
        reasons.append("related_to_market_move")
    if feature_scores.get("reliability", 0) > 0.8:
        reasons.append("high_source_reliability")
    return reasons


def build_perception_pack(selected_items: list[dict[str, Any]], agent: AgentContext, current_time: datetime, hidden_summary: dict[str, Any]) -> PerceptionPack:
    perception_items: list[PerceptionItem] = []
    for item in selected_items:
        obj: WorldObject = item["object"]
        perception_items.append(
            PerceptionItem(
                object_id=obj.object_id,
                object_type=obj.object_type,
                title=obj.title,
                summary=obj.summary,
                salience_score=item["score"],
                feature_scores=item["feature_scores"],
                relevance_reasons=infer_relevance_reasons(item["feature_scores"]),
                evidence_doc_ids=obj.evidence_doc_ids,
                evidence_spans=obj.evidence_spans,
                metadata=obj.metadata,
            )
        )

    return PerceptionPack(
        agent_id=agent.agent_id,
        timestamp=current_time,
        visible_items=perception_items,
        hidden_summary=hidden_summary,
        pack_metadata={
            "projection_version": "rule_based_v0.1",
            "scoring_method": "weighted_linear",
        },
    )


class AgentConditionedProjector:
    def __init__(self, visibility_filter: VisibilityFilter, weights: ProjectionWeights | None = None):
        self.visibility_filter = visibility_filter
        self.weights = weights or ProjectionWeights()

    def project(self, world_objects: list[WorldObject], agent: AgentContext, history: AgentHistory, current_time: datetime) -> PerceptionPack:
        visible_objects: list[WorldObject] = []
        hidden_reasons: dict[str, int] = {}

        for obj in world_objects:
            visible, reasons = self.visibility_filter.is_visible(obj=obj, agent=agent, current_time=current_time)
            if visible:
                visible_objects.append(obj)
            else:
                for reason in reasons:
                    hidden_reasons[reason] = hidden_reasons.get(reason, 0) + 1

        candidates = recall_candidates(visible_objects, agent, history)

        scored_items: list[dict[str, Any]] = []
        for obj in candidates:
            score, feature_scores = compute_salience_score(obj, agent, history, current_time, self.weights)
            scored_items.append({"object": obj, "score": score, "feature_scores": feature_scores})

        selected_items = select_with_budget(scored_items, agent)
        return build_perception_pack(selected_items, agent, current_time, hidden_reasons)
