import { useState } from "react";
import { loginUser } from "../services/api";

function Login({ onLogin }) {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleLogin = async (event) => {

        event.preventDefault();

        setError("");

        if (!email || !password) {
            setError("Please enter email and password.");
            return;
        }

        try {

            setLoading(true);

            // const response = await axios.post(
            //     "http://localhost:8081/api/auth/login",
            //     {
            //         email,
            //         password
            //     }
            // );

            // const data = response.data;
            const data = await loginUser(
                email,
                password
            );
            onLogin(data);

            // Save JWT
            localStorage.setItem(
                "token",
                data.token
            );

            // Save user information
            localStorage.setItem(
                "user",
                JSON.stringify({
                    id: data.id,
                    name: data.name,
                    email: data.email,
                    role: data.role
                })
            );

            // Tell App.jsx login succeeded
            onLogin(data);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data ||
                "Invalid email or password."
            );

        } finally {

            setLoading(false);
        }
    };


    return (

        <div className="login-page">

            <div className="login-card">

                {/* LOGO / TITLE */}

                <div className="login-header">

                    <h1>
                        ThreatShield
                    </h1>

                    <p>
                        Recruitment Fraud Detection Platform
                    </p>

                </div>


                {/* LOGIN FORM */}

                <form
                    className="login-form"
                    onSubmit={handleLogin}
                >

                    <div className="form-group">

                        <label>
                            Email
                        </label>

                        <input
                            type="email"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) =>
                                setEmail(e.target.value)
                            }
                        />

                    </div>


                    <div className="form-group">

                        <label>
                            Password
                        </label>

                        <input
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) =>
                                setPassword(e.target.value)
                            }
                        />

                    </div>


                    {error && (

                        <div className="login-error">
                            {error}
                        </div>

                    )}


                    <button
                        type="submit"
                        className="login-button"
                        disabled={loading}
                    >

                        {loading
                            ? "Signing in..."
                            : "Login"
                        }

                    </button>

                </form>


                <div className="login-footer">

                    <span>
                        ThreatShield Security Platform
                    </span>

                </div>

            </div>

        </div>
    );
}

export default Login;