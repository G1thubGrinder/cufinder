import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { ApiError } from "../api/client-error";
import { CU_EMAIL_REGEX } from "../types";
import { USE_MOCK } from "../api/client";
import styles from "./LoginPage.module.css";

interface LocationState {
  from?: string;
}

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as LocationState | null)?.from ?? "/";
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    const trimmed = email.trim().toLowerCase();
    if (!CU_EMAIL_REGEX.test(trimmed)) {
      setError("Please use your CU email (e.g. yourname@student.chula.ac.th).");
      return;
    }
    setSubmitting(true);
    try {
      await login(trimmed);
      navigate(from, { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <Link to="/" className={styles.brand}>
          <span className={styles.brandMark}>CU</span>Finder
        </Link>
        <h1 className={styles.title}>Sign in</h1>
        <p className={styles.subtitle}>Use your Chulalongkorn University email to continue.</p>

        <form onSubmit={handleSubmit} noValidate>
          <label className={styles.label} htmlFor="email">
            CU email
          </label>
          <input
            id="email"
            className={styles.input}
            type="email"
            placeholder="yourname@student.chula.ac.th"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            autoFocus
            required
          />
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" className={styles.submit} disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        {USE_MOCK && (
          <div className={styles.demoBlock}>
            <p className={styles.demoTitle}>Demo accounts (mock mode)</p>
            <ul className={styles.demoList}>
              <li>
                <button
                  type="button"
                  className={styles.demoBtn}
                  onClick={() => setEmail("library.admin@chula.ac.th")}
                >
                  library.admin@chula.ac.th
                </button>
                <span> — Library admin</span>
              </li>
              <li>
                <button
                  type="button"
                  className={styles.demoBtn}
                  onClick={() => setEmail("eng.admin@chula.ac.th")}
                >
                  eng.admin@chula.ac.th
                </button>
                <span> — Engineering admin</span>
              </li>
              <li>
                <button
                  type="button"
                  className={styles.demoBtn}
                  onClick={() => setEmail("student@student.chula.ac.th")}
                >
                  student@student.chula.ac.th
                </button>
                <span> — Regular user (any CU email works)</span>
              </li>
            </ul>
          </div>
        )}

        <p className={styles.backLink}>
          <Link to="/">&larr; Back to browse</Link>
        </p>
      </div>
    </div>
  );
}
