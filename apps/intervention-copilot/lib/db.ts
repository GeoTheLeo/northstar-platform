import Database from "better-sqlite3";
import fs from "fs";
import path from "path";

const DB_DIR = path.join(process.cwd(), "data");
fs.mkdirSync(DB_DIR, { recursive: true });

const db = new Database(path.join(DB_DIR, "interventions.db"));
db.pragma("journal_mode = WAL");

db.exec(`
  CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    rationale TEXT NOT NULL,
    message_draft TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_approval',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    decided_at TEXT,
    decided_by TEXT
  );
`);

export type InterventionStatus = "pending_approval" | "executed" | "rejected";

export interface Intervention {
  id: number;
  student_id: number;
  action_type: string;
  rationale: string;
  message_draft: string;
  status: InterventionStatus;
  created_at: string;
  decided_at: string | null;
  decided_by: string | null;
}

const POLICY_COOLDOWN_DAYS = 30;

export function getInterventionPolicyCooldownDays(): number {
  return POLICY_COOLDOWN_DAYS;
}

export function getIntervention(id: number): Intervention | undefined {
  return db
    .prepare(`SELECT * FROM interventions WHERE id = ?`)
    .get(id) as Intervention | undefined;
}

export function listInterventions(status?: InterventionStatus): Intervention[] {
  if (status) {
    return db
      .prepare(
        `SELECT * FROM interventions WHERE status = ? ORDER BY created_at DESC`,
      )
      .all(status) as Intervention[];
  }

  return db
    .prepare(`SELECT * FROM interventions ORDER BY created_at DESC`)
    .all() as Intervention[];
}

// A student is "protected" if they already have a proposal that's pending
// review or was already executed within the cooldown window. A rejected
// proposal does not block a new attempt.
export function hasRecentIntervention(studentId: number): boolean {
  const row = db
    .prepare(
      `SELECT COUNT(*) as count FROM interventions
       WHERE student_id = ?
         AND status != 'rejected'
         AND created_at >= datetime('now', ?)`,
    )
    .get(studentId, `-${POLICY_COOLDOWN_DAYS} days`) as { count: number };

  return row.count > 0;
}

export function createIntervention(input: {
  student_id: number;
  action_type: string;
  rationale: string;
  message_draft: string;
}): Intervention {
  const result = db
    .prepare(
      `INSERT INTO interventions (student_id, action_type, rationale, message_draft)
       VALUES (@student_id, @action_type, @rationale, @message_draft)`,
    )
    .run(input);

  return getIntervention(Number(result.lastInsertRowid))!;
}

export function decideIntervention(
  id: number,
  status: "executed" | "rejected",
  decidedBy: string,
): Intervention {
  db.prepare(
    `UPDATE interventions
     SET status = ?, decided_at = datetime('now'), decided_by = ?
     WHERE id = ?`,
  ).run(status, decidedBy, id);

  const updated = getIntervention(id);

  if (!updated) {
    throw new Error(`intervention ${id} not found after update`);
  }

  return updated;
}

export default db;
