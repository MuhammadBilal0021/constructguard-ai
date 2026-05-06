"""
ConstructGuard AI — Escalation Engine
SQLite-based site memory + autonomous escalation logic.
Stores violation history per site and detects dangerous patterns.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_DIR = Path(__file__).parent.parent / "database"
DB_PATH = DB_DIR / "constructguard_memory.db"


def _get_connection() -> sqlite3.Connection:
    """Get SQLite connection, creating DB and tables if needed."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Create tables on first run
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            total_workers INTEGER DEFAULT 0,
            total_violations INTEGER DEFAULT 0,
            escalation_level TEXT DEFAULT 'normal',
            risk_score REAL DEFAULT 0.0,
            violations_json TEXT,
            report_path TEXT
        );

        CREATE TABLE IF NOT EXISTS violation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            violation_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            location TEXT,
            reasoning TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_analyses_site ON analyses(site_id);
        CREATE INDEX IF NOT EXISTS idx_violation_log_site ON violation_log(site_id);
    """)
    conn.commit()
    return conn


def store_analysis(site_id: str, violations: list, risk_score: float,
                   escalation_level: str, report_path: str = None) -> int:
    """
    Store a complete analysis result in site memory.
    Returns the analysis ID.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO analyses
               (site_id, timestamp, total_workers, total_violations,
                escalation_level, risk_score, violations_json, report_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                site_id,
                datetime.now().isoformat(),
                0,  # updated later if needed
                len(violations),
                escalation_level,
                risk_score,
                json.dumps(violations),
                report_path,
            )
        )
        analysis_id = cursor.lastrowid

        # Log each individual violation
        for v in violations:
            vtype = v.get("violation_type", v.get("type", "unknown"))
            conn.execute(
                """INSERT INTO violation_log
                   (site_id, timestamp, violation_type, severity, location, reasoning)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    site_id,
                    datetime.now().isoformat(),
                    vtype,
                    v.get("severity", "medium"),
                    v.get("location", "unknown"),
                    v.get("reasoning", ""),
                )
            )

        conn.commit()
        return analysis_id
    finally:
        conn.close()


def check_escalation(site_id: str, current_violations: list) -> dict:
    """
    Autonomous escalation logic.
    Checks current session + historical patterns to decide escalation level.

    Rules:
    - 3+ critical violations in current session → EMERGENCY
    - 1-2 critical violations → HIGH
    - Same violation type 3+ times in last 7 days → SYSTEMIC flag
    - 5+ total violations in current session → ELEVATED
    - Otherwise → NORMAL
    """
    # Count current session critical violations
    critical_count = sum(
        1 for v in current_violations
        if v.get("severity", "").lower() == "critical"
    )
    high_count = sum(
        1 for v in current_violations
        if v.get("severity", "").lower() == "high"
    )
    total_count = len(current_violations)

    # Check historical patterns
    systemic_issues = []
    try:
        conn = _get_connection()
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

        # Find repeated violation types in last 7 days
        rows = conn.execute(
            """SELECT violation_type, COUNT(*) as cnt
               FROM violation_log
               WHERE site_id = ? AND timestamp > ?
               GROUP BY violation_type
               HAVING cnt >= 3""",
            (site_id, seven_days_ago)
        ).fetchall()

        systemic_issues = [
            {"violation_type": row["violation_type"], "occurrences": row["cnt"]}
            for row in rows
        ]
        conn.close()
    except Exception:
        pass  # If DB fails, still process current session

    # Determine escalation level
    if critical_count >= 3:
        level = "emergency"
        message = (
            f"🚨 EMERGENCY — {critical_count} critical violations detected. "
            f"Immediate stop-work order recommended. Site supervisor and safety "
            f"officer must be notified immediately."
        )
    elif critical_count >= 1:
        level = "high"
        message = (
            f"⚠️ HIGH ALERT — {critical_count} critical violation(s) detected. "
            f"Immediate supervisor notification required. Workers in affected "
            f"zones must halt operations until PPE compliance is verified."
        )
    elif high_count >= 2 or total_count >= 5:
        level = "elevated"
        message = (
            f"📋 ELEVATED — {total_count} total violations detected including "
            f"{high_count} high-severity issues. Safety briefing recommended "
            f"before next shift."
        )
    else:
        level = "normal"
        message = (
            f"✅ Normal operations — {total_count} minor violation(s) detected. "
            f"Standard corrective actions logged."
        )

    # Add systemic warning if applicable
    if systemic_issues:
        systemic_types = ", ".join(s["violation_type"] for s in systemic_issues)
        message += (
            f"\n\n🔄 SYSTEMIC PATTERN DETECTED: {systemic_types} — "
            f"recurring violations over the past 7 days indicate a training "
            f"or equipment supply issue. Management review recommended."
        )

    return {
        "escalation_level": level,
        "message": message,
        "critical_count": critical_count,
        "high_count": high_count,
        "total_violations": total_count,
        "systemic_issues": systemic_issues,
    }


def get_site_history(site_id: str, limit: int = 20) -> list[dict]:
    """Get violation history for a specific site."""
    try:
        conn = _get_connection()
        rows = conn.execute(
            """SELECT id, site_id, timestamp, total_violations,
                      escalation_level, risk_score
               FROM analyses
               WHERE site_id = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (site_id, limit)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []


def get_all_sites() -> list[str]:
    """Get list of all known site IDs."""
    try:
        conn = _get_connection()
        rows = conn.execute(
            "SELECT DISTINCT site_id FROM analyses ORDER BY site_id"
        ).fetchall()
        conn.close()
        return [row["site_id"] for row in rows]
    except Exception:
        return []
