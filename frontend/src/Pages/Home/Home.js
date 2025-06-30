import React from "react";
import Navbar from "../../components/Navbar/Navbar";
import {useNavigate} from  "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "./Home.css";
import illustration from "../../images/Data extraction-rafiki (1).svg";

const Home = () => {
    const navigate = useNavigate();

  return (
      <div>
        <Navbar/>
        <div className="hero-section">
            <div className="text-content">
                <h2 className="title">Welcome to ScrapeTrack</h2>
                <p className="lead">
                    The ultimate tool for tracking and analyzing online prices in real-time.
                </p>
                <p className="sub-lead">
                    Smart shopping starts here. Find the best price every time.
                </p>

                <button className="cta-button" onClick={() => navigate("/signup")}>
                    Start Tracking Now
                </button>
            </div>
            <div className="image-content">
                <img src={illustration} alt="Data Extraction"/>
            </div>
        </div>
      </div>
  );
};

export default Home;
