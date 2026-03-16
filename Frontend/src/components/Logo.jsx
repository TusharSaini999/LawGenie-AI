import { ArrowPathRoundedSquareIcon } from "@heroicons/react/16/solid";

function Logo({ className = "", ...props }) {
  return (
    <ArrowPathRoundedSquareIcon className={`size-5 ${className}`} {...props} />
  );
}

export default Logo;
