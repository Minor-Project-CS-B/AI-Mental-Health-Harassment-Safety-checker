function QuestionCard({ question, options, onAnswer }) {
  return (
    <div className="card">
      <h3>{question}</h3>

      {options.map((opt, index) => (
        <button key={index} onClick={() => onAnswer(opt)}>
          {opt}
        </button>
      ))}
    </div>
  );
}

export default QuestionCard;