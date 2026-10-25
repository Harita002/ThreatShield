import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function RiskAnalytics({ summary }) {

    if (!summary) {
        return null;
    }

    const data = [
        {
            name: "Suspicious",
            count: summary.suspicious_count
        },
        {
            name: "High Risk",
            count: summary.high_risk_count
        },
        {
            name: "Medium Risk",
            count: summary.medium_risk_count
        },
        {
            name: "Low Risk",
            count: summary.low_risk_count
        }
    ];

    return (
        <section className="analytics-section">

            <div className="analytics-header">

                <div>
                    <p className="analytics-label">
                        SECURITY ANALYTICS
                    </p>

                    <h2>
                        Threat Distribution
                    </h2>

                    <p className="analytics-description">
                        Overview of detected employee risk levels
                    </p>
                </div>

            </div>

            <div className="analytics-card">

                <ResponsiveContainer
                    width="100%"
                    height={320}
                >

                    <BarChart
                        data={data}
                        margin={{
                            top: 20,
                            right: 20,
                            left: 0,
                            bottom: 10
                        }}
                    >

                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="rgba(255,255,255,0.08)"
                        />

                        <XAxis
                            dataKey="name"
                            stroke="#8b9bb4"
                        />

                        <YAxis
                            allowDecimals={false}
                            stroke="#8b9bb4"
                        />

                        <Tooltip
                            contentStyle={{
                                background: "#111827",
                                border: "1px solid #26354d",
                                borderRadius: "10px",
                                color: "#ffffff"
                            }}
                        />

                        <Bar
                            dataKey="count"
                            fill="#6366f1"
                            radius={[8, 8, 0, 0]}
                            animationDuration={1000}
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>

        </section>
    );
}

export default RiskAnalytics;