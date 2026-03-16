const TRIM_RULE = {
  setValueAs: (value) => (typeof value === "string" ? value.trim() : value),
};

export const MESSAGE_RULES = {
  ...TRIM_RULE,
  required: "Message is required",
  minLength: {
    value: 6,
    message: "Message must be at least 2 characters.",
  },
  maxLength: {
    value: 128,
    message: "Message is too long.",
  },
  validate: {
    // Prevent whitespace-only messages
    notEmpty: (value) => value.trim().length > 0 || "Message cannot be empty.",
  },
};
