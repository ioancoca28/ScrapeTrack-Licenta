import React, {useEffect, useState} from "react";
import "./Login.css";
import "bootstrap/dist/css/bootstrap.min.css";
import {Link, useNavigate} from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEnvelope, faLock, faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";
import Navbar from "../../components/Navbar/Navbar"



function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState("");


  useEffect(() => {
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  useEffect(() => {
  if (errorMessage) {
    const timer = setTimeout(() => setErrorMessage(""), 4000);
    return () => clearTimeout(timer);
  }
}, [errorMessage]);


  const handleLogin = async (e) => {
    e.preventDefault();
    console.log("Sending login request...");

    try {
      const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      console.log("Response status:", response.status);
      const data = await response.json();
      console.log("Response data:", data);

      if (response.ok) {
  localStorage.setItem("token", data.token);
  navigate("/products");
} else {
  setErrorMessage(data.error);
}
    } catch (error) {
  console.error("Error:", error);
  setErrorMessage("Failed to connect to the server.");
}
  };

  return (
       <>
       <Navbar />
         {errorMessage && (
             <div className="toast-message d-flex align-items-center justify-content-between">
               <div className="d-flex align-items-center">
                 <FontAwesomeIcon icon={faExclamationTriangle} className="toast-icon me-2"/>
                 <span>{errorMessage}</span>
               </div>
               <button className="close-btn" onClick={() => setErrorMessage("")}>×</button>
             </div>

         )}
         <div className="auth-page login-page">
           <div className="login-box">
             <h3 className="text-center mb-4">Login</h3>
             <form onSubmit={handleLogin}>
               <div className="input-group mb-3">
            <span className="input-group-text">
              <FontAwesomeIcon icon={faEnvelope}/>
            </span>
            <input
              type="email"
              className="form-control"
              placeholder="Enter your Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="input-group mb-3">
            <span className="input-group-text">
              <FontAwesomeIcon icon={faLock} />
            </span>
            <input
              type="password"
              className="form-control"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-dark w-100">Login</button>
        </form>
        <p className="no-account-text text-center mt-3">
          Don't have an account? <Link to="/signup" className="signup-link">Sign Up</Link>
        </p>
      </div>
    </div>
         </>
  );
}

export default Login;
