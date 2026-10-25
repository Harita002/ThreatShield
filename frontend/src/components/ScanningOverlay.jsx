import { useEffect, useState } from "react";


function ScanningOverlay({ active }) {

    const [progress, setProgress] = useState(0);


    useEffect(() => {

        if (!active) {

            setProgress(0);

            return;

        }


        const interval = setInterval(() => {

            setProgress((current) => {

                if (current >= 92) {
                    return current;
                }

                const increment =
                    Math.floor(
                        Math.random() * 7
                    ) + 2;

                return Math.min(
                    current + increment,
                    92
                );

            });

        }, 350);


        return () => {
            clearInterval(interval);
        };

    }, [active]);


    if (!active) {
        return null;
    }


    const getStage = () => {

        if (progress < 25) {
            return 0;
        }

        if (progress < 50) {
            return 1;
        }

        if (progress < 75) {
            return 2;
        }

        return 3;

    };


    const currentStage = getStage();


    const stages = [
        "Dataset validation",
        "Feature engineering",
        "AI threat classification",
        "Preparing risk intelligence"
    ];


    return (

        <div className="scanner-overlay">

            <div className="scanner-card">


                {/* ANIMATED SHIELD */}

                <div className="scanner-icon">

                    <div className="scanner-ring">

                        <div className="scanner-core">
                            TS
                        </div>

                    </div>

                </div>


                {/* TITLE */}

                <div className="scanner-label">
                    THREATSHIELD AI
                </div>


                <h2>
                    Analyzing Dataset
                </h2>


                <p className="scanner-description">
                    AI is analyzing employee activity
                    for potential insider threats.
                </p>


                {/* PROGRESS */}

                <div className="scanner-progress-header">

                    <span>
                        Threat analysis
                    </span>

                    <strong>
                        {progress}%
                    </strong>

                </div>


                <div className="scanner-progress">

                    <div
                        className="scanner-progress-fill"
                        style={{
                            width:
                                `${progress}%`
                        }}
                    />

                </div>


                {/* STAGES */}

                <div className="scanner-stages">

                    {stages.map(
                        (stage, index) => (

                            <div
                                key={stage}
                                className={
                                    `scanner-stage ${
                                        index < currentStage
                                            ? "completed"
                                            : index === currentStage
                                            ? "active"
                                            : ""
                                    }`
                                }
                            >

                                <span className="stage-icon">

                                    {index < currentStage
                                        ? "✓"
                                        : index === currentStage
                                        ? "◉"
                                        : "○"
                                    }

                                </span>

                                <span>
                                    {stage}
                                </span>

                            </div>

                        )
                    )}

                </div>


                <div className="scanner-warning">

                    Do not close the browser while
                    analysis is in progress.

                </div>

            </div>

        </div>

    );

}


export default ScanningOverlay;