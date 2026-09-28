"""Availability feed: other-positions lane, dataset build and schema, carry-forward, chain order."""

import copy
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.run_availability_decisions import build_case, official_other_candidates
from scripts.verify_live_rankings import verify_availability
from src.availability_base_rates import (
    MODEL_VERSION,
    NEXT_BUCKETS_VERSION,
    OTHER_MODEL_VERSION,
    BaseRateModel,
    load_artifact,
    POPULATIONS,
)
from src.availability_decisions import build_state
from src.availability_feed import (
    FEED_DIR,
    MISSED_BUCKETS,
    build_dataset,
    current_week,
    player_object,
    validate_dataset,
    write_artifacts,
)
from src.availability_labels import TeamGame, team_schedule

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "scripts" / "daily_pigskin_chain.ps1"
UTC = timezone.utc
NOW = datetime(2026, 9, 28, 5, 0, tzinfo=UTC)  # Monday 01:00 ET
PUBLIC_PREFIX = "https://storage.googleapis.com/fantasy-football-498121-public-rankings/"
MODELS = {name: BaseRateModel.load_population(name) for name in ("skill", "other")}


def game(team, week, day, opponent, game_id=None):
    return {
        "team": team, "week": week, "opponent": opponent, "is_home": True,
        "game_id": game_id or f"2026_{week:02d}_{team}", "kickoff_utc": datetime(2026, 9, day, 17, 0, tzinfo=UTC),
    }


def context(roster_abbr="R01", position="CB", reports=()):
    games = [game("ATL", 2, 20, "CAR"), game("ATL", 3, 27, "GB"), game("ATL", 4, 28, "NO")]
    games[2]["kickoff_utc"] = datetime(2026, 10, 5, 0, 15, tzinfo=UTC)  # Sunday night, Week 4
    roster_row = {"gsis_id": "00-0036285", "week": 3, "team": "ATL", "status": "RES", "status_abbr": roster_abbr,
                  "sleeper_id": "6836", "player_name": "Test Corner", "position": position}
    return {
        "season": 2026,
        "games": games,
        "team_names": {"ATL": "Atlanta Falcons", "NO": "New Orleans Saints", "GB": "Green Bay Packers", "CAR": "Carolina Panthers"},
        "schedule": team_schedule(TeamGame(2026, g["team"], g["week"], g["game_id"]) for g in games),
        "reports": list(reports),
        "reports_by_player": {"00-0036285": list(reports)} if reports else {},
        "played": {("00-0036285", 2026, 2): "ATL"},
        "snaps": {("00-0036285", "2026_02_ATL"): {"offense_snaps": 0, "defense_snaps": 40, "st_snaps": 5}},
        "loaded_games": {"2026_02_ATL"},
        "roster": {("00-0036285", 2026, 3): ("ATL", "RES")},
        "sleeper_to_gsis": {"6836": "00-0036285"},
        "gsis_to_sleeper": {"00-0036285": "6836"},
        "latest_roster_week": 3,
        "latest_roster": {"00-0036285": roster_row},
        "roster_rows": {("00-0036285", 3): roster_row},
        "name_team_to_gsis": {},
    }


def defender_case(**ctx_overrides):
    ctx = context(**ctx_overrides)
    case, lane = build_case(ctx, MODELS, None, "00-0036285", "ATL", ctx["games"][2], NOW, [], [])
    return case, lane


def decision_row(case, relevant=1, blank=False, question_value=("will_miss", "2_4", "worsening")):
    availability, absence, trend = question_value
    items = [{
        "source": "draftsharks_injury_news", "item_url": f"https://example.test/{i}",
        "published_at": f"2026-09-2{i}T12:00:00+00:00", "title": "t", "summary": "s", "match": "name",
        "relevance": 0.9 if i < relevant else 0.1, "relevant": i < relevant,
    } for i in range(max(relevant, 1) + 1)]
    return {
        "relevant_text_count": relevant, "text_items_json": json.dumps(items),
        "availability": None if blank else availability, "availability_confidence": 0.91234, "availability_blank": blank,
        "absence": absence, "absence_confidence": 0.6, "absence_blank": False,
        "trend": trend, "trend_confidence": 0.55, "trend_blank": False,
        "jev_model_version": "jev-1.13.0",
    }


def dataset(entries):
    return build_dataset(
        entries, generated_at=NOW, decision_date=NOW.date(), season=2026, week=3,
        base_rate_versions=[MODEL_VERSION, OTHER_MODEL_VERSION, NEXT_BUCKETS_VERSION], jev_models=["jev-1.13.0"],
    )


def assert_importer_invariants(test: unittest.TestCase, data: dict) -> None:
    """The site importer rejects the whole object on any of these."""
    test.assertTrue(1 <= data["week"] <= 22)
    for player in data["players"]:
        test.assertIsInstance(player["sleeper_player_id"], str)
        base = player["base_rate"]
        test.assertIsInstance(base, dict)
        test.assertIsInstance(base["p_play_next_game"], float)
        test.assertEqual(set(base["missed_bucket"]), {"0", "1", "2_4", "5_plus_or_season"})
        test.assertTrue(all(isinstance(v, float) for v in base["missed_bucket"].values()))
        test.assertEqual(set(player["text"]), {
            "availability", "availability_confidence", "absence", "absence_confidence",
            "trend", "trend_confidence", "relevant_items", "sources",
        })
        test.assertIsInstance(player["text"]["relevant_items"], int)
        test.assertIsInstance(player["text"]["sources"], list)
        test.assertTrue(player["next_game"] is None or set(player["next_game"]) == {"opponent", "kickoff_utc"})


class OtherPositionsLaneTests(unittest.TestCase):
    def test_skill_artifact_numbers_unchanged(self):
        skill = load_artifact(POPULATIONS["skill"]["path"])
        self.assertEqual((skill["model_version"], skill["k"], skill["fit_rows"], skill["holdout_rows"]), (MODEL_VERSION, 50, 11636, 3104))
        self.assertEqual(skill["metrics"]["play_this_game"]["model"]["brier"], 0.08027)
        self.assertEqual(skill["tables"]["play_this_game"]["report_status"]["Out"], [2361, 1])

    def test_other_artifact_fit_the_same_way(self):
        other = load_artifact(POPULATIONS["other"]["path"])
        skill = load_artifact(POPULATIONS["skill"]["path"])
        self.assertEqual(other["model_version"], OTHER_MODEL_VERSION)
        for key in ("fit_seasons", "holdout_seasons", "chains", "buckets", "estimator", "source_table"):
            self.assertEqual(other[key], skill[key], key)
        self.assertGreater(other["fit_rows"], skill["fit_rows"])
        lane = other["metrics"]["play_this_game"]
        self.assertLess(lane["model"]["log_loss"], lane["status_only"]["log_loss"])

    def test_next_bucket_lanes_are_proper_distributions(self):
        for model in MODELS.values():
            for dist in (model.buckets_next_game({"report_status": "Out", "practice_status": "DNP", "played_this_game": None}),
                         model.roster_buckets_next_game("RES"), model.roster_buckets_next_game("UNSEEN")):
                self.assertEqual(list(dist), list(MISSED_BUCKETS))
                self.assertAlmostEqual(sum(dist.values()), 1.0)
            self.assertGreater(model.roster_buckets_next_game("RES")["5_plus_or_season"], 0.5)

    def test_defender_on_reserve_uses_other_lane_and_roster_designation(self):
        case, lane = defender_case()
        self.assertEqual(lane, "roster_status")
        self.assertEqual(case.base_rate_version, OTHER_MODEL_VERSION)
        self.assertEqual((case.designation, case.designation_source, case.sleeper_player_id), ("IR", "team_roster", "6836"))
        self.assertFalse(case.sleeper_collected)
        state = build_state(case)
        self.assertEqual(state["sleeper"], {"availability": "Sleeper data is not collected for this position."})
        self.assertIn("reserve/injured", state["official_injury_report"])
        self.assertIn("positions other than QB, RB, WR, and TE", state["base_rate_prior"])
        self.assertIn("40 defensive, 5 special teams snaps", " ".join(state["recent_games"]))
        self.assertAlmostEqual(sum(case.feed_buckets.values()), 1.0)
        self.assertIsNone(case.prior_buckets)  # the Jev state is unchanged; feed buckets stay out of it

    def test_cleared_official_designation_is_skipped(self):
        report = {"season": 2026, "week": 3, "team": "ATL", "gsis_id": "00-0036285", "player_name": "Test Corner",
                  "position": "CB", "report_status": None, "practice_status": "Full Participation in Practice",
                  "primary_injury": "Knee", "secondary_injury": None}
        case, lane = defender_case(roster_abbr="A01", reports=[report])
        self.assertIsNone(case)
        self.assertEqual(lane, "official_designation_cleared")

    def test_official_population_excludes_sleeper_positions_and_stale_rosters(self):
        ctx = context()
        found, _ = official_other_candidates(ctx, NOW, covered=set())
        self.assertEqual(found, {"00-0036285": "ATL"})
        ctx["latest_roster"]["00-0036285"]["position"] = "WR"  # Sleeper covers WR
        self.assertEqual(official_other_candidates(ctx, NOW, covered=set())[0], {})
        ctx = context()
        ctx["latest_roster_week"] = 2  # older than ATL's last game (week 3)
        found, skipped = official_other_candidates(ctx, NOW, covered=set())
        self.assertEqual((found, skipped["official_roster_older_than_last_game"]), ({}, 1))


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.case, _ = defender_case()
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_text_is_gated_and_rounded(self):
        text = player_object(self.case, decision_row(self.case))["text"]
        self.assertEqual((text["availability"], text["availability_confidence"]), ("will_miss", 0.912))
        self.assertEqual(len(text["sources"]), 1)
        self.assertTrue(text["sources"][0]["published_at"].endswith("Z"))
        blank = player_object(self.case, decision_row(self.case, blank=True))
        self.assertIsNone(blank["text"]["availability"])
        self.assertIsNone(blank["text"]["availability_confidence"])
        self.assertIn("availability", blank["caveats"][-1])
        none = player_object(self.case, decision_row(self.case, relevant=0))["text"]
        self.assertTrue(all(none[q] is None for q in ("availability", "absence", "trend")))
        failed = player_object(self.case, None)
        self.assertEqual((failed["text"]["relevant_items"], failed["text"]["sources"]), (0, []))
        self.assertIn("failed", failed["caveats"][-1])

    def test_sources_capped_at_three_newest_first(self):
        text = player_object(self.case, decision_row(self.case, relevant=5))["text"]
        self.assertEqual(len(text["sources"]), 3)
        self.assertEqual([s["published_at"] for s in text["sources"]], sorted((s["published_at"] for s in text["sources"]), reverse=True))

    def test_built_file_meets_schema_and_importer_invariants(self):
        other, _ = defender_case()
        other.player_name, other.team, other.sleeper_player_id, other.gsis_id = "Alpha Back", "LA", "99", None
        no_id, _ = defender_case()
        no_id.sleeper_player_id = None
        data = dataset([(self.case, decision_row(self.case)), (other, None), (no_id, None)])
        self.assertEqual([p["team"] for p in data["players"]], ["ATL", "LAR"])  # sorted, Sleeper codes, no-id player omitted
        entry = write_artifacts(data, omitted=1, out_dir=self.tmp)
        raw = (self.tmp / "availability.json").read_bytes()
        loaded = json.loads(raw)
        validate_dataset(loaded)
        assert_importer_invariants(self, loaded)
        self.assertEqual(entry["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(entry["bytes"], len(raw))
        self.assertTrue(entry["url"].startswith(PUBLIC_PREFIX + "v1/datasets/availability/sha256-"))
        self.assertEqual(json.loads((self.tmp / "availability.manifest-entry.json").read_text()), entry)
        self.assertEqual(verify_availability(raw, entry)["players"], 2)
        with self.assertRaises(ValueError):
            verify_availability(raw + b" ", entry)

    @unittest.skipUnless((FEED_DIR / "availability.json").exists(), "no locally built availability dataset")
    def test_locally_built_file_meets_importer_invariants(self):
        data = json.loads((FEED_DIR / "availability.json").read_bytes())
        validate_dataset(data)
        assert_importer_invariants(self, data)

    def test_validator_rejects_contract_breaks(self):
        good = dataset([(self.case, decision_row(self.case))])
        validate_dataset(good)
        breaks = {
            "null base_rate": lambda d: d["players"][0].update(base_rate=None),
            "null bucket": lambda d: d["players"][0]["base_rate"].update(missed_bucket=None),
            "missing text key": lambda d: d["players"][0]["text"].pop("trend"),
            "value without confidence": lambda d: d["players"][0]["text"].update(availability_confidence=None),
            "text without relevant items": lambda d: d["players"][0]["text"].update(relevant_items=0, sources=[]),
            "unrounded probability": lambda d: d["players"][0]["base_rate"].update(p_play_next_game=0.12345),
            "integer sleeper id": lambda d: d["players"][0].update(sleeper_player_id=6836),
            "week 23": lambda d: d.update(week=23),
            "extra top key": lambda d: d.update(extra=1),
            "four sources": lambda d: d["players"][0]["text"].update(sources=d["players"][0]["text"]["sources"] * 4),
        }
        for name, mutate in breaks.items():
            broken = copy.deepcopy(good)
            mutate(broken)
            with self.subTest(name), self.assertRaises(ValueError):
                validate_dataset(broken)

    def test_invalid_dataset_writes_nothing(self):
        data = dataset([(self.case, decision_row(self.case))])
        data["week"] = 0
        with self.assertRaises(ValueError):
            write_artifacts(data, omitted=0, out_dir=self.tmp)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_current_week_is_the_next_kickoff_week(self):
        games = [{"week": 3, "kickoff_utc": datetime(2026, 9, 29, 0, 15, tzinfo=UTC)},
                 {"week": 4, "kickoff_utc": datetime(2026, 10, 2, 0, 15, tzinfo=UTC)}]
        self.assertEqual(current_week(games, NOW), 3)
        self.assertEqual(current_week(games, datetime(2026, 9, 29, 6, 0, tzinfo=UTC)), 4)
        self.assertEqual(current_week(games, datetime(2027, 1, 30, tzinfo=UTC)), 4)


class CarryForwardTests(unittest.TestCase):
    def test_publisher_carries_previous_availability_entry(self):
        from scripts.publish_public_rankings import fetch_current_datasets

        entry = {"object": "v1/datasets/availability/sha256-a.json", "url": PUBLIC_PREFIX + "v1/datasets/availability/sha256-a.json",
                 "sha256": "a", "bytes": 1, "source_generated_at": "2026-09-27T11:00:00Z"}
        manifest = json.dumps({"profiles": {}, "datasets": {"availability": entry}}).encode()

        class Blob:
            def download_as_bytes(self):
                return manifest

        class Bucket:
            def blob(self, name):
                return Blob()

        self.assertEqual(fetch_current_datasets(Bucket(), "unused")["availability"], entry)


class ChainOrderTests(unittest.TestCase):
    def setUp(self):
        self.text = CHAIN.read_text(encoding="utf-8")

    def index(self, needle):
        position = self.text.find(needle)
        self.assertGreaterEqual(position, 0, needle)
        return position

    def test_availability_runs_after_inseason_and_before_upload_and_publish(self):
        step = self.index("Invoke-Logged 'availability-decisions'")
        self.assertLess(self.index("Invoke-Logged 'inseason-ranking-horizons'"), step)
        self.assertLess(step, self.index("foreach ($datasetId in"))
        self.assertLess(step, self.index("Invoke-Logged 'publish-public-rankings'"))
        self.assertEqual(self.text.count("run_availability_decisions.py"), 1)

    def test_availability_step_is_non_fatal_and_bounded(self):
        step = self.index("Invoke-Logged 'availability-decisions'")
        opened = self.text.rfind("try {", 0, step)
        closed = self.text.find("} catch {", step)
        block = self.text[opened:self.text.find("\n}", closed) + 2]
        self.assertNotIn("exit ", block)
        self.assertIn("Remove-Item -LiteralPath $availabilityArtifacts", block[: block.find("Invoke-Logged")])
        self.assertRegex(block, r"--live' -f \$root\) \$root \d+")
        self.assertIn("'availability'", self.text[self.index("foreach ($datasetId in"):][:200])
        catch = self.text[self.index("dataset upload failed"):][:400]
        self.assertLess(catch.find("continue"), catch.find("exit 1"))

    @unittest.skipUnless(shutil.which("powershell") or shutil.which("pwsh"), "PowerShell not available")
    def test_powershell_parses_and_step_sits_in_a_try_statement(self):
        script = (
            "$e=$null;$ast=[System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$null,[ref]$e);"
            "$tries=$ast.FindAll({param($n) $n -is [System.Management.Automation.Language.TryStatementAst]},$true) |"
            " Where-Object { $_.Body.Extent.Text -match \"'availability-decisions'\" };"
            "@{errors=$e.Count;try_blocks=@($tries).Count;catches=($tries | ForEach-Object { $_.CatchClauses.Count } | Measure-Object -Sum).Sum} | ConvertTo-Json -Compress"
        ) % str(CHAIN).replace("'", "''")
        shell = shutil.which("powershell") or shutil.which("pwsh")
        out = subprocess.run([shell, "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=60)
        result = json.loads(out.stdout.strip())
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["try_blocks"], 1)
        self.assertEqual(result["catches"], 1)


if __name__ == "__main__":
    unittest.main()
