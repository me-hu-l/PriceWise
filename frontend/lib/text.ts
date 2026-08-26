/** Splits a period-delimited explanation string into individual sentences for bulleted display. */
export function splitSentences(text: string): string[] {
  return text
    .split(/(?<=\.)\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}
