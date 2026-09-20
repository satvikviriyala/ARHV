import { beforeEach, describe, expect, it, vi } from "vitest";
import { api, ApiError } from "./api";
import { config } from "../config";

describe("api client", () => {
  beforeEach(() => {
    config.apiUrl = "https://example.test";
    vi.restoreAllMocks();
  });

  it("maps structured API errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ error: { code: "bad_family", message: "Unknown challenge family" } }), {
          status: 400,
          headers: { "content-type": "application/json" },
        }),
      ),
    );
    await expect(api.createChallenge({ family: "imu-v1" })).rejects.toMatchObject({
      status: 400,
      code: "bad_family",
    } satisfies Partial<ApiError>);
  });

  it("sends the physical family and cohort header", async () => {
    const challenge = { challengeId: "ch_test", family: "imu-v1", nonce: "00".repeat(16), targets: [] };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(challenge), { status: 201 })));
    await api.createChallenge({ family: "imu-v1", cohort: "study" });
    expect(fetch).toHaveBeenCalledWith(
      "https://example.test/v1/challenges",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ "x-pact-cohort": "study" }),
      }),
    );
  });
});
