const env = import.meta.env;

const required = {
  apiUrl: env.VITE_API_URL ?? "",
  region: env.VITE_REGION ?? "",
  userPoolId: env.VITE_USER_POOL_ID ?? "",
  userPoolClientId: env.VITE_USER_POOL_CLIENT_ID ?? "",
  stage: env.VITE_STAGE ?? "",
};

export const config = required;

export function missingConfig(): string[] {
  return Object.entries(required)
    .filter(([, value]) => !value)
    .map(([key]) => key);
}
