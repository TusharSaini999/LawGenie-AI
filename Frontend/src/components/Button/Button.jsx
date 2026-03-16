export default function Button({
  children = "Button",
  buttonColor = "bg-primary-400",
  textColor = "text-t-primary",
  isBold = false,
  className = "",
  ...props
}) {
  return (
    <button
      className={`relative inline-flex items-center justify-center overflow-hidden rounded-xl
      px-4 py-2.5 md:px-5 md:py-2.5
      border border-border ${isBold ? "font-semibold" : "font-medium"}
      ${textColor}
      shadow-sm transition-all duration-300 ease-out
      hover:-translate-y-0.5 hover:shadow-md active:translate-y-0 active:scale-[0.99]
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400/70 focus-visible:ring-offset-2 focus-visible:ring-offset-bg
      disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:shadow-sm
      group ${className}`}
      {...props}
    >
      {/* animated background */}
      <span
        className={`absolute inset-0 origin-left scale-x-0 group-hover:scale-x-100
        transform transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]
        group-disabled:scale-x-0
        ${buttonColor}`}
      />

      {/* subtle gloss layer */}
      <span className="pointer-events-none absolute inset-0 bg-gradient-to-b from-white/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      {/* content */}
      <span
        className={`relative z-10 flex items-center justify-center whitespace-nowrap
        transition-colors duration-200
        group-hover:text-white`}
      >
        {children}
      </span>
    </button>
  );
}
