import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router";
import Team from "./components/Team/TeamSection";
import {
  ArrowRightIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon,
  BoltIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  PaperAirplaneIcon,
  PencilSquareIcon,
  CodeBracketIcon,
  AcademicCapIcon,
  LightBulbIcon,
  DocumentTextIcon,
  LanguageIcon,
} from "@heroicons/react/24/outline";

import * as THREE from "three";
import NET from "vanta/dist/vanta.net.min";

export function VantaBackground({ children = null }) {
  const ref = useRef(null);
  const [vantaEffect, setVantaEffect] = useState(null);

  useEffect(() => {
    if (!vantaEffect) {
      const initNet = typeof NET === "function" ? NET : NET?.default;
      if (typeof initNet !== "function") return;

      setVantaEffect(
        initNet({
          el: ref.current,
          THREE: THREE,
          mouseControls: true,
          touchControls: true,
          minHeight: 600.0,
          minWidth: 800.0,
          scale: 1.0,
          scaleMobile: 1.0,
          color: 0x4f46e5,
          backgroundAlpha: 0.0,
          points: 4,
          maxDistance: 40,
          spacing: 50,
          showDots: true,
          showLines: true,
        }),
      );
    }
    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);

  return (
    <div ref={ref} className="absolute inset-0 z-0">
      {children}
    </div>
  );
}

function HomeButtonComp({
  children,
  href = undefined,
  onClick = undefined,
  variant = "primary",
  className = "",
}) {
  const baseStyle =
    "flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold shadow-md transition-transform hover:-translate-y-1 hover:shadow-lg";
  const primaryStyle = "bg-primary text-white hover:scale-105";
  const secondaryStyle =
    "border border-gray-300 dark:border-white/20 hover:bg-gray-100 dark:hover:bg-white/10 text-t-primary";
  const style =
    variant === "primary"
      ? `${baseStyle} ${primaryStyle} ${className}`
      : `${baseStyle} ${secondaryStyle} ${className}`;

  return href ? (
    <a href={href} className={style}>
      {children}
    </a>
  ) : (
    <button onClick={onClick} className={style}>
      {children}
    </button>
  );
}

function BackgroundDecor() {
  return (
    <>
      <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-primary-200/20 dark:bg-primary-700/30 blur-3xl animate-blob z-0" />
      <div className="absolute top-1/3 right-[-20%] w-72 h-72 rounded-full bg-accent-200/20 dark:bg-accent-700/30 blur-3xl animate-blob z-0" />
      <div className="absolute bottom-[-10%] left-1/4 w-80 h-80 rounded-full bg-primary-300/10 dark:bg-primary-600/20 blur-3xl animate-blob z-0" />
      <div className="absolute bottom-[-20%] right-0 w-64 h-64 rounded-full bg-accent-300/10 dark:bg-accent-600/20 blur-3xl animate-blob z-0" />
    </>
  );
}

function HeroSection() {
  return (
    <section
      className="relative flex items-center justify-center px-6 md:px-12 overflow-hidden min-h-screen bg-linear-to-br from-gray-50 via-gray-100 to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
      id="home"
    >
      <VantaBackground />
      <div className="relative z-10 max-w-4xl text-center space-y-6">
        <span className="inline-flex items-center px-4 py-1 mb-4 text-sm font-medium rounded-full border border-gray-300 dark:border-white/20 backdrop-blur text-gray-900 dark:text-gray-200">
          ⚖️ AI Legal Assistant
        </span>
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold leading-tight text-gray-900 dark:text-white">
          Smarter Legal Research{" "}
          <span className="block bg-linear-to-r from-primary to-accent bg-clip-text text-transparent">
            Powered by AI
          </span>
        </h1>
        <p className="mt-4 text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          LawGenie is an AI-powered legal assistant that simplifies access to
          Indian laws and legal knowledge. Ask questions, analyze legal
          documents, and get instant, cited answers using AI.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
          <HomeButtonComp href="/chat" variant="primary">
            Start Chat
          </HomeButtonComp>
        </div>
      </div>
    </section>
  );
}

function FeaturesSection() {
  const features = useMemo(
    () => [
      {
        icon: SparklesIcon,
        title: "AI-Powered Legal Chat",
        desc: "Ask questions about Indian laws (IPC, RTI, labour laws, and more) and get instant, accurate, cited answers powered by AI.",
      },
      {
        icon: ChatBubbleLeftRightIcon,
        title: "Semantic Search (RAG)",
        desc: "FAISS vector database retrieves the most relevant legal document chunks before generating AI responses.",
      },
      {
        icon: BoltIcon,
        title: "Multi-Language Support",
        desc: "Our assistant responds in the language you request, making legal knowledge accessible to everyone.",
      },
      {
        icon: ShieldCheckIcon,
        title: "Secure & Private",
        desc: "Redis-backed chat history and JWT authentication protect your data and preserve session history for 24 hours.",
      },
    ],
    [],
  );

  return (
    <section
      className="bg-bg py-20 md:py-28 relative overflow-hidden"
      id="features"
    >
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-semibold text-t-primary">
            Powerful Features for Modern AI
          </h2>
          <p className="mt-4 text-t-secondary max-w-2xl mx-auto">
            LawGenie combines AI, RAG, and multi-language support to make Indian
            legal knowledge accessible instantly.
          </p>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(({ icon: Icon, title, desc }, idx) => (
            <div
              key={idx}
              className="group relative p-6 rounded-2xl border border-border bg-surface shadow-sm hover:-translate-y-1 hover:shadow-lg transition-transform"
            >
              <div className="flex items-center justify-center w-12 h-12 mb-4 rounded-xl bg-primary-100 text-primary-600">
                <Icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-t-primary">{title}</h3>
              <p className="mt-2 text-sm text-t-secondary">{desc}</p>
              <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity bg-linear-to-br from-primary-400/5 to-accent-400/5" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  const navigate = useNavigate();

  return (
    <section
      className="relative py-24 md:py-32 overflow-hidden bg-elevated"
      id="cta"
    >
      <VantaBackground />
      <BackgroundDecor />
      <div className="max-w-6xl mx-auto px-6 relative z-10">
        <div className="relative rounded-3xl overflow-hidden shadow-2xl bg-linear-to-br from-primary-500 to-accent-500 p-10 md:p-16">
          <div className="absolute inset-0 bg-white/10 backdrop-blur-lg pointer-events-none rounded-3xl" />
          <div className="relative z-10 text-center max-w-3xl mx-auto space-y-6">
            <h2 className="text-3xl md:text-5xl font-extrabold leading-tight text-white">
              Start Using LawGenie Today
            </h2>
            <p className="text-white/80 text-lg md:text-xl">
              Access Indian legal knowledge instantly. Search laws and get
              AI-powered answers in real time.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row justify-center gap-5">
              <HomeButtonComp
                variant="primary"
                className="text-lg md:text-base"
                onClick={() => {
                  navigate("/chat");
                }}
              >
                Get Started <ArrowRightIcon className="w-5 h-5" />
              </HomeButtonComp>
            </div>
          </div>
          <div className="absolute -top-32 -left-32 w-72 h-72 rounded-full bg-primary-200/20 blur-3xl animate-blob" />
          <div className="absolute -bottom-32 -right-32 w-72 h-72 rounded-full bg-accent-200/20 blur-3xl animate-blob" />
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = useMemo(
    () => [
      {
        icon: ChatBubbleLeftRightIcon,
        title: "Ask Legal Questions",
        desc: "Type your legal query about Indian laws or regulations.",
        extra:
          "LawGenie interprets your question accurately and finds relevant legal references.",
      },
      {
        icon: CpuChipIcon,
        title: "AI Context Understanding",
        desc: "Our AI analyzes your question and searches the relevant legal corpus.",
        extra:
          "Combines Google Gemini AI with FAISS-based RAG retrieval to give precise answers.",
      },
      {
        icon: SparklesIcon,
        title: "Smart Document Analysis",
        desc: "Upload PDFs, DOC, DOCX, TXT, or CSV files to query your legal documents.",
        extra:
          "Only new documents are vectorized; existing indices are preserved for faster results.",
      },
      {
        icon: PaperAirplaneIcon,
        title: "Instant, Cited Results",
        desc: "Receive clear and actionable answers immediately.",
        extra:
          "Responses include citations to laws or uploaded documents, ensuring trustworthiness.",
      },
    ],
    [],
  );

  return (
    <section className="bg-elevated py-24 md:py-32" id="how-it-works">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-3xl md:text-4xl font-semibold text-t-primary">
            How LawGenie Works
          </h2>
          <p className="mt-4 text-t-secondary max-w-2xl mx-auto">
            AI-powered legal research simplified with RAG, multi-language
            support, and instant answers.
          </p>
        </div>
        <div className="relative space-y-20">
          <div className="absolute left-1/2 top-0 h-full w-px -translate-x-1/2 bg-border hidden md:block" />
          {steps.map(({ icon: Icon, title, desc, extra }, idx) => {
            const isLeft = idx % 2 === 0;
            return (
              <div
                key={idx}
                className="relative grid md:grid-cols-2 gap-12 items-center"
              >
                <div className={`${isLeft ? "md:text-right" : "md:order-2"}`}>
                  <div className="p-6 bg-surface border border-border rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                    <div
                      className={`flex items-center gap-3 mb-4 ${
                        isLeft ? "justify-end" : "justify-start"
                      }`}
                    >
                      <span className="flex w-10 h-10 items-center justify-center rounded-xl bg-primary-100 text-primary-600">
                        <Icon className="w-5 h-5" />
                      </span>
                      <span className="text-sm font-medium text-primary-500">
                        Step {idx + 1}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-t-primary">
                      {title}
                    </h3>
                    <p className="mt-2 text-sm text-t-secondary">{desc}</p>
                    <p className="mt-1 text-sm text-t-muted">{extra}</p>
                  </div>
                </div>
                <div className="absolute left-1/2 top-6 -translate-x-1/2 w-4 h-4 rounded-full bg-primary-500 ring-4 ring-bg hidden md:flex" />
                <div className={`${isLeft ? "md:order-2" : ""}`} />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function UseCasesSection() {
  const useCases = useMemo(
    () => [
      {
        icon: PencilSquareIcon,
        title: "Legal Document Query",
        desc: "Upload and search PDFs, DOC, DOCX, TXT, or CSV files for instant answers.",
      },
      {
        icon: CodeBracketIcon,
        title: "Law & Regulation Lookup",
        desc: "Get AI-powered insights and citations for IPC, RTI, labour laws, and more.",
      },
      {
        icon: AcademicCapIcon,
        title: "Research Made Easy",
        desc: "Analyze legal documents, case studies, and legal precedents efficiently.",
      },
      {
        icon: LightBulbIcon,
        title: "Instant Insights",
        desc: "Discover actionable insights and interpretations from complex legal text.",
      },
      {
        icon: DocumentTextIcon,
        title: "Multi-Language Answers",
        desc: "Receive responses in the language you prefer for better accessibility.",
      },
      {
        icon: LanguageIcon,
        title: "Incremental Training",
        desc: "Only newly added documents are vectorized, preserving existing knowledge base.",
      },
    ],
    [],
  );

  return (
    <section className="bg-bg py-24 md:py-32" id="use-cases">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-3xl md:text-4xl font-semibold text-t-primary">
            What You Can Do With LawGenie
          </h2>
          <p className="mt-4 text-t-secondary max-w-2xl mx-auto">
            Access laws, query documents, and get AI-powered legal insights
            instantly.
          </p>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {useCases.map(({ icon: Icon, title, desc }, idx) => (
            <div
              key={idx}
              className="group p-6 border border-border bg-surface rounded-2xl shadow-sm hover:-translate-y-1 hover:shadow-lg transition-transform relative"
            >
              <div className="flex w-12 h-12 items-center justify-center mb-4 rounded-xl bg-primary-100 text-primary-600">
                <Icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-t-primary">{title}</h3>
              <p className="mt-2 text-sm text-t-secondary">{desc}</p>
              <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity bg-linear-to-br from-primary-400/5 to-accent-400/5" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function App() {
  const location = useLocation();
  useEffect(() => {
    if (!location.hash) return;
    const el = document.querySelector(location.hash);
    el?.scrollIntoView({ behavior: "smooth" });
  }, [location]);

  return (
    <div className="flex flex-col relative overflow-hidden">
      <HeroSection />
      <FeaturesSection />
      <HowItWorks />
      <UseCasesSection />
      <Team />
      <CTASection />
    </div>
  );
}

export default App;
