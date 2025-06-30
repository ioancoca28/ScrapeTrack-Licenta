import React, { useState, useEffect } from "react";
import "./SignUp.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { Link, useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faEnvelope, faLock, faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";
import Navbar from "../../components/Navbar/Navbar";


function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  const handleSignup = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: name, email, password }),
      });

      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("token", data.token);
        navigate("/products");
        window.location.reload();
      } else {
        setError(data.error || "Registration failed.");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to connect to the server.");
    }
  };

  return (
    <>
      <Navbar />
      <div className="signup-page">
        <div className="signup-box">
          <h3 className="text-center mb-4">Sign Up</h3>
          <form onSubmit={handleSignup}>
            <div className="input-group mb-3">
              <span className="input-group-text">
                <FontAwesomeIcon icon={faUser} />
              </span>
              <input
                type="text"
                className="form-control"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="input-group mb-3">
              <span className="input-group-text">
                <FontAwesomeIcon icon={faEnvelope} />
              </span>
              <input
                type="email"
                className="form-control"
                placeholder="Enter your email"
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
            <div className="input-group mb-3">
              <span className="input-group-text">
                <FontAwesomeIcon icon={faLock} />
              </span>
              <input
                type="password"
                className="form-control"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>

           {error && (
  <div className="toast-message d-flex align-items-center justify-content-between">
    <div className="d-flex align-items-center">
      <FontAwesomeIcon icon={faExclamationTriangle} className="toast-icon me-2" />
      <span>{error}</span>
    </div>
    <button className="close-btn" onClick={() => setError("")}>×</button>
  </div>
)}

            <button className="btn btn-dark w-100">Sign Up</button>
          </form>
          <p className="text-center mt-3">
            Already have an account?{" "}
            <Link to="/login" className="login-link">
              Login
            </Link>
          </p>
        </div>
      </div>
    </>
  );
}

export default Signup;
