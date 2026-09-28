import json
import unittest
from datetime import datetime, timedelta, timezone

from src.availability_base_rates import PLAY_CHAIN, count_binary, count_buckets, predict_binary, predict_buckets
from src.availability_bq import assert_pilot_table
from src.availability_decisions import (
    THRESHOLDS,
    Case,
    build_questions,
    build_state,
    combined_play_probability,
    decision_row,
    gate_choice,
    input_hash,
)
from src.availability_labels import (
    InjuryRow,
    TeamGame,
    build_label_rows,
    consistent_buckets,
    dedupe_injury_rows,
    game_outcome,
    normalize_practice_status,
    resolve_bucket,
    team_schedule,
)
from src.availability_text import match_player_items, parse_draftsharks_rss

UTC = timezone.utc


def schedule(weeks, season=2020, team="BUF"):
    return team_schedule(TeamGame(season, team, w, f"{season}_{w:02d}_{team}") for w in weeks)


def report(week, status="Out", practice="Did Not Participate In Practice", team="BUF", primary="Knee", season=2020):
    return InjuryRow(season, week, team, "00-1", "Test Player", "WR", status, practice, primary, None)


class LabelTests(unittest.TestCase):
    def test_bye_week_is_not_a_missed_game(self):
        games = schedule([1, 2, 3, 5, 6])  # bye in week 4
        played = {("00-1", 2020, w): "BUF" for w in (1, 2, 5, 6)}
        rows = build_label_rows([report(3)], games, played, {})
        self.assertEqual(rows[0]["games_missed_until_return"], 1)
        self.assertEqual(rows[0]["missed_bucket"], "1")
        self.assertEqual(rows[0]["return_week"], 5)
        self.assertFalse(rows[0]["censored"])

    def test_return_detection_counts_team_games(self):
        games = schedule(range(1, 18))
        played = {("00-1", 2020, w): "BUF" for w in (1, 2, 7, 8)}
        rows = build_label_rows([report(3)], games, played, {})
        self.assertEqual(rows[0]["games_missed_until_return"], 4)
        self.assertEqual(rows[0]["missed_bucket"], "2_4")
        self.assertFalse(rows[0]["played_this_game"])
        self.assertFalse(rows[0]["played_next_game"])

    def test_played_listed_game_is_bucket_zero(self):
        games = schedule(range(1, 18))
        played = {("00-1", 2020, w): "BUF" for w in range(1, 18)}
        row = build_label_rows([report(3, "Questionable", "Limited Participation in Practice")], games, played, {})[0]
        self.assertTrue(row["played_this_game"])
        self.assertEqual((row["games_missed_until_return"], row["missed_bucket"]), (0, "0"))

    def test_season_end_censoring(self):
        games = schedule(range(1, 18))
        played = {("00-1", 2020, w): "BUF" for w in range(1, 15)}
        rows = build_label_rows([report(15), report(17)], games, played, {})
        by_week = {r["week"]: r for r in rows}
        self.assertEqual(by_week[15]["censor_reason"], "season_end")
        self.assertEqual(by_week[15]["games_missed_until_return"], 3)
        self.assertEqual(by_week[15]["missed_bucket"], "5_plus_or_season")
        # One game left and missed: one game or season-ending is ambiguous, so no bucket.
        self.assertIsNone(by_week[17]["missed_bucket"])
        self.assertIsNone(by_week[17]["played_next_game"])

    def test_data_horizon_censoring_leaves_short_absence_unresolved(self):
        games = schedule(range(1, 18), season=2026)
        rows = build_label_rows([report(1, season=2026), report(3, season=2026)], games, {}, {}, last_observed_week={2026: 2})
        self.assertEqual([r["week"] for r in rows], [1])  # week 3 has no outcome yet
        self.assertEqual(rows[0]["censor_reason"], "data_horizon")
        self.assertIsNone(rows[0]["missed_bucket"])
        self.assertIsNone(resolve_bucket(3, "data_horizon"))
        self.assertEqual(resolve_bucket(6, "data_horizon"), "5_plus_or_season")

    def test_exclusion_flags(self):
        games = schedule(range(1, 18))
        played = {("00-1", 2020, 6): "MIA"}
        roster = {("00-1", 2020, 4): ("BUF", "CUT")}
        row = build_label_rows([report(3)], games, played, roster)[0]
        self.assertTrue(row["flag_team_change"])
        self.assertTrue(row["flag_cut"])
        self.assertTrue(row["excluded_from_fit"])
        nir = build_label_rows([report(3, primary="Not injury related - resting player")], games, {("00-1", 2020, 4): "BUF"}, {})[0]
        self.assertTrue(nir["flag_not_injury_related"])

    def test_episode_and_previous_week_state(self):
        games = schedule(range(1, 18))
        played = {("00-1", 2020, w): "BUF" for w in (1, 2, 4, 5, 6)}
        rows = build_label_rows([report(3), report(4, "Questionable"), report(6)], games, played, {})
        by_week = {r["week"]: r for r in rows}
        self.assertEqual(by_week[3]["prev_week_state"], "NOT_LISTED")
        self.assertEqual(by_week[4]["prev_week_state"], "LISTED_MISSED")
        self.assertEqual(by_week[4]["prev_week_status"], "Out")
        self.assertEqual(by_week[4]["episode_id"], by_week[3]["episode_id"])
        self.assertEqual(by_week[4]["weeks_in_episode"], 2)
        self.assertNotEqual(by_week[6]["episode_id"], by_week[3]["episode_id"])

    def test_dedupe_keeps_most_severe_entry(self):
        rows = dedupe_injury_rows([report(3, "Questionable"), report(3, "Doubtful")])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].report_status, "Doubtful")
        self.assertEqual(normalize_practice_status("Out (Definitely Will Not Play)"), "DNP")

    def test_game_outcome_for_scoring(self):
        ids = ["g3", "g4", "g5", "g6"]
        self.assertIsNone(game_outcome(ids, set(), {"g1", "g2"}, False))  # target not loaded yet
        open_absence = game_outcome(ids, set(), {"g3", "g4"}, False)
        self.assertEqual(open_absence["games_missed"], 2)
        self.assertEqual(open_absence["censor_reason"], "data_horizon")
        self.assertEqual(open_absence["possible_buckets"], ["2_4", "5_plus_or_season"])
        returned = game_outcome(ids, {"g4"}, {"g3", "g4"}, False)
        self.assertEqual((returned["bucket"], returned["played"]), ("1", False))
        self.assertEqual(consistent_buckets(1, None), ["1", "2_4", "5_plus_or_season"])


class BaseRateTests(unittest.TestCase):
    def test_backoff_shrinks_sparse_cells_toward_parent(self):
        rows = [{"report_status": "Out", "practice_status": "DNP", "prev_week_state": "NOT_LISTED", "body_part_group": "knee", "played_this_game": False}] * 8
        rows += [{"report_status": "Questionable", "practice_status": "LP", "prev_week_state": "NOT_LISTED", "body_part_group": "knee", "played_this_game": True}] * 2
        tables = count_binary(rows, PLAY_CHAIN, "played_this_game")
        global_rate = (2 + 1) / (10 + 2)
        expected_status = (0 + 5 * global_rate) / (8 + 5)
        self.assertAlmostEqual(predict_binary(tables, PLAY_CHAIN, 5, rows[0], depth=1), expected_status)
        unseen = {"report_status": "Doubtful", "practice_status": "DNP", "prev_week_state": "NOT_LISTED", "body_part_group": "ankle"}
        self.assertAlmostEqual(predict_binary(tables, PLAY_CHAIN, 5, unseen), global_rate)
        for row in rows:
            row["missed_bucket"] = "0" if row["played_this_game"] else "2_4"
        dist = predict_buckets(count_buckets(rows, PLAY_CHAIN), PLAY_CHAIN, 5, rows[0])
        self.assertAlmostEqual(sum(dist), 1.0)
        self.assertEqual(max(range(4), key=lambda i: dist[i]), 2)


def sample_case(**overrides) -> Case:
    as_of = datetime(2026, 9, 27, 11, 0, tzinfo=UTC)  # 07:00 ET, Sunday
    values = dict(
        gsis_id="00-1", sleeper_player_id="123", player_name="Test Player", team="BUF", team_name="Buffalo Bills (BUF)",
        position="WR", as_of=as_of, season=2026, target_week=4, target_game_id="2026_04_BUF_MIA",
        kickoff_utc=datetime(2026, 10, 1, 0, 15, tzinfo=UTC),  # Wednesday 20:15 ET
        opponent_name="Miami Dolphins", is_home=False, games_remaining=14,
        official_report="No official injury report for Week 4 yet.", sleeper_status="Questionable",
        sleeper_body_part="Hamstring", sleeper_note=None, sleeper_practice=None,
        sleeper_listed_since=datetime(2026, 9, 24, 11, 0, tzinfo=UTC), recent_games=[],
        prior_lane="report_last_game", prior_lane_description="test", prior_play=0.6, prior_buckets=None,
        text_items=[{
            "source": "draftsharks_injury_news", "item_url": "https://example.test/1",
            "published_at": as_of - timedelta(days=3), "title": "Test Player hurts hamstring", "text": "He left practice.",
        }],
        designation="Questionable", practice_status="NONE", body_part="Hamstring",
    )
    values.update(overrides)
    return Case(**values)


class DecisionTests(unittest.TestCase):
    def test_state_dates_come_from_code(self):
        state = build_state(sample_case())
        self.assertEqual(state["today"], "Sunday, September 27, 2026")
        self.assertEqual(state["next_game"]["date"], "Wednesday, September 30, 2026 (in 3 days)")
        self.assertEqual(state["news_items"][0]["published"], "Thursday, September 24, 2026 (3 days ago)")
        self.assertIn("3 days before today", state["sleeper"]["listed_with_this_designation_since"])
        self.assertIn("60 percent", state["base_rate_prior"])
        self.assertNotIn("2026-", json.dumps(state))  # no raw ISO dates for the model to compare

    def test_threshold_blanking(self):
        low = gate_choice({"choice": "will_play", "confidence": THRESHOLDS["availability"] - 0.01, "probabilities": {"will_play": 0.7}}, THRESHOLDS["availability"])
        self.assertTrue(low["blank"])
        self.assertIsNone(low["value"])
        self.assertEqual(low["top"], "will_play")
        high = gate_choice({"choice": "will_miss", "confidence": 0.9, "probabilities": {}}, THRESHOLDS["availability"])
        self.assertEqual((high["value"], high["blank"]), ("will_miss", False))
        self.assertTrue(gate_choice(None, 0.5)["blank"])

    def test_decision_row_logs_every_blank(self):
        case = sample_case()
        response = {
            "model": "jev-1.13.0",
            "usage": {"input_tokens": 1000, "output_tokens": 50},
            "answers": {
                "availability": {"choice": "will_miss", "confidence": 0.95, "probabilities": {"will_play": 0.02, "game_time_decision": 0.02, "will_miss": 0.96}},
                "absence": {"choice": "1", "confidence": 0.2, "probabilities": {"0": 0.3, "1": 0.4, "2_4": 0.2, "5_plus_or_season": 0.1}},
                "trend": {"choice": "worsening", "confidence": 0.8, "probabilities": {}},
                "relevance_0": {"noul": 0.9},
            },
        }
        row, misses = decision_row(case, run_mode="live", decision_date=datetime(2026, 9, 27).date(), state_hash="h", response=response, base_rate_version="v")
        self.assertEqual(row["availability"], "will_miss")
        self.assertIsNone(row["absence"])
        self.assertTrue(row["absence_blank"])
        self.assertEqual([m["question"] for m in misses], ["absence"])
        self.assertEqual(row["relevant_text_count"], 1)
        self.assertAlmostEqual(row["combined_play_prob"], 0.02 + 0.02 * 0.6)
        self.assertAlmostEqual(row["cost_usd"], 1000 * 0.042 / 1_000_000)

    def test_combined_probability_falls_back_to_prior(self):
        answer = {"blank": False, "probabilities": {"will_play": 0.1, "game_time_decision": 0.0, "will_miss": 0.9}}
        self.assertEqual(combined_play_probability(0.7, answer, has_relevant_text=False), 0.7)
        self.assertEqual(combined_play_probability(0.7, {**answer, "blank": True}, has_relevant_text=True), 0.7)

    def test_input_hash_is_stable_and_sensitive(self):
        case = sample_case()
        h1 = input_hash(build_state(case), build_questions(case, 1))
        self.assertEqual(h1, input_hash(build_state(sample_case()), build_questions(sample_case(), 1)))
        changed = sample_case(sleeper_status="Out")
        self.assertNotEqual(h1, input_hash(build_state(changed), build_questions(changed, 1)))

    def test_questions_fan_out_one_relevance_noul_per_item(self):
        questions = build_questions(sample_case(), 3)
        self.assertEqual(sorted(questions), ["absence", "availability", "relevance_0", "relevance_1", "relevance_2", "trend"])
        self.assertEqual(questions["relevance_1"]["type"], "noul")

    def test_writes_are_limited_to_pilot_tables(self):
        assert_pilot_table("availability_decisions_daily")
        for name in ("analytics_pigskin_rankings", "unified_draft_rankings_current", "availability_x.other"):
            with self.assertRaises(ValueError):
                assert_pilot_table(name)


class TextTests(unittest.TestCase):
    RSS = """<rss xmlns:media="http://search.yahoo.com/mrss/" version="2.0"><channel>
    <item><title>Keon Coleman Misses Practice</title><link>https://www.draftsharks.com/n/1</link>
    <pubDate>Wed, 23 Sep 2026 18:00:00 +0000</pubDate><description>Bills WR Keon Coleman (hamstring) did not practice &amp; is iffy.</description>
    <media:keywords>Fantasy Football, Injury News, Keon Coleman, Bills</media:keywords></item>
    </channel></rss>"""

    def test_parse_and_match_respect_the_as_of_boundary(self):
        items = parse_draftsharks_rss(self.RSS, datetime(2026, 9, 24, tzinfo=UTC))
        self.assertEqual(items[0]["summary"], "Bills WR Keon Coleman (hamstring) did not practice & is iffy.")
        self.assertIn("Keon Coleman", items[0]["keywords"])
        before = match_player_items("Keon Coleman", "BUF", items, datetime(2026, 9, 24, tzinfo=UTC))
        self.assertEqual(len(before), 1)
        # An item published after the as-of moment must never enter a retro state.
        self.assertEqual(match_player_items("Keon Coleman", "BUF", items, datetime(2026, 9, 23, 17, 0, tzinfo=UTC)), [])

    def test_surname_match_only_inside_own_team_feed(self):
        items = [
            {"source": "team_news_items", "item_url": "u1", "team": "BUF", "title": "Coleman limited again", "summary": "", "published_at": datetime(2026, 9, 22, tzinfo=UTC)},
            {"source": "team_news_items", "item_url": "u2", "team": "DEN", "title": "Coleman breaks out", "summary": "", "published_at": datetime(2026, 9, 22, tzinfo=UTC)},
        ]
        matched = match_player_items("Keon Coleman Jr.", "BUF", items, datetime(2026, 9, 24, tzinfo=UTC))
        self.assertEqual([m["item_url"] for m in matched], ["u1"])
        self.assertEqual(matched[0]["match"], "surname_team_feed")


if __name__ == "__main__":
    unittest.main()
