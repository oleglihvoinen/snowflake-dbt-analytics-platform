from src.incremental_control import Change, build_window, merge_changes, reconcile, utc


def change(key, ts, payload, deleted=False):
    return Change(key, utc(ts), payload, deleted)


def test_watermark_uses_lookback_for_late_arrivals():
    window = build_window(utc("2026-10-01T10:00:00Z"), utc("2026-10-01T11:00:00Z"), 30)
    assert window.extraction_start == utc("2026-10-01T09:30:00Z")


def test_reprocessing_same_batch_is_idempotent():
    batch = [change("O1", "2026-10-01T10:00:00Z", "a")]
    once = merge_changes({}, batch)
    twice = merge_changes(once, batch)
    assert once == twice


def test_late_older_change_does_not_overwrite_newer_state():
    state = {"O1": change("O1", "2026-10-01T11:00:00Z", "new")}
    result = merge_changes(state, [change("O1", "2026-10-01T10:30:00Z", "old")])
    assert result["O1"].payload_hash == "new"


def test_delete_removes_current_state():
    state = {"O1": change("O1", "2026-10-01T10:00:00Z", "a")}
    result = merge_changes(state, [change("O1", "2026-10-01T11:00:00Z", "b", True)])
    assert "O1" not in result


def test_reconciliation_reports_content_drift():
    source = [change("O1", "2026-10-01T10:00:00Z", "expected")]
    target = {"O1": change("O1", "2026-10-01T10:00:00Z", "wrong")}
    report = reconcile(source, target)
    assert report["balanced"] is False
    assert report["hash_mismatch_keys"] == ["O1"]
