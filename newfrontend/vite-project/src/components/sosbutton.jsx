// src/components/SOSButton.jsx
import React, { useState } from 'react';

const SOSButton = () => {
  const [active, setActive] = useState(false);

  const handleSOS = () => {
    setActive(true);
    // Logic to send GPS coordinates or alert emergency contacts
    alert("Emergency Alert Sent! Your location is being shared.");
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <button 
        onClick={handleSOS}
        className={`w-40 h-40 rounded-full font-bold text-white transition-all 
        ${active ? 'bg-red-800 scale-95' : 'bg-red-600 hover:bg-red-500 shadow-xl'}`}
      >
        {active ? "ALERTING..." : "SOS"}
      </button>
      <p className="mt-4 text-gray-500 text-sm italic">Press in case of immediate danger</p>
    </div>
  );
};

export default SOSButton;