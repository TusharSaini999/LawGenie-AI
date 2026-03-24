import { useEffect, useLayoutEffect, useRef, useState } from "react";
import InputChatBox from "@/components/Chat/InputChatBox";
import ChatScrollWindow from "../components/Chat/ChatScrollWindow";
import chatService from "@/services/chatService";

const createMessage = (payload) => ({
  id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
  role: payload?.role,
  text: payload?.text,
  createdAt: payload?.createdAt || new Date(),
});

const initialMessages = [
  createMessage({
    role: "assistant",
    text: "Hello! I am LawGenie. Ask me about Indian laws, legal procedures, rights, contracts, or legal research.",
  }),
];

function ChatPage() {
  const [messages, setMessages] = useState(initialMessages);
  const [isTyping, setIsTyping] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [chatError, setChatError] = useState("");
  const [chatResetKey, setChatResetKey] = useState(0);
  const pageRef = useRef(null);
  const pageBottomRef = useRef(null);

  const scrollToBottom = (behavior = "auto") => {
    const scrollBehavior = behavior === "smooth" ? "smooth" : "auto";
    const page = pageRef.current;
    const pageBottom = pageBottomRef.current;

    if (page) {
      page.scrollTo({
        top: page.scrollHeight,
        behavior: scrollBehavior,
      });
    }

    if (pageBottom) {
      pageBottom.scrollIntoView({ block: "end", behavior: scrollBehavior });
    }
  };

  useLayoutEffect(() => {
    if (isHistoryLoading) return;

    const id = requestAnimationFrame(() => {
      scrollToBottom("auto");
    });

    return () => cancelAnimationFrame(id);
  }, [messages, isTyping, isHistoryLoading]);

  useEffect(() => {
    let isMounted = true;

    const loadHistory = async () => {
      setIsHistoryLoading(true);
      setChatError("");

      try {
        const { hasHistory, history } = await chatService.getHistory();

        if (!isMounted) return;

        if (hasHistory) {
          setMessages(
            history.map((item) =>
              createMessage({
                role: item.role,
                text: item.text,
                createdAt: item.createdAt,
              }),
            ),
          );
        } else {
          setMessages(initialMessages);
        }
      } catch (error) {
        if (!isMounted) return;

        setMessages(initialMessages);
        setChatError(error?.message || "Unable to load chat history.");
      } finally {
        if (isMounted) {
          setIsHistoryLoading(false);
        }
      }
    };

    loadHistory();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSend = async ({ message }) => {
    if (isTyping || isHistoryLoading) return;

    setChatError("");

    const userMessage = createMessage({ role: "user", text: message });

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    scrollToBottom();

    try {
      const { reply } = await chatService.sendMessage({ message });

      setMessages((prev) => [
        ...prev,
        createMessage({ role: "assistant", text: reply }),
      ]);
      scrollToBottom();
    } catch (error) {
      const messageText = error?.message || "Unable to fetch response.";
      setChatError(messageText);
      throw error;
    } finally {
      setIsTyping(false);
      scrollToBottom();
    }
  };

  const handleNewChat = () => {
    if (isTyping || isHistoryLoading) return;

    chatService.startNewChat();
    setChatError("");
    setMessages(initialMessages);
    setChatResetKey((prev) => prev + 1);
    scrollToBottom("auto");
  };

  return (
    <div
      ref={pageRef}
      className="relative h-full min-h-0 text-t-primary bg-bg"
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-35"
        aria-hidden="true"
        style={{
          backgroundImage:
            "linear-gradient(to right, color-mix(in oklab, var(--color-border) 45%, transparent) 1px, transparent 1px), linear-gradient(to bottom, color-mix(in oklab, var(--color-border) 45%, transparent) 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
      />

      <section className="relative z-10 mx-auto min-h-full w-full max-w-7xl flex flex-col">
        <ChatScrollWindow
          messages={messages}
          isTyping={isTyping}
          isHistoryLoading={isHistoryLoading}
        />

        <InputChatBox
          onSend={handleSend}
          loading={isTyping}
          disabled={isHistoryLoading}
          onNewChat={handleNewChat}
          errorMessage={chatError}
          resetKey={chatResetKey}
        />
      </section>

      <div ref={pageBottomRef} className="h-px" aria-hidden="true" />
    </div>
  );
}

export default ChatPage;
