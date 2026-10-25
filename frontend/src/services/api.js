import axios from "axios";

// ============================================================
// SPRING BOOT BACKEND
// ============================================================

const SPRING_API_URL = "http://localhost:8081";

const api = axios.create({
    baseURL: SPRING_API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});


// ============================================================
// AUTOMATICALLY ATTACH JWT
// ============================================================

api.interceptors.request.use(
    (config) => {

        const token =
            localStorage.getItem("token");

        if (token) {

            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    },

    (error) => {
        return Promise.reject(error);
    }
);


// ============================================================
// ANALYZE DATASET
// ============================================================

export const analyzeDataset = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(
        "/api/analysis/analyze",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};


// ============================================================
// EXPLAIN EMPLOYEE
// ============================================================

export const explainEmployee = async (employee) => {

    const response = await api.post(
        "/api/analysis/explain",
        employee
    );

    return response.data;
};


// ============================================================
// CURRENT USER
// ============================================================

export const getCurrentUser = async () => {

    const response = await api.get(
        "/api/user/me"
    );

    return response.data;
};


// ============================================================
// LOGIN
// ============================================================

export const loginUser = async (email, password) => {

    const response = await api.post(
        "/api/auth/login",
        {
            email,
            password
        }
    );

    return response.data;
};


export default api;