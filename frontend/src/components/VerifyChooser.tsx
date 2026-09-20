import { useEffect, useRef, useState } from "react";
import QRCode from "qrcode";
import { getCohort } from "../lib/cohort";

type Props = {
  onChoose: (family: "imu-v1" | "mdg-v1") => void;
};

export default function VerifyChooser({ onChoose }: Props) {
  const canTilt =
    typeof DeviceMotionEvent !== "undefined" &&
    typeof window !== "undefined" &&
    window.matchMedia("(pointer: coarse)").matches;
  const [qr, setQr] = useState("");
  const firstChoice = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    firstChoice.current?.focus();
  }, [canTilt]);
  useEffect(() => {
    if (canTilt || typeof window === "undefined") return;
    const cohort = getCohort();
    const url = `${window.location.origin}/phone${cohort !== "public" ? `?cohort=${encodeURIComponent(cohort)}` : ""}`;
    void QRCode.toDataURL(url, { margin: 1, width: 220 }).then(setQr);
  }, [canTilt]);
  return (
    <div className="space-y-3">
      {canTilt ? (
        <>
          <button
            ref={firstChoice}
            type="button"
            onClick={() => onChoose("imu-v1")}
            className="w-full rounded-xl bg-accent p-4 text-left font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Tilt your phone gently <span className="block text-sm font-normal">Quick presence check · physical proof</span>
          </button>
          <button
            type="button"
            onClick={() => onChoose("mdg-v1")}
            className="w-full rounded-xl border border-line p-4 text-left focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Spot the moving shape <span className="block text-sm text-muted">Screen-based alternative · motion puzzle</span>
          </button>
        </>
      ) : (
        <>
          <button
            ref={firstChoice}
            type="button"
            onClick={() => onChoose("mdg-v1")}
            className="w-full rounded-xl bg-accent p-4 text-left font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Spot the moving shape <span className="block text-sm font-normal">Screen-based alternative · motion puzzle</span>
          </button>
          <div className="rounded-xl border border-line p-4 text-center">
            <p className="font-medium">Use your phone instead</p>
            {qr && <img src={qr} alt="QR code for the ARHV phone tilt check" className="mx-auto my-3 size-56" loading="lazy" />}
            <p className="text-sm text-muted">Scan with your phone camera. Tilt gently to confirm a journey—something a screen-only AI can&apos;t do.</p>
          </div>
        </>
      )}
    </div>
  );
}
