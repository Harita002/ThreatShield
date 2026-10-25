import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip,
    Legend,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid
} from "recharts";


function RiskCharts({ summary }) {

    if (!summary) {
        return null;
    }


    const riskData = [
        {
            name: "High Risk",
            value: summary.high_risk_count
        },
        {
            name: "Medium Risk",
            value: summary.medium_risk_count
        },
        {
            name: "Low Risk",
            value: summary.low_risk_count
        }
    ];


    const suspiciousData = [
        {
            name: "Suspicious",
            value: summary.suspicious_count
        },
        {
            name: "Normal",
            value:
                summary.total_analyzed -
                summary.suspicious_count
        }
    ];


    return (

        <div className="charts-grid">

            {/* RISK DISTRIBUTION */}

            <div className="chart-card">

                <div className="chart-header">

                    <span className="chart-label">
                        RISK ANALYTICS
                    </span>

                    <h2>
                        Risk Distribution
                    </h2>

                </div>


                <div className="chart-container">

                    <ResponsiveContainer
                        width="100%"
                        height={300}
                    >

                        <PieChart>

                            <Pie
                                data={riskData}
                                dataKey="value"
                                nameKey="name"
                                cx="50%"
                                cy="50%"
                                innerRadius={75}
                                outerRadius={110}
                                paddingAngle={4}
                                animationDuration={900}
                            >

                                <Cell fill="#ff4d67" />
                                <Cell fill="#ffb347" />
                                <Cell fill="#38d996" />

                            </Pie>


                            <Tooltip
                                contentStyle={{
                                    background:
                                        "#111827",
                                    border:
                                        "1px solid #334155",
                                    borderRadius:
                                        "10px"
                                }}
                            />


                            <Legend />

                        </PieChart>

                    </ResponsiveContainer>

                </div>

            </div>


            {/* THREAT OVERVIEW */}

            <div className="chart-card">

                <div className="chart-header">

                    <span className="chart-label">
                        THREAT OVERVIEW
                    </span>

                    <h2>
                        Suspicious vs Normal
                    </h2>

                </div>


                <div className="chart-container">

                    <ResponsiveContainer
                        width="100%"
                        height={300}
                    >

                        <BarChart
                            data={suspiciousData}
                            layout="vertical"
                            margin={{
                                top: 20,
                                right: 30,
                                left: 20,
                                bottom: 20
                            }}
                        >

                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#263449"
                            />

                            <XAxis
                                type="number"
                                stroke="#7f8ea8"
                            />

                            <YAxis
                                dataKey="name"
                                type="category"
                                stroke="#7f8ea8"
                            />

                            <Tooltip
                                contentStyle={{
                                    background:
                                        "#111827",
                                    border:
                                        "1px solid #334155",
                                    borderRadius:
                                        "10px"
                                }}
                            />

                            <Bar
                                dataKey="value"
                                radius={[0, 8, 8, 0]}
                                animationDuration={900}
                            >

                                <Cell fill="#ff4d67" />
                                <Cell fill="#38a8ff" />

                            </Bar>

                        </BarChart>

                    </ResponsiveContainer>

                </div>

            </div>

        </div>

    );
}


export default RiskCharts;