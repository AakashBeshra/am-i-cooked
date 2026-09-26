export const TEXT_EGGS = [
  {
    match: ["i'm fine", "im fine", "i am fine"],
    response: "That's exactly what someone who is cooked would say.",
  },
  {
    match: ["it's fine", "its fine"],
    response: "Famous last words.",
  },
  {
    match: ["i have time", "i still have time"],
    response: "You have time. Time has also filed a complaint.",
  },
  {
    match: ["i'll do it tomorrow", "ill do it tomorrow"],
    response: "The oven will still be preheated tomorrow.",
  },
  {
    match: ["i work better under pressure"],
    response: "The pressure is filing a formal grievance.",
  },
  {
    match: ["one more episode"],
    response: "One more episode. One more hour. One more deadline missed.",
  },
  {
    match: ["i'll sleep later", "ill sleep later"],
    response: "Sleep is not a subscription you can pause.",
  },
  {
    match: ["it's not that bad", "its not that bad"],
    response: "That's the exact sentence every burnt toast says.",
  },
];

export function detectTextEgg(input) {
  if (!input) return null;
  const lower = input.toLowerCase();
  for (const egg of TEXT_EGGS) {
    if (egg.match.some((m) => lower.includes(m))) return egg.response;
  }
  return null;
}