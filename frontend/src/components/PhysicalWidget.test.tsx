import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "../lib/api";
import type { ImuChallenge, ImuTrace } from "../lib/imu";
import PhysicalWidget from "./PhysicalWidget";

vi.mock("./TiltChallenge", () => ({
  default: ({ onDone }: { onDone: (trace: ImuTrace) => void }) => (
    <button
      type="button"
      onClick={() =>
        onDone({
          challengeId: "ch_0123456789abcdef01234567",
          nonce: "0123456789abcdef0123456789abcdef",
          samples: [],
        })
      }
    >
      Submit sensor trace
    </button>
  ),
}));

const challenge: ImuChallenge = {
  challengeId: "ch_0123456789abcdef01234567",
  expiresAt: 1_789_999_999,
  family: "imu-v1",
  nonce: "0123456789abcdef0123456789abcdef",
  targets: [
    { dBeta: 20, dGamma: 0, radius: 8, holdMs: 450 },
    { dBeta: 0, dGamma: 20, radius: 8, holdMs: 450 },
    { dBeta: -20, dGamma: 0, radius: 8, holdMs: 450 },
  ],
  baselineMs: 600,
  maxDurationMs: 30_000,
  sampleHz: 60,
};

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("PhysicalWidget mobile sensor path", () => {
  it("shows neutral retry guidance and focuses sensor retry after an incomplete signal", async () => {
    vi.spyOn(api, "createChallenge").mockResolvedValue(challenge);
    vi.spyOn(api, "submitTrace").mockResolvedValue({
      passed: false,
      reasons: ["gravity"],
      metrics: { gravityFrac: 0.5 },
    });

    render(<PhysicalWidget sensorOnly onVerified={vi.fn()} />);

    fireEvent.click(await screen.findByRole("button", { name: "Submit sensor trace" }));

    const message = await screen.findByText("Motion signal incomplete. Please try the sensors again.");
    expect(message).toBeTruthy();
    expect(screen.queryByText(/suspicious activity/i)).toBeNull();
    expect(screen.queryByText(/bot|agent/i)).toBeNull();

    const retry = screen.getByRole("button", { name: "Try sensors again" });
    await waitFor(() => expect(document.activeElement).toBe(retry));
    fireEvent.click(retry);
    await waitFor(() => expect(api.createChallenge).toHaveBeenCalledTimes(2));
  });
});
