import { useEffect, useState } from "react";

import "./App.css";

import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";

import { getCurrentUser } from "./services/api";


function App() {

    const [user, setUser] = useState(null);

    const [checkingAuth, setCheckingAuth] =
        useState(true);


    // ========================================================
    // CHECK EXISTING LOGIN
    // ========================================================

    useEffect(() => {

        const token =
            localStorage.getItem("token");

        if (!token) {

            setCheckingAuth(false);

            return;
        }


        getCurrentUser()

            .then((data) => {

                // JWT is valid
                setUser(data);

            })

            .catch((error) => {

                console.error(
                    "Authentication check failed:",
                    error
                );

                // JWT is invalid/expired
                localStorage.removeItem("token");
                localStorage.removeItem("user");

                setUser(null);

            })

            .finally(() => {

                setCheckingAuth(false);

            });

    }, []);


    // ========================================================
    // LOGIN
    // ========================================================

    const handleLogin = (data) => {

        const userData = {

            id: data.id,

            name: data.name,

            email: data.email,

            role: data.role

        };

        localStorage.setItem(
            "token",
            data.token
        );

        localStorage.setItem(
            "user",
            JSON.stringify(userData)
        );

        setUser(userData);
    };


    // ========================================================
    // LOGOUT
    // ========================================================

    const handleLogout = () => {

        localStorage.removeItem("token");

        localStorage.removeItem("user");

        setUser(null);
    };


    // ========================================================
    // CHECKING AUTHENTICATION
    // ========================================================

    if (checkingAuth) {

        return (
            <div className="auth-loading">

                Checking authentication...

            </div>
        );
    }


    // ========================================================
    // LOGIN PAGE
    // ========================================================

    if (!user) {

        return (
            <Login
                onLogin={handleLogin}
            />
        );
    }


    // ========================================================
    // DASHBOARD
    // ========================================================

    return (
        <Dashboard
            user={user}
            onLogout={handleLogout}
        />
    );
}


export default App;