// import "./Navbar.css";
// function Navbar() {
//   return (
//     <nav className="navbar">
//       <h2 className="logo">MindSafe AI</h2>

//       <div className="nav-links">
//         <a href="/" className="nav-link">Home </a>
//         <a href="/questions" className="nav-link"> StartQuestionaires </a>
//         <a href="/dashboard" className="nav-link"> DashBoard </a>
//         <a href="/result" className="nav-link">  Result </a>
//         <a href="/privacy" className="nav-link">  Privacy </a>
//       </div>
//     </nav>
//   );
// }
// s
// export default Navbar;


import React, { useState } from 'react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  // Function to quickly redirect to a neutral site for safety
  const handleQuickExit = () => {
    window.location.href = "https://www.google.com/search?q=weather";
  };

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          
          {/* Logo Section */}
          <div className="flex-shrink-0 flex items-center">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-2">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <span className="font-bold text-xl text-gray-800 tracking-tight">
              Safe<span className="text-blue-600">Mind</span>
            </span>
          </div>

          {/* Desktop Links */}
          <div className="hidden md:flex space-x-8 items-center">
            <a href="/" className="text-gray-600 hover:text-blue-600 font-medium transition">Home</a>
            <a href="" className="text-gray-600 hover:text-blue-600 font-medium transition">Assessment</a>
            <a href="#" className="text-gray-600 hover:text-blue-600 font-medium transition">Safety Tips</a>
            <a href="#" className="text-gray-600 hover:text-blue-600 font-medium transition">Helplines</a>
            
            {/* Quick Exit Button (Desktop) */}
            <button 
              onClick={handleQuickExit}
              className="bg-red-50 text-red-600 px-4 py-2 rounded-full text-sm font-bold border border-red-100 hover:bg-red-600 hover:text-white transition-all shadow-sm"
            >
              QUICK EXIT
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button 
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-600 hover:text-gray-900 focus:outline-none"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Content */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-gray-50 pb-4 px-4 space-y-2">
          <a href="#" className="block py-3 text-gray-600 font-medium">Home</a>
          <a href="#" className="block py-3 text-gray-600 font-medium">Assessment</a>
          <a href="#" className="block py-3 text-gray-600 font-medium">Safety Tips</a>
          <a href="#" className="block py-3 text-gray-600 font-medium text-red-600 font-bold" onClick={handleQuickExit}>
            QUICK EXIT
          </a>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
;;;

