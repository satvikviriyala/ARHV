const COHORT = /^(public|study|local|agent:[a-z0-9.-]{1,40}:k[0-9]{1,2})$/;
const KEY = "arhv-cohort";

export function getCohort(): string {
  if (typeof window === "undefined") return "public";
  const query = new URLSearchParams(window.location.search).get("cohort")?.toLowerCase() ?? "";
  if (COHORT.test(query)) {
    window.sessionStorage.setItem(KEY, query);
    return query;
  }
  return window.sessionStorage.getItem(KEY) ?? "public";
}

export function cohortHeader(): { "x-pact-cohort": string } {
  return { "x-pact-cohort": getCohort() };
}
