// PACT authorization policies.
// Cedar semantics: default DENY; any matching `forbid` overrides every `permit`.

// P1 - A visitor who passed the PACT motion challenge may book (token is single-use).
@id("permit-motion-book")
permit (
  principal is Pact::Visitor,
  action == Pact::Action::"BookTicket",
  resource is Pact::Counter
)
when { principal.assurance == "motion" };

// P2 - Accessible path (WCAG 2.2 SC 3.3.8): a verified account may book without any
// cognitive test, but with a daily quota because account assurance is weaker.
@id("permit-account-book-with-quota")
permit (
  principal is Pact::Visitor,
  action == Pact::Action::"BookTicket",
  resource is Pact::Counter
)
when { principal.assurance == "account" && context.bookingsToday < 2 };

// F1 - Every PACT token is single-use. A replayed token is always denied.
@id("forbid-token-replay")
forbid (principal, action, resource)
when { context.tokenReplayed };
