from datetime import datetime
import json

from projector import (
    AgentConditionedProjector,
    AgentContext,
    AgentHistory,
    VisibilityFilter,
    WorldObject,
)


def main() -> None:
    current_time = datetime(2026, 1, 1, 10, 0)

    world_objects = [
        WorldObject(
            object_id="event_600519_earnings_surprise_20260101",
            object_type="event",
            timestamp=datetime(2026, 1, 1, 9, 45),
            title="贵州茅台一季度业绩超预期",
            summary="贵州茅台发布一季度报告，利润增速高于市场预期。",
            related_entities=["company_600519"],
            related_instruments=["600519.SH"],
            related_sectors=["liquor"],
            source_ids=["official_announcement", "mainstream_news"],
            evidence_doc_ids=["doc_001", "doc_002"],
            polarity=0.8,
            magnitude=0.75,
            uncertainty=0.12,
            source_reliability=0.92,
            metadata={"event_type": "earnings_surprise", "source_types": ["institutional"]},
        ),
        WorldObject(
            object_id="move_600519_up_5pct",
            object_type="market_move",
            timestamp=datetime(2026, 1, 1, 9, 50),
            title="贵州茅台盘中快速上涨 5%",
            summary="盘中成交量明显放大，市场关注业绩超预期后的持续性。",
            related_instruments=["600519.SH"],
            related_sectors=["liquor"],
            source_ids=["mainstream_news"],
            source_reliability=0.76,
            metadata={"move_type": "short_term_price_move", "market_move_relation": "possible_trigger"},
        ),
    ]

    agent = AgentContext(
        agent_id="value_investor_001",
        role="value_investor",
        portfolio=["600519.SH", "000858.SZ"],
        watchlist=["300750.SZ"],
        preferred_sectors=["liquor", "consumer"],
        source_access=["official_announcement", "mainstream_news", "research_report"],
        information_channels=["institutional_feed"],
        network_position={"centrality": 0.7, "community_id": 0.0, "social_media_exposure": 0.2},
        risk_preference=0.3,
        memory_half_life_hours=72,
        attention_budget={"event": 5, "narrative": 3, "market_move": 3},
        role_interest_weights={
            "earnings_surprise": 1.0,
            "policy_change": 0.8,
            "supply_shock": 0.7,
            "short_term_price_move": 0.3,
            "social_media_hype": 0.2,
        },
    )

    history = AgentHistory(
        seen_object_ids={"event_old_001"},
        previous_beliefs={"600519.SH": {"direction": "bullish", "confidence": 0.62}},
        previous_actions=[],
        memory_items=[],
    )

    visibility_filter = VisibilityFilter(
        channel_delays={
            "official_announcement": 0,
            "mainstream_news": 5,
            "research_report": 30,
            "social_media": 1,
            "private_channel": 120,
        }
    )

    projector = AgentConditionedProjector(visibility_filter=visibility_filter)
    pack = projector.project(world_objects, agent, history, current_time)

    print(json.dumps(pack.to_dict(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
