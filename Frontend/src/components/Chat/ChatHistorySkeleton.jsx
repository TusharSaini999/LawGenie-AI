function SkeletonRow({ align = "left", width = "w-1/2" }) {
  const rowAlignClass = align === "right" ? "justify-end" : "justify-start";

  return (
    <div className={`w-full flex ${rowAlignClass}`}>
      <div className={`h-12 rounded-2xl bg-surface border border-border animate-pulse ${width}`} />
    </div>
  );
}

function ChatHistorySkeleton() {
  return (
    <div className="w-full space-y-5" aria-label="Loading chat history" aria-busy="true">
      <SkeletonRow align="left" width="w-2/3" />
      <SkeletonRow align="right" width="w-1/2" />
      <SkeletonRow align="left" width="w-5/6" />
      <SkeletonRow align="right" width="w-2/5" />
    </div>
  );
}

export default ChatHistorySkeleton;
