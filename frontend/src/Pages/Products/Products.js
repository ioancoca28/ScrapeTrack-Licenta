import React, { useEffect, useState } from "react";
import { FaSearchMinus, FaInfoCircle } from "react-icons/fa";
import Navbar from "../../components/Navbar/Navbar";
import "./Products.css";
import PriceModal from "../../components/PriceModal/PriceModal";
import SearchBar from "../../components/SearchBar/SearchBar";
import ProductTable from "../../components/ProductTable/ProductTable";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

function Products() {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState({ altex: [], emag: [], flanco: [] });
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [priceHistory, setPriceHistory] = useState([]);
  const [modalTitle, setModalTitle] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem("produse");
    if (saved) {
      setProducts(JSON.parse(saved));
      setSearched(true);
    }
  }, []);

  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(""), 4000);
      return () => clearTimeout(timer);
    }
  }, [errorMessage]);

  const waitForScrapingToFinish = async (query, maxAttempts = 30, delay = 10000) => {
    for (let i = 0; i < maxAttempts; i++) {
      const res = await fetch("http://localhost:5000/scrape-status?query=" + encodeURIComponent(query));
      const data = await res.json();
      if (data.scraping === false) return true;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
    return false;
  };

  const pollForProducts = async (query, maxAttempts = 30, delay = 5000) => {
  for (let i = 0; i < maxAttempts; i++) {
    const res = await fetch("http://localhost:5000/get-products?query=" + encodeURIComponent(query));
    const data = await res.json();

    const deduplicate = (products) => {
      const seen = new Set();
      return products.filter(p => {
        const key = `${p.nume}-${p.link}-${p.source}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    };

    const altex = deduplicate(data.filter((p) => p.source === "Altex"));
const emag = deduplicate(data.filter((p) => p.source === "eMAG"));
const flanco = deduplicate(data.filter((p) => p.source === "Flanco"));


    const allEmpty = altex.length === 0 && emag.length === 0 && flanco.length === 0;

    if (!allEmpty) {
      return { altex, emag, flanco };
    }

    const scrapingStatusRes = await fetch("http://localhost:5000/scrape-status?query=" + encodeURIComponent(query));
    const scrapingStatus = await scrapingStatusRes.json();

    if (scrapingStatus.scraping === false) {
      return { altex: [], emag: [], flanco: [] };
    }

    await new Promise((resolve) => setTimeout(resolve, delay));
  }

  return { altex: [], emag: [], flanco: [] };
};

const handleSearch = async (event) => {
  if (event.key === "Enter") {
    if (searchTerm.trim() === "") {
      setErrorMessage("Please enter a search term.");
      return;
    }

    setLoading(true);
    setSearched(false);
    setProducts({ altex: [], emag: [], flanco: [] });
    localStorage.removeItem("produse");

    try {
      await fetch("http://localhost:5000/scrape-all", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchTerm }),
      });

      const scrapingDone = await waitForScrapingToFinish(searchTerm);

      if (scrapingDone) {
        const newProducts = await pollForProducts(searchTerm);
        setProducts(newProducts);
        localStorage.setItem("produse", JSON.stringify(newProducts));
        setSearched(true);
      }

      setLoading(false);
    } catch (error) {
      console.error("Eroare:", error);
      setLoading(false);
      setSearched(true);
    }
  }
};


  const handlePriceHistory = async (nume, link) => {
    try {
      const response = await fetch(
        `http://localhost:5000/get-price-history?nume=${encodeURIComponent(nume)}&link=${encodeURIComponent(link)}`
      );
      const data = await response.json();

      if (data.error) {
        console.error(data.error);
      } else {
        setModalTitle(nume);
        setPriceHistory(data);
        setShowModal(true);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <>
      <Navbar />
      {errorMessage && (
        <div className="toast-message d-flex align-items-center justify-content-between">
          <div className="d-flex align-items-center">
            <FaInfoCircle className="toast-icon me-2" />
            <span>{errorMessage}</span>
          </div>
          <button className="close-btn" onClick={() => setErrorMessage("")}>×</button>
        </div>
      )}

      <div className="products-page">
        <SearchBar
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            handleSearch={handleSearch}
        />
        {!searchTerm && (
  <p className="info-text">
    Monitor prices across top retailers with one search.
  </p>
)}


        {loading && (
            <div className="loading-message">
              Searching for products
              <span className="bouncing-dots">
              <span></span>
              <span></span>
              <span></span>
            </span>
            </div>
        )}

        {searched && !loading &&
            products.altex.length === 0 &&
            products.emag.length === 0 &&
            products.flanco.length === 0 && (
                <div className="no-results-message">
                  <FaSearchMinus size={48} style={{marginBottom: "10px", color: "#ccc"}}/>
                  <h3>No products found for your search.</h3>
                  <p>Try a different keyword or come back later.</p>
                </div>
            )}

        {!loading && (
            <div style={{width: "100%"}}>
              <ProductTable title="Altex Products" data={products.altex} onPriceHistory={handlePriceHistory}/>
              <ProductTable title="eMAG Products" data={products.emag} onPriceHistory={handlePriceHistory}/>
              <ProductTable title="Flanco Products" data={products.flanco} onPriceHistory={handlePriceHistory}/>
            </div>
        )}

        <PriceModal
            show={showModal}
            onClose={() => setShowModal(false)}
            title={modalTitle}
            priceHistory={priceHistory}
        />
      </div>
    </>
  );
}

export default Products;
