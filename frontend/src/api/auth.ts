import { api } from "./client";
import type { User } from "../types";

export const authApi = {
  login: (email: string) =>
    api<User>("/api/auth/login", { method: "POST", body: { email } }),
  logout: () => api<void>("/api/auth/logout", { method: "POST" }),
  me: () => api<User>("/api/auth/me"),
};
