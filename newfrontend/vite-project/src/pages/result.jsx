import RiskIndicator from "../components/RiskIndicator.jsx";
import Navbar from "../components/Navbar.jsx";
function Result() {

  const risk = "medium";

  return (
    <div>
      <Navbar/>
      <h2>Your Risk Level: {risk}</h2>

      {risk === "low" && <p>Practice breathing and relaxation.</p>}

      {risk === "medium" && <p>Consider speaking with a trusted person.</p>}

      {risk === "high" && <p>Please contact a helpline immediately.</p>}

        <RiskIndicator level={risk} />
    </div>
  );
}

export default Result;



