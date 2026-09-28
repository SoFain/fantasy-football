<?php
// Executed on the IONOS host via cbs-league-history's run_remote_php.py
// (which prepends the site bootstrap). Pulls v1/manifest.json and mirrors
// changed boards into MySQL; unchanged profiles are skipped by sha256.
$result = pigskin_rankings_import();
echo json_encode($result), PHP_EOL;
foreach (['standard', 'ppr', 'half_ppr', 'gng_keeper'] as $profile) {
    $status = (string) ($result[$profile] ?? 'missing profile');
    if ($status !== 'unchanged, kept' && !preg_match('/^[1-9][0-9]* rows$/', $status)) {
        throw new RuntimeException('Ranking import failed for ' . $profile . ': ' . $status);
    }
}
$inseasonStatus = (string) ($result['inseason_rankings'] ?? 'missing in-season result');
if ($inseasonStatus !== 'unchanged, kept'
    && !preg_match('/^imported [A-Za-z0-9_.-]+, week (?:[2-9]|1[0-8])$/D', $inseasonStatus)) {
    throw new RuntimeException('In-season ranking import failed: ' . $inseasonStatus);
}
