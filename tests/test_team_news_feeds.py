import unittest
from datetime import datetime, timedelta, timezone

from src import team_news_feeds as feeds

NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)

ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Buffalo Rumblings</title>
  <entry>
    <title>James Cook limited in practice Wednesday</title>
    <link href="https://www.buffalorumblings.com/post/1"/>
    <summary>The Bills running back was limited with an ankle issue.</summary>
    <author><name>Beat Writer</name></author>
    <published>2026-09-09T18:30:00Z</published>
  </entry>
  <entry>
    <title>Season preview</title>
    <link href="https://www.buffalorumblings.com/post/old"/>
    <summary>Way too early takes.</summary>
    <published>2026-07-01T10:00:00Z</published>
  </entry>
</feed>"""

RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>Pats Pulpit</title>
  <item>
    <title>Rhamondre Stevenson returns to practice</title>
    <link>https://www.patspulpit.com/post/2</link>
    <description>Back after a week off.</description>
    <pubDate>Wed, 09 Sep 2026 14:00:00 +0000</pubDate>
  </item>
</channel></rss>"""


class FeedRegistryTest(unittest.TestCase):
    def test_all_32_teams_present(self):
        self.assertEqual(len(feeds.TEAM_FEEDS), 32)

    def test_abbreviations_match_warehouse(self):
        # These are the values that appear in sleeper_players_current.team.
        expected = {
            "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN",
            "DET", "GB", "HOU", "IND", "JAX", "KC", "LAC", "LAR", "LV", "MIA",
            "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB",
            "TEN", "WAS",
        }
        self.assertEqual(set(feeds.TEAM_FEEDS), expected)

    def test_feed_urls_are_unique(self):
        urls = list(feeds.TEAM_FEEDS.values())
        self.assertEqual(len(urls), len(set(urls)))


class NormalizeNameTest(unittest.TestCase):
    def test_strips_accents_and_punctuation(self):
        self.assertEqual(feeds.normalize_name("Ja'Marr Chase"), "jamarr chase")
        self.assertEqual(feeds.normalize_name("Amon-Ra St. Brown"), "amon ra st brown")

    def test_drops_generational_suffix(self):
        self.assertEqual(feeds.normalize_name("Marvin Harrison Jr."), "marvin harrison")
        self.assertEqual(feeds.normalize_name("Odell Beckham III"), "odell beckham")

    def test_empty_input(self):
        self.assertEqual(feeds.normalize_name(None), "")
        self.assertEqual(feeds.normalize_name(""), "")


class ParseFeedTest(unittest.TestCase):
    def test_parses_atom(self):
        items = feeds.parse_feed(ATOM)
        self.assertEqual(len(items), 2)
        first = items[0]
        self.assertIn("James Cook", first["title"])
        self.assertEqual(first["url"], "https://www.buffalorumblings.com/post/1")
        self.assertEqual(first["author"], "Beat Writer")
        self.assertEqual(first["published_at"].year, 2026)

    def test_parses_rss(self):
        items = feeds.parse_feed(RSS)
        self.assertEqual(len(items), 1)
        self.assertIn("Rhamondre Stevenson", items[0]["title"])
        self.assertEqual(items[0]["published_at"].tzinfo, timezone.utc)

    def test_malformed_xml_returns_empty_not_raises(self):
        # One broken feed must not fail the run for the other 31 teams.
        self.assertEqual(feeds.parse_feed("<feed><unclosed>"), [])

    def test_empty_feed(self):
        self.assertEqual(feeds.parse_feed('<feed xmlns="http://www.w3.org/2005/Atom"/>'), [])


class FilterRecentTest(unittest.TestCase):
    def test_drops_items_older_than_window(self):
        kept = feeds.filter_recent(feeds.parse_feed(ATOM), now=NOW, max_age_days=7)
        self.assertEqual(len(kept), 1)
        self.assertIn("James Cook", kept[0]["title"])

    def test_keeps_items_with_no_timestamp(self):
        items = [{"title": "No date", "published_at": None}]
        self.assertEqual(len(feeds.filter_recent(items, now=NOW)), 1)

    def test_respects_max_items(self):
        items = [
            {"title": f"item {i}", "published_at": NOW - timedelta(hours=i)}
            for i in range(50)
        ]
        self.assertEqual(len(feeds.filter_recent(items, now=NOW, max_items=10)), 10)

    def test_sorted_newest_first(self):
        items = [
            {"title": "older", "published_at": NOW - timedelta(days=2)},
            {"title": "newer", "published_at": NOW - timedelta(hours=1)},
        ]
        self.assertEqual(feeds.filter_recent(items, now=NOW)[0]["title"], "newer")


class MatchPlayersTest(unittest.TestCase):
    def test_matches_full_name_in_title(self):
        items = feeds.parse_feed(ATOM)
        players = [{"player_name": "James Cook", "sleeper_player_id": "1"}]
        matched = feeds.match_players(items, players)
        self.assertEqual(len(matched[0]["matched_players"]), 1)

    def test_matches_in_summary(self):
        items = [{"title": "Injury report", "summary": "James Cook was limited."}]
        players = [{"player_name": "James Cook", "sleeper_player_id": "1"}]
        self.assertEqual(len(feeds.match_players(items, players)[0]["matched_players"]), 1)

    def test_does_not_match_on_last_name_alone(self):
        # "Cook" alone appears constantly on a team blog.
        items = [{"title": "Cook expected to start", "summary": ""}]
        players = [{"player_name": "James Cook", "sleeper_player_id": "1"}]
        self.assertEqual(feeds.match_players(items, players)[0]["matched_players"], [])

    def test_matches_despite_punctuation_difference(self):
        items = [{"title": "JaMarr Chase practices fully", "summary": ""}]
        players = [{"player_name": "Ja'Marr Chase", "sleeper_player_id": "1"}]
        self.assertEqual(len(feeds.match_players(items, players)[0]["matched_players"]), 1)

    def test_single_word_player_names_are_ignored(self):
        # A defense entry like "Bills" would match nearly every article.
        items = [{"title": "Bills win again", "summary": ""}]
        players = [{"player_name": "Bills", "sleeper_player_id": "BUF"}]
        self.assertEqual(feeds.match_players(items, players)[0]["matched_players"], [])

    def test_no_players_yields_no_matches(self):
        items = feeds.parse_feed(ATOM)
        self.assertEqual(feeds.match_players(items, [])[0]["matched_players"], [])


class FakeResponse:
    def __init__(self, text, status=200):
        self.text = text
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise RuntimeError(f"HTTP {self.status}")


class FakeSession:
    def __init__(self, text=ATOM, status=200, boom=None):
        self.text, self.status, self.boom = text, status, boom
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(url)
        if self.boom:
            raise self.boom
        return FakeResponse(self.text, self.status)


class FetchTeamFeedTest(unittest.TestCase):
    def test_fetches_and_tags_team(self):
        session = FakeSession()
        items = feeds.fetch_team_feed("BUF", session=session)
        self.assertEqual(session.calls, [feeds.TEAM_FEEDS["BUF"]])
        self.assertTrue(all(i["team"] == "BUF" for i in items))

    def test_unknown_team_returns_empty(self):
        session = FakeSession()
        self.assertEqual(feeds.fetch_team_feed("XXX", session=session), [])
        self.assertEqual(session.calls, [])

    def test_network_error_returns_empty(self):
        session = FakeSession(boom=OSError("connection reset"))
        self.assertEqual(feeds.fetch_team_feed("KC", session=session), [])

    def test_http_error_returns_empty(self):
        self.assertEqual(feeds.fetch_team_feed("KC", session=FakeSession(status=503)), [])


if __name__ == "__main__":
    unittest.main()
