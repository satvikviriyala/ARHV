export function reasonMessage(reasons: string[] = []): string {
  if (reasons.includes("targets")) return "You didn't reach all three rings in order. Hold the dot inside each ring until it fills.";
  if (reasons.includes("timing")) return "That took too long or the sensor stream stalled. Keep the page open and try again.";
  if (reasons.some((reason) => ["gravity", "tilt", "gyro", "continuity"].includes(reason))) {
    return "Your device's sensors didn't behave like a phone moving in a hand. If you're emulating sensors, that's exactly what we check.";
  }
  if (reasons.some((reason) => ["binding", "size", "format"].includes(reason))) {
    return "Something went wrong with this check. Start a new one.";
  }
  return "The physical check did not pass. Try again with your phone in portrait mode.";
}
