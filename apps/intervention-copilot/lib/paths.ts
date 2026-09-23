import path from "path";

// apps/intervention-copilot -> repo root is two levels up.
export const REPO_ROOT = path.resolve(process.cwd(), "..", "..");

export const AUDIT_LOG_PATH = path.join(
  REPO_ROOT,
  "data",
  "intervention_audit_log.csv",
);

export const COPILOT_API_URL =
  process.env.COPILOT_API_URL ?? "http://127.0.0.1:8000";
