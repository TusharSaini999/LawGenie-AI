import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const formatTime = (time) => {
  if (!time) return "";

  const date = time instanceof Date ? time : new Date(time);

  return new Intl.DateTimeFormat("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

function ChatBubble({ role, text, createdAt }) {
  const isUser = role === "user";
  const bubbleWidthClass = isUser
    ? "max-w-[92%] sm:max-w-[80%]"
    : "max-w-full";

  return (
    <article
      className={`w-full flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`${bubbleWidthClass} ${isUser ? "items-end" : "items-start"} flex flex-col gap-2`}
      >
        <div className="flex items-center gap-2 px-1">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-t-muted">
            {isUser ? "You" : "LawGenie"}
          </span>

          <span className="text-[11px] text-t-disabled">
            {formatTime(createdAt)}
          </span>
        </div>

        <div
          className={`rounded-2xl px-4 py-3 text-[15px] leading-relaxed whitespace-pre-wrap wrap-anywhere border ${
            isUser
              ? "bg-surface-elevated text-t-primary border-border"
              : "bg-transparent text-bot-text border-transparent"
          }`}
        >
          {isUser ? (
            text
          ) : (
            <div className="chat-markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {text || ""}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}

export default ChatBubble;
