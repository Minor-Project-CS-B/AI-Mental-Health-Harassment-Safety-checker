import React, { useState } from 'react';
import logo from '../assets/logo minor.jpg';




const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);


  // Function to quickly redirect to a neutral site for safety
  const handleQuickExit = () => {
   
    window.location.href = "http://localhost:5173/";
  };






  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
         
          {/* Updated Logo Section */}
          <div className="flex-shrink-0 flex items-center">
            <a href="/" className="flex items-center">
              <img
                src={logo}
                alt="AIMHHC logo"
                className="h-10 w-auto mr-3 rounded-lg"
              />
              <span className="font-bold text-xl text-gray-800 tracking-tight">
                AI<span className="text-blue-600">MH</span>HC
              </span>
            </a>
          </div>


          {/* Desktop Links ... Rest of your code */}








         


          {/* Desktop Links */}
          <div className="hidden md:flex space-x-8 items-center">
            <a href="/" className="text-gray-600 hover:text-blue-600 font-medium transition">Home</a>
            <a href="/chat" className="text-gray-600 hover:text-blue-600 font-medium transition">AI Chat</a>
            <a href="/assessment" className="text-gray-600 hover:text-blue-600 font-medium transition">Assessment</a>
            <a href="/dashboard" className="text-gray-600 hover:text-blue-600 font-medium transition">DashBoard</a>
            <a href="/help" className="text-gray-600 hover:text-blue-600 font-medium transition">Help And Support</a>
           
            {/* Quick Exit Button (Desktop) */}
            <button
              onClick={handleQuickExit}
              className="bg-red-50 text-red-600 px-4 py-2 rounded-full text-sm font-bold border border-red-100 hover:bg-red-600 hover:text-white transition-all shadow-sm"
            >
               LogOut
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
          <a href="/dashboard" className="block py-3 text-gray-600 font-medium">Dashboard</a>
          <a href="/assessment" className="block py-3 text-gray-600 font-medium">Assessment</a>
          <a href="/chat" className="block py-3 text-gray-600 font-medium">AI Chat</a>
          <a href="/help" className="block py-3 text-gray-600 font-medium">Help And Support</a>
          <a href="/" className="block py-3 text-gray-600 font-medium text-red-600 font-bold" onClick={handleQuickExit}>
            Logout
          </a>
        </div>
      )}
    </nav>
  );
};


export default Navbar;
;;;





