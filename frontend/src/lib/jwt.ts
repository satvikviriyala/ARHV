export type TokenClaims = {
  sub?: string;
  asr?: string;
  prf?: string;
  exp?: number;
  jti?: string;
  cid?: string;
};

export function decodePayload(token: string): TokenClaims {
  try {
    const part = token.split(".")[1];
    if (!part) return {};
    const padded = part.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((part.length + 3) % 4);
    return JSON.parse(atob(padded)) as TokenClaims;
  } catch {
    return {};
  }
}
