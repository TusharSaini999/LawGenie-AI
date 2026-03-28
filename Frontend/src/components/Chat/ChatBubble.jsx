import { useEffect, useMemo, useRef, useState } from "react";
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

const normalizeTextForSpeech = (value = "") =>
  value
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/[>*#_~]/g, "")
    .replace(/\s+/g, " ")
    .trim();

const NON_LATIN_SCRIPT_PATTERN =
  /[\u0400-\u04FF\u0590-\u05FF\u0600-\u06FF\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F\u0E00-\u0E7F\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]/;

const isEdgeBrowser = () => {
  if (typeof navigator === "undefined") return false;

  return /Edg\//.test(navigator.userAgent || "");
};

const detectSpeechLanguage = (value = "") => {
  if (!value.trim()) return "en-US";

  if (/[\u0900-\u097F]/.test(value)) return "hi-IN";
  if (/[\u0980-\u09FF]/.test(value)) return "bn-IN";
  if (/[\u0A80-\u0AFF]/.test(value)) return "gu-IN";
  if (/[\u0A00-\u0A7F]/.test(value)) return "pa-IN";
  if (/[\u0B80-\u0BFF]/.test(value)) return "ta-IN";
  if (/[\u0C00-\u0C7F]/.test(value)) return "te-IN";
  if (/[\u0C80-\u0CFF]/.test(value)) return "kn-IN";
  if (/[\u0D00-\u0D7F]/.test(value)) return "ml-IN";
  if (/[\u0600-\u06FF]/.test(value)) return "ar-SA";
  if (/[\u0400-\u04FF]/.test(value)) return "ru-RU";
  if (/[\u0590-\u05FF]/.test(value)) return "he-IL";
  if (/[\u0E00-\u0E7F]/.test(value)) return "th-TH";
  if (/[\u3040-\u30FF]/.test(value)) return "ja-JP";
  if (/[\uAC00-\uD7AF]/.test(value)) return "ko-KR";
  if (/[\u4E00-\u9FFF]/.test(value)) return "zh-CN";

  if (typeof navigator !== "undefined" && navigator.language) {
    return navigator.language;
  }

  return "en-US";
};

const findBestVoice = (voices, targetLang, allowGenericFallback = true) => {
  if (!voices?.length) return null;

  const normalizedTarget = targetLang.toLowerCase();
  const targetBase = normalizedTarget.split("-")[0];

  return (
    voices.find((voice) => voice.lang?.toLowerCase() === normalizedTarget) ||
    voices.find((voice) =>
      voice.lang?.toLowerCase().startsWith(`${targetBase}-`),
    ) ||
    voices.find((voice) => voice.lang?.toLowerCase().startsWith(targetBase)) ||
    (allowGenericFallback
      ? voices.find((voice) => voice.default) || voices[0]
      : null)
  );
};

const hasLanguageVoiceSupport = (voices, targetLang) => {
  if (!voices?.length || !targetLang) return false;

  const normalizedTarget = targetLang.toLowerCase();
  const targetBase = normalizedTarget.split("-")[0];

  return voices.some((voice) => {
    const lang = voice.lang?.toLowerCase() || "";
    return (
      lang === normalizedTarget ||
      lang.startsWith(`${targetBase}-`) ||
      lang.startsWith(targetBase)
    );
  });
};

function ChatBubble({ role, text, createdAt }) {
  const isUser = role === "user";
  const speechText = useMemo(() => normalizeTextForSpeech(text || ""), [text]);
  const speechLang = useMemo(() => detectSpeechLanguage(speechText), [speechText]);
  const speechSynthesisApi =
    typeof window !== "undefined" ? window.speechSynthesis : null;
  const utteranceRef = useRef(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState([]);
  const [speechNotice, setSpeechNotice] = useState("");
  const speakTimeoutRef = useRef(null);
  const retryRef = useRef(false);
  const stopRequestedRef = useRef(false);
  const bubbleWidthClass = isUser
    ? "max-w-[92%] sm:max-w-[80%]"
    : "max-w-full";

  const stopSpeech = () => {
    if (!speechSynthesisApi) return;

    stopRequestedRef.current = true;

    if (speakTimeoutRef.current) {
      clearTimeout(speakTimeoutRef.current);
      speakTimeoutRef.current = null;
    }

    speechSynthesisApi.cancel();
    utteranceRef.current = null;
    retryRef.current = false;
    setIsSpeaking(false);
  };

  useEffect(() => {
    if (!speechSynthesisApi) return undefined;

    const loadVoices = () => {
      setVoices(speechSynthesisApi.getVoices());
    };

    let retries = 0;
    const retryInterval = setInterval(() => {
      const loadedVoices = speechSynthesisApi.getVoices();
      if (loadedVoices.length > 0 || retries >= 8) {
        setVoices(loadedVoices);
        clearInterval(retryInterval);
        return;
      }
      retries += 1;
    }, 250);

    loadVoices();
    if (typeof speechSynthesisApi.addEventListener === "function") {
      speechSynthesisApi.addEventListener("voiceschanged", loadVoices);
    } else {
      speechSynthesisApi.onvoiceschanged = loadVoices;
    }

    return () => {
      if (typeof speechSynthesisApi.removeEventListener === "function") {
        speechSynthesisApi.removeEventListener("voiceschanged", loadVoices);
      } else {
        speechSynthesisApi.onvoiceschanged = null;
      }
      clearInterval(retryInterval);
    };
  }, [speechSynthesisApi]);

  const speakWithUtterance = (utterance) => {
    if (!speechSynthesisApi) return;

    if (speakTimeoutRef.current) {
      clearTimeout(speakTimeoutRef.current);
      speakTimeoutRef.current = null;
    }

    // Edge is sensitive to speak() immediately after cancel(), so add a tiny delay.
    speakTimeoutRef.current = setTimeout(
      () => {
        if (stopRequestedRef.current) {
          speakTimeoutRef.current = null;
          return;
        }
        speechSynthesisApi.speak(utterance);
        speakTimeoutRef.current = null;
      },
      isEdgeBrowser() ? 120 : 0,
    );
  };

  const handleSpeak = () => {
    if (!speechSynthesisApi || !speechText) return;

    setSpeechNotice("");

    if (isSpeaking) {
      stopSpeech();
      return;
    }

    stopRequestedRef.current = false;
    speechSynthesisApi.cancel();
    const availableVoices = voices.length ? voices : speechSynthesisApi.getVoices();
    if (!hasLanguageVoiceSupport(availableVoices, speechLang)) {
      stopSpeech();
      setSpeechNotice("Language Speeck is not Supported");
      return;
    }

    const utterance = new SpeechSynthesisUtterance(speechText);
    const hasNonLatinScript = NON_LATIN_SCRIPT_PATTERN.test(speechText);
    const voice = findBestVoice(
      availableVoices,
      speechLang,
      !hasNonLatinScript,
    );

    utterance.lang = speechLang;
    if (voice) {
      utterance.voice = voice;
      utterance.lang = voice.lang || speechLang;
    }

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.onend = () => {
      if (stopRequestedRef.current) {
        stopRequestedRef.current = false;
      }
      setIsSpeaking(false);
      utteranceRef.current = null;
      retryRef.current = false;
    };
    utterance.onerror = () => {
      if (stopRequestedRef.current) {
        stopRequestedRef.current = false;
        setIsSpeaking(false);
        utteranceRef.current = null;
        retryRef.current = false;
        return;
      }

      setIsSpeaking(false);
      utteranceRef.current = null;
      retryRef.current = false;
      setSpeechNotice("Language Speeck is not Supported");
    };

    retryRef.current = false;
    utteranceRef.current = utterance;
    setIsSpeaking(true);
    speakWithUtterance(utterance);
  };

  useEffect(() => {
    return () => {
      if (speakTimeoutRef.current) {
        clearTimeout(speakTimeoutRef.current);
        speakTimeoutRef.current = null;
      }
      if (utteranceRef.current && speechSynthesisApi?.speaking) {
        speechSynthesisApi.cancel();
      }
    };
  }, [speechSynthesisApi]);

  useEffect(() => {
    if (isSpeaking) {
      stopSpeech();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text]);

  useEffect(() => {
    if (!speechNotice) return undefined;

    const timeoutId = setTimeout(() => {
      setSpeechNotice("");
    }, 3000);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [speechNotice]);

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

          <button
            type="button"
            onClick={handleSpeak}
            disabled={!speechText}
            className="ml-1 rounded-md border border-border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-t-muted transition hover:text-t-primary disabled:cursor-not-allowed disabled:opacity-50"
            aria-label={isSpeaking ? "Stop reading message" : "Read message aloud"}
            title={isSpeaking ? "Stop" : "Read aloud"}
          >
            {isSpeaking ? "Stop" : "Speak"}
          </button>

          {speechNotice ? (
            <span className="text-[10px] font-semibold text-red-500">
              {speechNotice}
            </span>
          ) : null}
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
