<?php
// Executed on the IONOS host via cbs-league-history's run_remote_php.py
// (which prepends the site bootstrap). Pulls v1/manifest.json and mirrors
// changed boards into MySQL; unchanged profiles are skipped by sha256.
echo json_encode(pigskin_rankings_import()), PHP_EOL;
