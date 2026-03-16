function HoverButton({ children, className = "", ...props }) {
  return (
    <button
      aria-haspopup="true"
      className={`p-1.5 sm:p-2 rounded-lg hover:bg-elevated transition ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export default HoverButton;
