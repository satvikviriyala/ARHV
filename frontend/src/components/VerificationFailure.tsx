import { useEffect, useRef } from "react";

type Props = {
  onRetry: () => void;
  context?: string;
};

export default function VerificationFailure({
  onRetry,
  context = "The booking was not completed. Your journey details are still here.",
}: Props) {
  const heading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    heading.current?.focus();
  }, []);

  return (
    <section
      className="rounded-2xl border border-bad bg-bad/5 p-5"
      role="alert"
      aria-labelledby="verification-failure-heading"
    >
      <p className="font-mono text-xs tracking-[0.18em] text-bad">VERIFICATION REQUIRED</p>
      <h2
        id="verification-failure-heading"
        ref={heading}
        tabIndex={-1}
        className="mt-2 text-2xl font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        Verification could not be confirmed
      </h2>
      <p className="mt-2 font-medium text-bad">Suspicious activity detected. Please try human verification again.</p>
      <p className="mt-2 text-sm text-muted">{context}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-5 rounded-xl bg-accent px-5 py-3 font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        Try verification again
      </button>
    </section>
  );
}
