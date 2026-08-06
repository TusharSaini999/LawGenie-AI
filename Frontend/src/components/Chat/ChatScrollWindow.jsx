import ChatBubble from "@/components/Chat/ChatBubble";
import ChatHistorySkeleton from "@/components/Chat/ChatHistorySkeleton";
import TypingIndicator from "@/components/Chat/TypingIndicator";

function ChatScrollWindow({ messages, isTyping, isHistoryLoading = false }) {
  return (
    <div className="relative flex-1 px-4 py-5 sm:px-6 sm:py-6 overflow-y-auto">
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
