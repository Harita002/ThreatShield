// import { useState } from "react";
// import { explainEmployee } from "../services/api";


// function EmployeeTable({ employees, onExplanation }) {

//     const [loadingId, setLoadingId] = useState(null);


//     if (!employees || employees.length === 0) {

//         return (
//             <div className="empty-state">
//                 No suspicious employees found.
//             </div>
//         );
//     }


//     const handleEmployeeClick = async (employee) => {

//     console.log("=================================");
//     console.log("EMPLOYEE CLICKED");
//     console.log("Employee:", employee);
//     console.log("Employee ID:", employee.employee_id);
//     console.log("Employee Data:", employee.employee_data);

//     try {

//         setLoadingId(employee.employee_id);

//         const explanation = await explainEmployee(
//             employee.employee_data
//         );

//         console.log("SHAP API RESPONSE:");
//         console.log(explanation);

//         onExplanation(
//             employee,
//             explanation
//         );

//         console.log("onExplanation called successfully");

//     } catch (error) {

//         console.error(
//             "SHAP EXPLANATION ERROR:",
//             error
//         );

//     } finally {

//         setLoadingId(null);

//     }
// };

//     return (

//         <div className="employee-section">

//             <h2>
//                 Suspicious Employees
//             </h2>

//             <div className="table-container">

//                 <table>

//                     <thead>

//                         <tr>

//                             <th>Employee ID</th>

//                             <th>Risk Score</th>

//                             <th>Probability</th>

//                             <th>Risk Level</th>

//                         </tr>

//                     </thead>


//                     <tbody>

//                         {employees.map(
//                             (employee) => (

//                                 <tr
//                                     key={
//                                         employee.employee_id
//                                     }
//                                     onClick={() =>
//                                         handleEmployeeClick(
//                                             employee
//                                         )
//                                     }
//                                     className="employee-row"
//                                 >

//                                     <td>

//                                         {loadingId ===
//                                         employee.employee_id

//                                             ? "Loading..."

//                                             : employee.employee_id

//                                         }

//                                     </td>

//                                     <td>

//                                         {employee.risk_score.toFixed(
//                                             2
//                                         )}%

//                                     </td>

//                                     <td>

//                                         {(
//                                             employee.probability *
//                                             100
//                                         ).toFixed(2)}%

//                                     </td>

//                                     <td>

//                                         <span
//                                             className={
//                                                 `risk-badge ${employee.risk_level.toLowerCase()}`
//                                             }
//                                         >

//                                             {
//                                                 employee.risk_level
//                                             }

//                                         </span>

//                                     </td>

//                                 </tr>

//                             )
//                         )}

//                     </tbody>

//                 </table>

//             </div>

//         </div>
//     );
// }


// export default EmployeeTable;


import { useMemo, useState } from "react";
import { Search, ArrowUpDown, ShieldAlert } from "lucide-react";
import { explainEmployee } from "../services/api";


function EmployeeTable({ employees, onExplanation }) {

    const [loadingId, setLoadingId] = useState(null);

    const [search, setSearch] = useState("");

    const [riskFilter, setRiskFilter] = useState("ALL");

    const [sortDescending, setSortDescending] =
        useState(true);


    /* =========================================================
       FILTER + SEARCH + SORT
    ========================================================= */

    const filteredEmployees = useMemo(() => {

        if (!employees) {
            return [];
        }

        let data = [...employees];


        /* SEARCH */

        if (search.trim()) {

            data = data.filter((employee) =>
                employee.employee_id
                    .toLowerCase()
                    .includes(
                        search.toLowerCase()
                    )
            );

        }


        /* RISK FILTER */

        if (riskFilter !== "ALL") {

            data = data.filter(
                (employee) =>
                    employee.risk_level ===
                    riskFilter
            );

        }


        /* SORT */

        data.sort((a, b) => {

            return sortDescending
                ? b.risk_score - a.risk_score
                : a.risk_score - b.risk_score;

        });


        return data;

    }, [
        employees,
        search,
        riskFilter,
        sortDescending
    ]);


    /* =========================================================
       EMPLOYEE CLICK
    ========================================================= */

    const handleEmployeeClick = async (employee) => {

    try {

        console.log(
            "================================="
        );

        console.log(
            "EMPLOYEE INVESTIGATION STARTED"
        );

        console.log(
            "Employee ID:",
            employee.employee_id
        );

        console.log(
            "Employee Data:",
            employee.employee_data
        );


        setLoadingId(
            employee.employee_id
        );


        if (!employee.employee_data) {

            console.error(
                "Employee data is missing!"
            );

            return;
        }


        const explanation =
            await explainEmployee(
                employee.employee_data
            );


        console.log(
            "SHAP EXPLANATION RECEIVED:",
            explanation
        );


        onExplanation(
            employee,
            explanation
        );

    }

    catch (error) {

        console.error(
            "Explanation error:",
            error
        );

    }

    finally {

        setLoadingId(null);

    }

};


    /* =========================================================
       EMPTY STATE
    ========================================================= */

    if (
        !employees ||
        employees.length === 0
    ) {

        return (

            <div className="empty-state">

                <ShieldAlert
                    size={40}
                />

                <p>
                    No suspicious employees found.
                </p>

            </div>

        );

    }


    return (

        <div className="employee-section">


            {/* =================================================
                HEADER
            ================================================= */}

            <div className="employee-header">

                <div>

                    <span className="section-label">
                        THREAT MONITORING
                    </span>

                    <h2>
                        Suspicious Employees
                    </h2>

                    <p className="section-description">
                        Click an employee to view AI-powered
                        SHAP risk analysis.
                    </p>

                </div>


                <div className="employee-count">

                    {filteredEmployees.length}
                    {" "}
                    detected

                </div>

            </div>


            {/* =================================================
                CONTROLS
            ================================================= */}

            <div className="table-controls">


                {/* SEARCH */}

                <div className="search-box">

                    <Search
                        size={17}
                    />

                    <input
                        type="text"
                        placeholder="Search employee ID..."
                        value={search}
                        onChange={(e) =>
                            setSearch(
                                e.target.value
                            )
                        }
                    />

                </div>


                {/* FILTER */}

                <select
                    value={riskFilter}
                    onChange={(e) =>
                        setRiskFilter(
                            e.target.value
                        )
                    }
                >

                    <option value="ALL">
                        All Risk Levels
                    </option>

                    <option value="HIGH">
                        High Risk
                    </option>

                    <option value="MEDIUM">
                        Medium Risk
                    </option>

                    <option value="LOW">
                        Low Risk
                    </option>

                </select>


                {/* SORT */}

                <button
                    className="sort-button"
                    onClick={() =>
                        setSortDescending(
                            !sortDescending
                        )
                    }
                >

                    <ArrowUpDown
                        size={16}
                    />

                    Risk Score

                    {sortDescending
                        ? " ↓"
                        : " ↑"
                    }

                </button>

            </div>


            {/* =================================================
                TABLE
            ================================================= */}

            <div className="table-container">

                <table>

                    <thead>

                        <tr>

                            <th>
                                Employee ID
                            </th>

                            <th>
                                Risk Score
                            </th>

                            <th>
                                Probability
                            </th>

                            <th>
                                Risk Level
                            </th>

                            <th>
                                Action
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {filteredEmployees.map(
                            (employee) => (

                                <tr
                                    key={
                                        employee.employee_id
                                    }
                                    className={
                                        "employee-row " +
                                        (
                                            employee.risk_score >= 90
                                                ? "critical-row"
                                                : ""
                                        )
                                    }
                                    onClick={() =>
                                        handleEmployeeClick(
                                            employee
                                        )
                                    }
                                >


                                    {/* EMPLOYEE ID */}

                                    <td>

                                        <div className="employee-id">

                                            {employee.risk_score >= 90 && (

                                                <span className="critical-dot">
                                                    ●
                                                </span>

                                            )}

                                            {loadingId ===
                                            employee.employee_id

                                                ? "Analyzing..."

                                                : employee.employee_id

                                            }

                                        </div>

                                    </td>


                                    {/* RISK SCORE */}

                                    <td>

                                        <div className="risk-score-wrapper">

                                            <div className="risk-score-text">

                                                {employee.risk_score.toFixed(
                                                    2
                                                )}%

                                            </div>


                                            <div className="risk-bar">

                                                <div
                                                    className={
                                                        `risk-bar-fill ${employee.risk_level.toLowerCase()}`
                                                    }
                                                    style={{
                                                        width:
                                                            `${employee.risk_score}%`
                                                    }}
                                                />

                                            </div>

                                        </div>

                                    </td>


                                    {/* PROBABILITY */}

                                    <td>

                                        {(
                                            employee.probability *
                                            100
                                        ).toFixed(2)}%

                                    </td>


                                    {/* RISK LEVEL */}

                                    <td>

                                        <span
                                            className={
                                                `risk-badge ${employee.risk_level.toLowerCase()}`
                                            }
                                        >

                                            {employee.risk_level}

                                        </span>

                                    </td>


                                    {/* ACTION */}

                                    <td>

                                        <button
                                            type="button"
                                            className="investigate-button"
                                            onClick={(event) => {
                                                event.preventDefault();
                                                event.stopPropagation();

                                                console.log(
                                                    "INVESTIGATE CLICKED:",
                                                    employee.employee_id
                                                );

                                                handleEmployeeClick(employee);
                                            }}
                                        >
                                            Investigate
                                        </button>

                                    </td>

                                </tr>

                            )
                        )}

                    </tbody>

                </table>

            </div>


            {filteredEmployees.length === 0 && (

                <div className="no-results">

                    No employees match your search/filter.

                </div>

            )}

        </div>

    );

}


export default EmployeeTable;