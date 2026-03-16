import { ArrowRightIcon } from "@heroicons/react/24/outline";
import { useNavigate, useLocation } from "react-router";
import Button from "../Button/Button";

export default function UnauthNavbar() {
  const navigate = useNavigate();
  const location = useLocation();

  if (location.pathname === "/chat") {
    return null; // Don't render on the chat page
  }

  return (
    <Button
      onClick={() => {
        navigate("/chat");
      }}
      className="text-sm sm:text-base"
      isBold
    >
      Try It
      <ArrowRightIcon className="ml-2 w-4 h-4 sm:w-5 sm:h-5 my-auto" />
    </Button>
  );
}
