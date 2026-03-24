import ChatBubble from "@/components/Chat/ChatBubble";
import ChatHistorySkeleton from "@/components/Chat/ChatHistorySkeleton";
import TypingIndicator from "@/components/Chat/TypingIndicator";

function ChatScrollWindow({ messages, isTyping, isHistoryLoading = false }) {
  return (
    <div className="relative flex-1 px-4 py-5 sm:px-6 sm:py-6 bg-bg overflow-y-auto">
      <div
        className="pointer-events-none absolute inset-0 opacity-35"
        aria-hidden="true"
        style={{
          backgroundImage:
            "linear-gradient(to right, color-mix(in oklab, var(--color-border) 45%, transparent) 1px, transparent 1px), linear-gradient(to bottom, color-mix(in oklab, var(--color-border) 45%, transparent) 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
      />

      <div
        className="relative mx-auto w-full max-w-full space-y-6"
        aria-live="polite"
        role="log"
        aria-relevant="additions text"
      >
        {isHistoryLoading ? (
          <ChatHistorySkeleton />
        ) : (
          messages.map((message) => (
            <ChatBubble
              key={message.id}
              role={message.role}
              text={message.text}
              createdAt={message.createdAt}
            />
          ))
        )}

        {!isHistoryLoading && isTyping && <TypingIndicator />}
      </div>
    </div>
  );
}

export default ChatScrollWindow;
