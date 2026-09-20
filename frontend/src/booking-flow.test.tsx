import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router";
import BookingCard from "./components/BookingCard";
import BookingConfirmation from "./components/BookingConfirmation";
import VerificationFailure from "./components/VerificationFailure";
import { api, ApiError, type Booking } from "./lib/api";
import { DEFAULT_JOURNEY, TRAIN_OPTIONS } from "./lib/rail";

const booking: Booking = {
  bookingId: "bk_demo",
  pnr: "4821930675",
  seat: "B2-34",
  counter: "Rush Hour Counter (demo)",
  assurance: "physical",
  policy: "permit-physical-book",
  createdAt: 1_789_999_999,
};

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("booking result flow", () => {
  it("renders a dedicated confirmation page with the selected journey details", () => {
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: "/booking/confirmed",
            state: { booking, journey: DEFAULT_JOURNEY, train: TRAIN_OPTIONS[0]! },
          },
        ]}
      >
        <Routes>
          <Route path="/booking/confirmed" element={<BookingConfirmation />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Your ticket is confirmed" })).toBeTruthy();
    expect(screen.getByText(booking.pnr)).toBeTruthy();
    expect(screen.getByText("Bengaluru → Visakhapatnam")).toBeTruthy();
    expect(screen.getByText(DEFAULT_JOURNEY.travelClass)).toBeTruthy();
    expect(screen.getByRole("link", { name: /Book another journey/i })).toBeTruthy();
  });

  it("shows the suspicious-activity state for a booking authorization failure", async () => {
    vi.spyOn(api, "book").mockRejectedValue(new ApiError(403, "http_403", "Forbidden"));
    const onRetry = vi.fn();

    render(<BookingCard token="expired-demo-token" onRetry={onRetry} />);

    expect(await screen.findByText("Suspicious activity detected. Please try human verification again.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Try verification again" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("passes a successful booking response to the confirmation transition", async () => {
    vi.spyOn(api, "book").mockResolvedValue(booking);
    const onBooked = vi.fn();

    render(<BookingCard token="fresh-demo-token" onBooked={onBooked} onRetry={vi.fn()} />);

    await waitFor(() => expect(onBooked).toHaveBeenCalledWith(booking));
    expect(screen.getByText("Journey confirmed")).toBeTruthy();
  });

  it("exposes a keyboard-accessible retry action for verification", () => {
    const onRetry = vi.fn();
    render(<VerificationFailure onRetry={onRetry} />);

    const retry = screen.getByRole("button", { name: "Try verification again" });
    retry.focus();
    fireEvent.keyDown(retry, { key: "Enter" });
    fireEvent.click(retry);

    expect(onRetry).toHaveBeenCalledOnce();
  });
});
