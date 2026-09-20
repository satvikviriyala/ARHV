export type VerificationDisposition = "retry" | "suspicious";

export function verificationDisposition(
  reasons: string[] = [],
  metrics: Record<string, unknown> = {},
): VerificationDisposition {
  const gyroCorr = Array.isArray(metrics.gyroCorr)
    ? metrics.gyroCorr.filter((value): value is number => typeof value === "number")
    : [];
  const gravityFrac = typeof metrics.gravityFrac === "number" ? metrics.gravityFrac : 1;
  const tiltErr = typeof metrics.tiltErrDeg === "number" ? metrics.tiltErrDeg : 0;

  if (reasons.includes("binding") || reasons.includes("continuity")) return "suspicious";
  if (reasons.includes("gravity") && gravityFrac < 0.8) return "suspicious";
  if (reasons.includes("tilt") && (metrics.tiltErrDeg === null || tiltErr > 30)) return "suspicious";
  if (reasons.includes("gyro") && (!gyroCorr.length || gyroCorr.every((value) => value < 0.35))) return "suspicious";
  return "retry";
}

export function reasonMessage(reasons: string[] = []): string {
  if (reasons.includes("targets")) return "You didn't reach all three rings in order. Hold the dot inside each ring until it fills.";
  if (reasons.includes("timing")) return "That took too long or the sensor stream stalled. Keep the page open and try again.";
  if (reasons.some((reason) => ["gravity", "tilt", "gyro", "continuity"].includes(reason))) {
    return "The motion reading was ambiguous this time. Keep the phone moving gently and try the fresh check again.";
  }
  if (reasons.some((reason) => ["binding", "size", "format"].includes(reason))) {
    return "Something went wrong with this check. Start a new one.";
  }
  return "The physical check did not pass. Try again with your phone in portrait mode.";
}
