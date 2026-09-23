import { COPILOT_API_URL } from "./paths";

export interface AtRiskStudent {
  student_id: number;
  attendance: number;
  engagement_score: number;
  assessment_score: number;
  prediction: number;
  confidence: number;
}

export interface StudentDetail extends AtRiskStudent {
  cluster: number;
}

export async function fetchAtRiskStudents(
  minConfidence = 0,
): Promise<AtRiskStudent[]> {
  const res = await fetch(
    `${COPILOT_API_URL}/students/at-risk?min_confidence=${minConfidence}`,
    { cache: "no-store" },
  );

  if (!res.ok) {
    throw new Error(`copilot API error (${res.status}) listing at-risk students`);
  }

  return res.json();
}

export async function fetchStudentDetail(
  studentId: number,
): Promise<StudentDetail> {
  const res = await fetch(`${COPILOT_API_URL}/students/${studentId}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(
      `copilot API error (${res.status}) fetching student ${studentId}`,
    );
  }

  return res.json();
}
