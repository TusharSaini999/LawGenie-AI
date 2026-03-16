import { Outlet } from "react-router";
import Header from "../components/Header/Header";
import Footer from "../components/Footer/Footer";

const Layout = () => {
  return (
    <div className="flex flex-col h-screen w-full bg-bg text-t-primary">
      <Header />
      {/* Below margin-top values are related to navbar height */}
      <main className="flex flex-1 flex-row mt-[57px] sm:mt-[65px]">
        <div className="w-full">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
