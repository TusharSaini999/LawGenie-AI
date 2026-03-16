import { useState, useRef, useEffect } from "react";
import {
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  Bars3Icon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { NavLink, useLocation, useNavigate } from "react-router";
import Logo from "../Logo";
import HoverButton from "../Button/HoverButton";
import UnauthNavbar from "./UnAuthNavbar";
import useTheme from "@/hooks/useTheme";

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isThemeMenuOpen, setIsThemeMenuOpen] = useState(false);

  const mobileMenuRef = useRef(null);
  const mobileButtonRef = useRef(null);
  const themeMenuRef = useRef(null);

  const navigate = useNavigate();
  const location = useLocation();

  const { theme, systemTheme, setTheme } = useTheme();
  const currentTheme = theme === "system" ? systemTheme : theme;
  const ThemeIcon = currentTheme === "dark" ? MoonIcon : SunIcon;

  const themeItems = [
    { name: "Light", value: "light", icon: SunIcon },
    { name: "Dark", value: "dark", icon: MoonIcon },
    { name: "System", value: "system", icon: ComputerDesktopIcon },
  ];

  const homeSections = [
    { name: "Home", id: "home" },
    { name: "Features", id: "features" },
    { name: "How It Works", id: "how-it-works" },
    { name: "Use Cases", id: "use-cases" },
  ];

  const navItems =
    location.pathname === "/"
      ? homeSections.map((section) => ({
          name: section.name,
          link: `#${section.id}`,
          isActive: location.hash === `#${section.id}`,
        }))
      : null;

  const toggleThemeMenu = () => {
    setIsThemeMenuOpen((value) => !value);
    setIsMobileMenuOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (themeMenuRef.current && !themeMenuRef.current.contains(e.target)) {
        setIsThemeMenuOpen(false);
      }
      if (
        mobileMenuRef.current &&
        !mobileMenuRef.current.contains(e.target) &&
        mobileButtonRef.current &&
        !mobileButtonRef.current.contains(e.target)
      ) {
        setIsMobileMenuOpen(false);
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        setIsThemeMenuOpen(false);
        setIsMobileMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <nav className="bg-surface/60 border-b border-border fixed top-0 left-0 right-0 text-t-primary backdrop-filter backdrop-blur-lg  border-b border-white/20">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-8">
        {/*
          ⚠️ If you change h-14 / sm:h-16 below, 
          remember to update scroll-padding-top in html{} in index.css accordingly.
          + also Edit the Layout.jsx 
        */}
        <div className="flex h-14 sm:h-16 items-center justify-between">
          {/* Left – shared */}
          <div className="flex flex-1 items-center gap-4">
            <button
              onClick={() => {
                if (location.pathname == "/") {
                  // On MainScreen the user will press on this to go to top.
                  window?.scrollTo({ top: 0 });

                  // Remove the hash from URL
                  window?.history?.replaceState(
                    null,
                    "",
                    window.location.pathname + window.location.search,
                  );
                } else {
                  navigate("/");
                }
              }}
              className="flex items-center gap-2 text-base sm:text-lg font-medium cursor-pointer"
            >
              <Logo className="w-5 h-5 sm:w-6 sm:h-6" />
              <span className="font-medium">
                <span className="font-bold text-primary-500">L</span>aw
                <span className="font-bold text-primary-500">G</span>enie
              </span>
            </button>

            {/* Desktop nav */}
            {navItems && (
              <div className="hidden md:flex flex-1 justify-center items-center gap-6 lg:gap-8">
                {navItems.map((item) => (
                  <NavLink
                    replace
                    to={item.link}
                    key={item.name}
                    className={`text-sm lg:text-base font-medium transition-colors ${
                      item.isActive
                        ? "text-primary"
                        : "text-t-muted hover:text-primary"
                    }`}
                  >
                    {item.name}
                  </NavLink>
                ))}
              </div>
            )}
          </div>

          {/* Right – variant */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Theme switcher */}
            <div ref={themeMenuRef} className="relative">
              <HoverButton onClick={toggleThemeMenu}>
                <ThemeIcon className="w-6 h-6 text-t-primary" />
              </HoverButton>

              {isThemeMenuOpen && (
                <div className="absolute right-0 mt-2 w-40 rounded-lg bg-surface border border-border shadow-lg z-50">
                  <div className="py-1 px-2">
                    {themeItems.map((item) => {
                      const Icon = item.icon;
                      return (
                        <button
                          key={item.value}
                          onClick={() => {
                            setTheme(item.value);
                            setIsThemeMenuOpen(false);
                          }}
                          className={`w-full flex my-1 items-center gap-2 px-3 py-2 rounded-md text-sm transition ${
                            theme === item.value
                              ? "bg-surface-elevated"
                              : "hover:bg-surface-elevated"
                          }`}
                        >
                          <Icon className="w-5 h-5" />
                          {item.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            <UnauthNavbar />

            {navItems && (
              <button
                ref={mobileButtonRef}
                onClick={() => setIsMobileMenuOpen((p) => !p)}
                className="md:hidden p-2 rounded-lg hover:bg-surface-elevated"
              >
                {isMobileMenuOpen ? (
                  <XMarkIcon className="w-6 h-6" />
                ) : (
                  <Bars3Icon className="w-6 h-6" />
                )}
              </button>
            )}

            {navItems && isMobileMenuOpen && (
              <div
                ref={mobileMenuRef}
                className="absolute top-full left-0 w-full border-t border-border bg-surface md:hidden"
              >
                {navItems.map((item) => (
                  <NavLink
                    key={item.name}
                    to={item.link}
                    className="block px-4 py-2 my-1"
                    onClick={(e) => {
                      setIsMobileMenuOpen(false);
                    }}
                  >
                    {item.name}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
