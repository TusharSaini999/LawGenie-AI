import { useRef, useState, useEffect, useCallback } from "react";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";

const MAX_MESSAGE_LENGTH = 2000;

function InputChatBox({
  onSend,
  onNewChat,
  loading = false,
  disabled = false,
  errorMessage = "",
  resetKey = 0,
}) {
  const textareaRef = useRef(null);

  const [message, setMessage] = useState("");

  const canSend = !loading && !disabled && message.trim().length > 0;
  const isLocked = loading || disabled;

  const resizeTextarea = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;

    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, []);

  useEffect(() => {
    resizeTextarea();
  }, [message, resizeTextarea]);

  useEffect(() => {
    setMessage("");

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [resetKey]);

  const onSubmit = async () => {
    if (!canSend || isLocked) return;

    const text = message.trim();
    // Clear input immediately so sent text only appears in the chat stream.
    setMessage("");

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    try {
      await onSend?.({
        message: text,
      });

      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    } catch {
      setMessage(text);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      if (canSend) onSubmit();
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <div className="w-full border-t border-border bg-bg px-4 py-4 sm:px-6">
      <form onSubmit={handleFormSubmit} className="w-full max-w-5xl mx-auto space-y-2">
        <div className="rounded-3xl border border-border bg-surface p-2 shadow-sm focus-within:border-primary/40">
          <div className="rounded-2xl bg-surface">
            <textarea
              maxLength={MAX_MESSAGE_LENGTH}
              rows={1}
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={isLocked}
              enterKeyHint="send"
              onKeyDown={handleKeyDown}
              placeholder="Ask LawGenie about Indian law, procedures, rights, or contracts..."
              className="w-full resize-none px-4 py-3.5 outline-none text-sm sm:text-[15px] bg-transparent text-t-primary placeholder:text-t-muted"
            />
          </div>

          <div className="flex items-center justify-between gap-3 px-1 pt-2 pb-1">
            <div className="flex items-center gap-2 px-2">
              <button
                type="button"
                onClick={onNewChat}
                disabled={isLocked}
                className="rounded-lg border border-border px-2.5 py-1 text-[11px] sm:text-xs text-t-secondary hover:text-t-primary hover:bg-bg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                New chat
              </button>
              <p className="text-[11px] sm:text-xs text-t-muted">
                {loading ? "Processing your question..." : "Shift + Enter for new line"}
              </p>
            </div>

            <div className="flex items-center gap-3 pr-1">
              <span
                className={`text-xs ${
                  message.length > 1800 ? "text-error" : "text-t-secondary"
                }`}
              >
                {message.length}/{MAX_MESSAGE_LENGTH}
              </span>

              <button
                type="submit"
                disabled={!canSend}
                className={`flex items-center justify-center w-10 h-10 rounded-2xl transition ${
                  canSend ? "hover:scale-105" : "opacity-40"
                } bg-primary text-white`}
                aria-label="Send message"
              >
                {loading ? (
                  <span className="h-4 w-4 rounded-full border-2 border-white/70 border-t-transparent animate-spin" />
                ) : (
                  <PaperAirplaneIcon className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-[11px] text-t-disabled px-2">
          LawGenie can make mistakes. Verify legal advice with official sources.
        </p>

        {errorMessage && <div className="text-xs mt-2 text-error">{errorMessage}</div>}
      </form>
    </div>
  );
}

export default InputChatBox;
