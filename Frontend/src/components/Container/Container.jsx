import React from "react";

const Container = ({ className = "", children }) => {
  return (
    <div
      className={`px-8 py-12 md:px-16 lg:px-24 text-t-primary bg-bg ${className}`}
    >
      {children}
    </div>
  );
};

export default Container;
