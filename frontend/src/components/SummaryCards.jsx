function SummaryCards({ summary }) {

    if (!summary) {
        return null;
    }

    const cards = [
        {
            title: "Total Employees",
            value: summary.total_analyzed,
        },
        {
            title: "Suspicious",
            value: summary.suspicious_count,
        },
        {
            title: "High Risk",
            value: summary.high_risk_count,
        },
        {
            title: "Medium Risk",
            value: summary.medium_risk_count,
        },
        {
            title: "Low Risk",
            value: summary.low_risk_count,
        },
    ];

    return (

        <div className="summary-grid">

            {cards.map((card) => (

                <div
                    className={`summary-card ${card.title
                        .toLowerCase()
                        .replace(" ", "-")}`}
                    key={card.title}
                >

                    <div className="summary-title">
                        {card.title}
                    </div>

                    <div className="summary-value">
                        {card.value}
                    </div>

                </div>

            ))}

        </div>
    );
}

export default SummaryCards;