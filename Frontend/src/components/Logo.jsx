function Logo({ className = "", ...props }) {
  return (
    <img
      src="/favicon.svg"
      alt="LawGenie logo"
      className={`size-5 ${className}`}
      {...props}
    />
  );
}

export default Logo;
