"use server";

import fs from "fs";
import path from "path";
import { revalidatePath } from "next/cache";
import { decideIntervention } from "@/lib/db";
import { AUDIT_LOG_PATH } from "@/lib/paths";

function csvEscape(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function appendAuditLog(entry: Record<string, string | number>): void {
  fs.mkdirSync(path.dirname(AUDIT_LOG_PATH), { recursive: true });

  const headers = Object.keys(entry);
  const isNew = !fs.existsSync(AUDIT_LOG_PATH);

  if (isNew) {
    fs.appendFileSync(AUDIT_LOG_PATH, headers.join(",") + "\n");
  }

  fs.appendFileSync(
    AUDIT_LOG_PATH,
    headers.map((h) => csvEscape(String(entry[h]))).join(",") + "\n",
  );
}

export async function approveIntervention(formData: FormData): Promise<void> {
  const id = Number(formData.get("id"));
  const intervention = decideIntervention(id, "executed", "staff-demo-user");

  // The only place a "real" effect happens - and it's a log line, never an
  // actual send. Approving in the UI is the entire human-in-the-loop gate.
  appendAuditLog({
    intervention_id: intervention.id,
    student_id: intervention.student_id,
    action_type: intervention.action_type,
    decided_at: intervention.decided_at ?? "",
    decided_by: intervention.decided_by ?? "",
    status: intervention.status,
  });

  revalidatePath("/queue");
  revalidatePath("/");
}

export async function rejectIntervention(formData: FormData): Promise<void> {
  const id = Number(formData.get("id"));
  decideIntervention(id, "rejected", "staff-demo-user");

  revalidatePath("/queue");
  revalidatePath("/");
}
