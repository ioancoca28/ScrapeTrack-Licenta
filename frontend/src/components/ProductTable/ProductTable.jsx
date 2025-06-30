import React from "react";
import { FaInfoCircle } from "react-icons/fa";

function ProductTable({ title, data, onPriceHistory }) {
  if (!data || data.length === 0) return null;

  return (
    <div style={{ marginBottom: "40px", width: "100%" }}>
      <h2>{title}</h2>
      <div className="table-container">
        <table className="product-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Link</th>
              <th>Search Date</th>
              <th>Price</th>
              <th>History</th>
            </tr>
          </thead>
          <tbody>
            {data.map((product) => (
              <tr key={product.id}>
                <td>{product.nume}</td>
                <td>
                  <a href={product.link} target="_blank" rel="noopener noreferrer">
                    {product.link}
                  </a>
                </td>
                <td>{new Date(product.data_adaugarii).toISOString().split("T")[0]}</td>
                <td>{product.pret}</td>
                <td>
                  <button
                    title="View price history"
                    className="info-icon-btn"
                    onClick={() => onPriceHistory(product.nume, product.link)}
                  >
                    <FaInfoCircle size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ProductTable;
