import { config } from "../config";
import type { ImuChallenge, ImuTrace } from "./imu";

export type MdgRound = { frames: string; frameCount: number; options: string[] };
export type MdgChallenge = {
  challengeId: string;
  expiresAt: number;
  family: "mdg-v1";
  width: number;
  height: number;
  dot: number;
  fps: number;
  playback: "pingpong";
  rounds: MdgRound[];
};
export type Booking = {
  bookingId: string;
  pnr: string;
  seat: string;
  counter: string;
  assurance: string;
  policy: string;
  createdAt: number;
  bookingsToday?: number;
};
export type Stats = {
  family: string;
  chance: { round: number; pass: number } | null;
  cohorts: Array<{
    cohort: string;
    attempts: number;
    passes: number;
    passRate: number;
    passCi: [number, number];
    roundAccuracy: number;
    roundCi: [number, number];
    meanMs: number;
  }>;
};
export type Health = {
  ok: boolean;
  stage: string;
  agentModels: string[];
  cloudAgents: boolean;
};
export type AgentRunRound = {
  index: number;
  options: string[];
  frameUrls?: string[];
  answer?: string | null;
  confidence?: number | null;
  rationale?: string;
  valid?: boolean;
  latencyMs?: number;
  repaired?: boolean;
  error?: string | null;
  truth?: string;
  correct?: boolean;
};
export type AgentRun = {
  runId: string;
  status: "queued" | "running" | "done" | "error";
  model: string;
  modelId: string;
  frames: number;
  progress: number;
  createdAt: number;
  startedAt?: number;
  finishedAt?: number;
  passed: boolean;
  roundsCorrect: number;
  error: string | null;
  rounds: AgentRunRound[];
  replay?: MdgChallenge;
};
export type ImuAnswer = {
  passed: boolean;
  token?: string;
  assurance?: "physical";
  proof?: "imu-v1";
  reasons?: string[];
  metrics?: Record<string, unknown>;
};
export type MdgAnswer = {
  passed: boolean;
  token?: string;
  assurance?: "motion";
  roundsCorrect?: number;
};
export type ApiCall = { method: string; path: string; status: number; ms: number };

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const calls: ApiCall[] = [];

export function getApiLog(): ApiCall[] {
  return [...calls];
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  extraHeaders: Record<string, string> = {},
): Promise<T> {
  if (!config.apiUrl) {
    throw new ApiError(0, "missing_config", "The API URL is not configured. Run make web-env first.");
  }
  const started = performance.now();
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 20_000);
  let response: Response;
  try {
    response = await fetch(`${config.apiUrl}${path}`, {
      method,
      signal: controller.signal,
      headers: { "content-type": "application/json", ...extraHeaders },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (error) {
    const message = error instanceof DOMException && error.name === "AbortError" ? "The request timed out." : "Network error.";
    throw new ApiError(0, "network", message);
  } finally {
    window.clearTimeout(timer);
  }
  const ms = Math.round(performance.now() - started);
  calls.push({ method, path, status: response.status, ms });
  if (calls.length > 20) calls.shift();
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    payload = {};
  }
  if (!response.ok) {
    const error = payload as { error?: { code?: string; message?: string } };
    throw new ApiError(
      response.status,
      error.error?.code ?? `http_${response.status}`,
      error.error?.message ?? `Request failed (${response.status}).`,
    );
  }
  return payload as T;
}

export const api = {
  health: () => request<Health>("GET", "/v1/health"),
  createChallenge: (options: { family?: "mdg-v1" | "imu-v1"; cohort?: string } = {}) =>
    request<MdgChallenge | ImuChallenge>("POST", "/v1/challenges", options, options.cohort ? { "x-pact-cohort": options.cohort } : {}),
  submitAnswers: (challengeId: string, answers: string[], timingsMs: number[], cohort?: string) =>
    request<MdgAnswer>("POST", `/v1/challenges/${challengeId}/answers`, { answers, timingsMs }, cohort ? { "x-pact-cohort": cohort } : {}),
  submitTrace: (challengeId: string, trace: ImuTrace, cohort?: string) =>
    request<ImuAnswer>("POST", `/v1/challenges/${challengeId}/answers`, { trace }, cohort ? { "x-pact-cohort": cohort } : {}),
  book: (token: string) => request<Booking>("POST", "/v1/demo/bookings", {}, { "x-pact-token": token }),
  explain: (token: string) =>
    request<{
      tokenValid: boolean;
      decision?: string;
      policies?: string[];
      claims?: Record<string, unknown>;
      replayed?: boolean;
    }>("POST", "/v1/authz/explain", { token }),
  stats: (family: "mdg-v1" | "imu-v1" = "mdg-v1") => request<Stats>("GET", `/v1/stats?family=${family}`),
  startAgentRun: (model: string, frames: 1 | 4 | 8) =>
    request<{ runId: string; status: "queued" }>("POST", "/v1/agent-runs", { model, frames }),
  getAgentRun: (runId: string, options: { replay?: boolean } = {}) =>
    request<AgentRun>("GET", `/v1/agent-runs/${runId}${options.replay ? "?replay=1" : ""}`),
};
