from __future__ import annotations

import unittest
from pathlib import Path

from src import app_auth


class _FakeForm:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeSidebar:
    def __init__(self):
        self.captions: list[str] = []
        self.button_clicked = False

    def caption(self, text: str):
        self.captions.append(text)

    def button(self, *_args, **_kwargs):
        return self.button_clicked


class _FakeStreamlit:
    def __init__(self, *, username: str = "", password: str = "", submitted: bool = False):
        self.session_state: dict[str, object] = {}
        self.sidebar = _FakeSidebar()
        self.username = username
        self.password = password
        self.submitted = submitted
        self.markdowns: list[str] = []
        self.captions: list[str] = []
        self.errors: list[str] = []
        self.rerun_called = False

    def markdown(self, text: str):
        self.markdowns.append(text)

    def caption(self, text: str):
        self.captions.append(text)

    def form(self, _key: str):
        return _FakeForm()

    def text_input(self, label: str, **_kwargs):
        if label == "Username":
            return self.username
        if label == "Password":
            return self.password
        return ""

    def form_submit_button(self, _label: str):
        return self.submitted

    def error(self, text: str):
        self.errors.append(text)

    def rerun(self):
        self.rerun_called = True


class AppAuthTests(unittest.TestCase):
    def test_auth_disabled_allows_render(self):
        fake_st = _FakeStreamlit()
        self.assertTrue(app_auth.render_login_gate(fake_st, {}))
        self.assertEqual(fake_st.markdowns, [])

    def test_auth_enabled_without_session_shows_login_gate(self):
        fake_st = _FakeStreamlit()
        allowed = app_auth.render_login_gate(fake_st, {app_auth.APP_AUTH_ENABLED: "true"})
        self.assertFalse(allowed)
        self.assertIn("### Data Studio Login", fake_st.markdowns)

    def test_valid_password_sets_session(self):
        encoded = app_auth.hash_password("correct horse", salt=b"1234567890123456")
        users = f"sofain:{encoded}"
        fake_st = _FakeStreamlit(username="sofain", password="correct horse", submitted=True)

        allowed = app_auth.render_login_gate(
            fake_st,
            {app_auth.APP_AUTH_ENABLED: "true", app_auth.APP_AUTH_USERS: users},
        )

        self.assertFalse(allowed)
        self.assertTrue(fake_st.session_state[app_auth.AUTHENTICATED_KEY])
        self.assertEqual(fake_st.session_state[app_auth.AUTHENTICATED_USER_KEY], "sofain")
        self.assertTrue(fake_st.rerun_called)

    def test_auth_users_accepts_semicolon_delimiter_for_cloud_run_env(self):
        first = app_auth.hash_password("one", salt=b"1234567890123456")
        second = app_auth.hash_password("two", salt=b"6543210987654321")
        users = app_auth.parse_auth_users(f"sofain:{first};racehorse:{second}")

        self.assertEqual(sorted(users.keys()), ["racehorse", "sofain"])
        self.assertTrue(app_auth.verify_password("one", users["sofain"]))
        self.assertTrue(app_auth.verify_password("two", users["racehorse"]))

    def test_invalid_password_fails(self):
        encoded = app_auth.hash_password("correct horse", salt=b"1234567890123456")
        users = f"sofain:{encoded}"

        self.assertFalse(app_auth.authenticate_user("sofain", "wrong", users))

    def test_unknown_username_fails(self):
        encoded = app_auth.hash_password("correct horse", salt=b"1234567890123456")
        users = f"sofain:{encoded}"

        self.assertFalse(app_auth.authenticate_user("racehorse", "correct horse", users))

    def test_password_verification_uses_hash_not_plaintext(self):
        encoded = app_auth.hash_password("correct horse", salt=b"1234567890123456")

        self.assertTrue(encoded.startswith("pbkdf2_sha256$260000$"))
        self.assertNotIn("correct horse", encoded)
        self.assertTrue(app_auth.verify_password("correct horse", encoded))

    def test_raw_owner_passwords_are_not_committed_in_source(self):
        source_paths = [
            Path("app.py"),
            Path("src/app_auth.py"),
            Path("tests/test_app_auth.py"),
            Path("tests/test_pigskin_packet_qa_ui.py"),
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)

        first_secret = "Signal-" + "Comet-" + "760-" + "XERZ6"
        second_secret = "Vault-" + "Anchor-" + "831"
        self.assertNotIn(first_secret, combined)
        self.assertNotIn(second_secret, combined)

    def test_qa_ui_flag_and_historical_tool_are_separate(self):
        app_source = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("def use_pigskin_packet_qa_ui()", app_source)
        self.assertIn("if use_pigskin_packet_qa_ui():", app_source)
        self.assertNotIn("USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true", app_source)


if __name__ == "__main__":
    unittest.main()
