function RiskIndicator({ level }) {

  const colors = {
    low: "green",
    medium: "orange",
    high: "red"
  }

  return (
    <div style={{color: colors[level]}}>
      <h2>Risk Level: {level}</h2>
    </div>
  )
}

export default RiskIndicator;