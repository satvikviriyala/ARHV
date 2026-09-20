import { useState } from "react";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "../lib/api";
import type { ImuChallenge, ImuTrace } from "../lib/imu";
import BookingCard from "./BookingCard";
import PhysicalWidget from "./PhysicalWidget";

vi.mock("./TiltChallenge", () => ({
  default: function CheckpointDriver({ onDone }: { onDone: (trace: ImuTrace) => void }) {
    const [completed, setCompleted] = useState(0);
    return (
      <button
        type="button"
        onClick={() => {
          if (completed === 2) {
            onDone({
              challengeId: "ch_0123456789abcdef01234567",
              nonce: "0123456789abcdef0123456789abcdef",
              samples: [],
            });
          } else {
            setCompleted((value) => value + 1);
          }
        }}
      >
        Complete checkpoint {completed + 1}
      </button>
    );
  },
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

    const checkpoint = await screen.findByRole("button", { name: "Complete checkpoint 1" });
    fireEvent.click(checkpoint);
    fireEvent.click(screen.getByRole("button", { name: "Complete checkpoint 2" }));
    fireEvent.click(screen.getByRole("button", { name: "Complete checkpoint 3" }));

    const message = await screen.findByText("Motion signal incomplete. Please try the sensors again.");
    expect(message).toBeTruthy();
    expect(screen.queryByText(/suspicious activity/i)).toBeNull();
    expect(screen.queryByText(/bot|agent/i)).toBeNull();

    const retry = screen.getByRole("button", { name: "Try sensors again" });
    await waitFor(() => expect(document.activeElement).toBe(retry));
    fireEvent.click(retry);
    await waitFor(() => expect(api.createChallenge).toHaveBeenCalledTimes(2));
  });

  it("moves from all three checkpoints directly to verified booking", async () => {
    const booking = {
      bookingId: "bk_mobile",
      pnr: "4821930675",
      seat: "B2-34",
      counter: "Rush Hour Counter (demo)",
      assurance: "physical",
      policy: "permit-physical-book",
      createdAt: 1_789_999_999,
    };
    vi.spyOn(api, "createChallenge").mockResolvedValue(challenge);
    vi.spyOn(api, "submitTrace").mockResolvedValue({
      passed: true,
      token: "fresh-physical-token",
      assurance: "physical",
      proof: "imu-v1",
      metrics: { targetsReached: 3 },
    });
    vi.spyOn(api, "book").mockResolvedValue(booking);
    const onVerified = vi.fn();

    function MobileFlow() {
      const [token, setToken] = useState("");
      return token ? (
        <BookingCard token={token} onRetry={vi.fn()} />
      ) : (
        <PhysicalWidget sensorOnly onVerified={(value) => { onVerified(value); setToken(value); }} />
      );
    }

    render(<MobileFlow />);

    fireEvent.click(await screen.findByRole("button", { name: "Complete checkpoint 1" }));
    fireEvent.click(screen.getByRole("button", { name: "Complete checkpoint 2" }));
    fireEvent.click(screen.getByRole("button", { name: "Complete checkpoint 3" }));

    await waitFor(() => expect(onVerified).toHaveBeenCalledWith("fresh-physical-token"));
    expect(await screen.findByText("Journey confirmed")).toBeTruthy();
    expect(api.book).toHaveBeenCalledWith("fresh-physical-token");
    expect(screen.queryByText(/suspicious|bot|agent|moving shape|checkpoint/i)).toBeNull();
  });
});
