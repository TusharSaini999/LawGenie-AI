import { useEffect, useLayoutEffect, useRef, useState } from "react";
import InputChatBox from "@/components/Chat/InputChatBox";
import ChatScrollWindow from "../components/Chat/ChatScrollWindow";
import chatService from "@/services/chatService";
import Header from "@/components/Header/Header";

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
      className="relative h-screen min-h-0 text-t-primary bg-bg overflow-hidden flex flex-col"
    >
      {/* Background Pattern and Animations */}
      <div className="absolute inset-0 chat-scroll opacity-40 pointer-events-none" aria-hidden="true" />
      <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-primary-200/30 dark:bg-primary-700/20 blur-3xl animate-blob z-0 pointer-events-none" />
      <div className="absolute top-1/3 right-[-10%] w-72 h-72 rounded-full bg-accent-200/30 dark:bg-accent-700/20 blur-3xl animate-blob animation-delay-2000 z-0 pointer-events-none" />
      <div className="absolute -bottom-32 left-1/4 w-80 h-80 rounded-full bg-primary-200/20 dark:bg-primary-700/10 blur-3xl animate-blob animation-delay-4000 z-0 pointer-events-none" />

      {/* Global Navbar */}
      <Header />

      <section className="relative z-10 mx-auto h-full w-full max-w-4xl flex flex-col pt-[57px] sm:pt-[65px]">
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
