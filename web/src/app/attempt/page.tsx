"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, type Attempt, type Result } from "@/lib/api";

type PracticeFeedback = {
  is_correct: boolean;
  explanation: string;
  source_excerpt?: string;
};

export default function AttemptPage() {
  const router = useRouter();
  const [id, setId] = useState<string | null>(null);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string[]>>({});
  const [flags, setFlags] = useState<Record<string, boolean>>({});
  const [result, setResult] = useState<Result | null>(null);
  const [feedback, setFeedback] = useState<Record<string, PracticeFeedback>>({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
  const confirmDialog = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    setId(new URLSearchParams(window.location.search).get("id"));
  }, []);

  useEffect(() => {
    if (!id) return;
    api<Attempt>(`/attempts/${id}`)
      .then((data) => {
        setAttempt(data);
        setAnswers(
          Object.fromEntries(data.questions.map((question) => [question.key || question.id || "", question.selected_option_ids || []])),
        );
        setFlags(
          Object.fromEntries(data.questions.map((question) => [question.key || question.id || "", !!question.is_flagged])),
        );
      })
      .catch((cause) => setError(cause.message));
  }, [id]);

  useEffect(() => {
    if (!attempt?.expires_at) return;
    const tick = () => setSecondsLeft(Math.max(0, Math.floor((new Date(attempt.expires_at!).getTime() - Date.now()) / 1000)));
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [attempt]);

  async function saveResponse(questionKey: string, selectedOptionIds: string[], flagged = flags[questionKey] || false) {
    await api(`/attempts/${id}/responses/${questionKey}`, {
      method: "PUT",
      body: JSON.stringify({ selected_option_ids: selectedOptionIds, is_flagged: flagged }),
    });
  }

  async function chooseOption(optionId: string) {
    if (!attempt) return;
    const question = attempt.questions[index];
    const questionKey = question.key || question.id || "";
    const previous = answers[questionKey] || [];
    const selected = question.qtype === "multiple_select"
      ? previous.includes(optionId)
        ? previous.filter((value) => value !== optionId)
        : [...previous, optionId]
      : [optionId];
    setAnswers({ ...answers, [questionKey]: selected });
    try {
      await saveResponse(questionKey, selected);
    } catch (cause) {
      setError((cause as Error).message);
    }
  }

  const submit = useCallback(async () => {
    if (!id || busy || result) return;
    setBusy(true);
    setError("");
    try {
      setResult(await api<Result>(`/attempts/${id}/submit`, { method: "POST" }));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }, [id, busy, result]);

  useEffect(() => {
    if (secondsLeft === 0 && attempt?.mode === "exam" && !result) void submit();
  }, [attempt?.mode, result, secondsLeft, submit]);

  async function checkAnswer() {
    if (!attempt) return;
    const question = attempt.questions[index];
    const questionKey = question.key || question.id || "";
    try {
      const response = await api<PracticeFeedback>(`/attempts/${id}/responses/${questionKey}/check`, {
        method: "POST",
        body: JSON.stringify({ selected_option_ids: answers[questionKey] || [] }),
      });
      setFeedback({ ...feedback, [questionKey]: response });
    } catch (cause) {
      setError((cause as Error).message);
    }
  }

  if (!id) return <main className="shell">Missing attempt ID <button onClick={() => router.push("/")}>Home</button></main>;
  if (!attempt && !result) return <main className="shell">{error || "Loading assessment…"}</main>;

  if (result) {
    return (
      <main className="shell">
        <header className="top"><Link className="brand" href="/">StudyForge</Link><span>Results</span></header>
        <section className="hero">
          <div className="eyebrow">Assessment complete</div>
          <h1>{result.percentage}%</h1>
          <p>{result.score_points} / {result.max_points} points · {result.passed ? "Passed" : "Not passed"}</p>
          <div className="progress"><div style={{ width: `${result.percentage}%` }} /></div>
          <button className="btn primary" onClick={() => router.push("/")}>Dashboard</button>
        </section>
        <div className="list">
          {result.questions.map((question, questionIndex) => (
            <section className="card" key={question.key || questionIndex}>
              <div className="eyebrow">Question {questionIndex + 1} · {question.is_correct ? "Correct" : "Incorrect"}</div>
              <h3>{question.stem}</h3>
              <p>Your answer: {question.selected_option_ids.length ? question.selected_option_ids.join(", ") : "Unanswered"}</p>
              <p>Correct answer: {question.correct_option_ids?.join(", ")}</p>
              <p>{question.explanation}</p>
              {question.source_excerpt && <p>Source: “{question.source_excerpt}”</p>}
            </section>
          ))}
        </div>
      </main>
    );
  }

  const question = attempt!.questions[index];
  const questionKey = question.key || question.id || "";
  const answeredCount = Object.values(answers).filter((value) => value.length).length;

  return (
    <main className="shell">
      <header className="top">
        <Link className="brand" href="/">StudyForge</Link>
        <div>
          {attempt!.mode === "exam" && <b>{secondsLeft === null ? "" : `${Math.floor(secondsLeft / 60)}:${String(secondsLeft % 60).padStart(2, "0")}`}</b>}
          　<span>{attempt!.mode} mode</span>
        </div>
      </header>
      <section className="hero">
        <div className="eyebrow">Question {index + 1} of {attempt!.questions.length}</div>
        <h1>{attempt!.mode === "exam" ? "Exam session" : "Practice session"}</h1>
        <p>{answeredCount} answered</p>
        <div className="progress"><div style={{ width: `${((index + 1) / attempt!.questions.length) * 100}%` }} /></div>
      </section>
      <div className="grid">
        <section className="card s8">
          <div className="eyebrow">{question.qtype.replace("_", " ")}</div>
          <h2>{question.stem}</h2>
          <p>Select {question.qtype === "multiple_select" ? "all answers that apply" : "one answer"}.</p>
          <div className="options">
            {question.options.map((option) => (
              <label className={`option ${(answers[questionKey] || []).includes(option.id) ? "selected" : ""}`} key={option.id}>
                <input
                  type={question.qtype === "multiple_select" ? "checkbox" : "radio"}
                  name={questionKey}
                  checked={(answers[questionKey] || []).includes(option.id)}
                  onChange={() => chooseOption(option.id)}
                />
                <span><b>{option.id}.</b> {option.text}</span>
              </label>
            ))}
          </div>
          {attempt!.mode === "practice" && (
            <>
              <button className="btn primary" onClick={checkAnswer}>Check answer</button>
              {feedback[questionKey] && (
                <div className={`feedback ${feedback[questionKey].is_correct ? "good" : "bad"}`}>
                  <b>{feedback[questionKey].is_correct ? "Correct!" : "Not quite."}</b>
                  <p>{feedback[questionKey].explanation}</p>
                  {feedback[questionKey].source_excerpt && <p>Source: “{feedback[questionKey].source_excerpt}”</p>}
                </div>
              )}
            </>
          )}
          <div className="actions">
            <button className="btn" disabled={index === 0} onClick={() => setIndex(index - 1)}>← Previous</button>
            <button className="btn" disabled={index === attempt!.questions.length - 1} onClick={() => setIndex(index + 1)}>Next →</button>
            <button
              className="btn"
              onClick={async () => {
                const flagged = !flags[questionKey];
                setFlags({ ...flags, [questionKey]: flagged });
                try {
                  await saveResponse(questionKey, answers[questionKey] || [], flagged);
                } catch (cause) {
                  setError((cause as Error).message);
                }
              }}
            >
              {flags[questionKey] ? "Unflag" : "Flag for review"}
            </button>
          </div>
          {error && <div className="notice error" role="alert">{error}</div>}
        </section>
        <aside className="card s4">
          <h3>Question navigator</h3>
          <div className="nav">
            {attempt!.questions.map((item, questionIndex) => {
              const key = item.key || item.id || "";
              return (
                <button
                  key={key}
                  className={`${questionIndex === index ? "active " : ""}${answers[key]?.length ? "answered" : ""}`}
                  onClick={() => setIndex(questionIndex)}
                >
                  {questionIndex + 1}{flags[key] ? "⚑" : ""}
                </button>
              );
            })}
          </div>
          <p>{answeredCount} of {attempt!.questions.length} answered</p>
          <button className="btn primary" onClick={() => confirmDialog.current?.showModal()} disabled={busy}>
            {busy ? "Submitting…" : "Submit assessment"}
          </button>
          <p>Exam answers are graded only after submission.</p>
        </aside>
      </div>
      {attempt!.mode === "exam" && (
        <dialog
          ref={confirmDialog}
          className="confirm-dialog"
          aria-labelledby="submit-confirm-title"
          aria-describedby="submit-confirm-description"
        >
          <h2 id="submit-confirm-title">Submit this exam?</h2>
          <p id="submit-confirm-description">
            You have answered {answeredCount} of {attempt!.questions.length} questions. Submitted answers will be graded and results revealed. You can’t change them afterward.
          </p>
          <div className="actions">
            <button className="btn" type="button" onClick={() => confirmDialog.current?.close()}>Keep working</button>
            <button
              className="btn primary"
              type="button"
              onClick={() => {
                confirmDialog.current?.close();
                void submit();
              }}
            >
              Submit exam
            </button>
          </div>
        </dialog>
      )}
    </main>
  );
}
