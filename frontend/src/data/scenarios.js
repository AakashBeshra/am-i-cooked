export const EXAMPLE_SCENARIOS = [
  "My exam is tomorrow and I haven't studied.",
  "I accidentally texted my boss what I meant for my girlfriend.",
  "I have ₹500 left and payday is 20 days away.",
  "My interview starts in 2 hours and I just learned Python.",
  "I haven't started my final year project and it's due Friday.",
  "I told three different people I'm free tonight.",
  "My phone has 2% battery and my charger disappeared.",
];

export const CHAOS_SCENARIOS = [
  "You have an interview in 30 minutes and your laptop decided to update Windows.",
  "You told three different people you were free tonight.",
  "Your professor asks you to explain the code you copied yesterday.",
  "Your phone has 2% battery and your charger disappeared.",
  "You sent a screenshot of a chat to the person the chat was about.",
  "You skipped one class and the syllabus doubled.",
  "You 'replied later' to a message from 3 weeks ago.",
  "You just realized the deadline was yesterday.",
  "You said 'I'll remember' and immediately forgot.",
  "Your alarm didn't go off and the exam started 20 minutes ago.",
  "You told your mom you'd study and opened YouTube instead.",
  "You approved a pull request without reading it.",
];

export function pickChaosScenario() {
  return CHAOS_SCENARIOS[Math.floor(Math.random() * CHAOS_SCENARIOS.length)];
}