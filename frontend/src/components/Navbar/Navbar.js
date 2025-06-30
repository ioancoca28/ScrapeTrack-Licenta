import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "./Navbar.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSpider } from "@fortawesome/free-solid-svg-icons";

const Navbar = () => {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem("token"));

  useEffect(() => {
    const handleStorageChange = () => setToken(localStorage.getItem("token"));
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("produse");
  setToken(null);
  navigate("/home");
};
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container d-flex justify-content-between">
        <div className="navbar-brand">
          <FontAwesomeIcon icon={faSpider} className="me-2 spider-icon" />
          <span>ScrapeTrack</span>
        </div>
        <div className="btn-container">
          {token ? (
  <>
    <Link to="/home" className="btn-navbar btn-home me-3">Home</Link>
    <Link to="/products" className="btn-navbar btn-products me-3">Products</Link>
    <button className="btn-navbar btn-logout" onClick={handleLogout}>Logout</button>
  </>
) : (
  <>
    <Link to="/home" className="btn-navbar btn-home me-3">Home</Link>
    <Link to="/signup" className="btn-navbar btn-signup me-3">Sign Up</Link>
    <Link to="/login" className="btn-navbar btn-login">Login</Link>
  </>
)}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
