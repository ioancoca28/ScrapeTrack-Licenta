import React from "react";
import { Line } from "react-chartjs-2";

function PriceModal({ show, onClose, title, priceHistory }) {
  if (!show) return null;

  const sortedData = [...priceHistory]
  .sort((a, b) => new Date(b.data_adaugarii) - new Date(a.data_adaugarii))
  .slice(0, 10)
  .sort((a, b) => new Date(a.data_adaugarii) - new Date(b.data_adaugarii));


  const labels = sortedData.map(entry =>
    new Date(entry.data_adaugarii).toISOString().split("T")[0]
  );

  const dataPoints = sortedData.map(entry => entry.pret);

  const borderColor =
    dataPoints[0] > dataPoints[dataPoints.length - 1]
      ? "#38A169"
      : dataPoints[0] < dataPoints[dataPoints.length - 1]
      ? "#E53E3E"
      : "#CBD5E0";

  const maxPrice = Math.max(...dataPoints);
  const minPrice = Math.min(...dataPoints);

  const chartData = {
    labels,
    datasets: [
      {
        data: dataPoints,
        borderColor,
        backgroundColor: "rgba(79, 209, 197, 0.15)",
        tension: 0.4,
        pointBackgroundColor: dataPoints.map(p => {
          if (p === minPrice) return "#38A169";
          if (p === maxPrice) return "#E53E3E";
          return "#fff";
        }),
        pointBorderColor: borderColor,
        pointRadius: 5,
        pointHoverRadius: 8,
        pointHoverBorderWidth: 2,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => {
            const index = context.dataIndex;
            const value = context.raw;
            const prev = context.dataset.data[index - 1];
            const diff = prev !== undefined ? (value - prev).toFixed(2) : null;
            const diffText =
              diff && diff !== "0.00"
                ? ` (${diff > 0 ? "+" : ""}${diff} RON)`
                : "";
            return ` ${value} RON${diffText}`;
          },
          title: (items) => `Data: ${items[0].label}`,
        },
        backgroundColor: "#1A202C",
        titleColor: "#4FD1C5",
        bodyColor: "#E2E8F0",
        borderColor: "#4FD1C5",
        borderWidth: 1,
        padding: 10,
      }
    },
    layout: { padding: { top: 20 } },
    scales: {
      x: {
        ticks: { color: "#D1D5DB" },
        title: { display: false }
      },
      y: {
        suggestedMin: minPrice - 10,
        suggestedMax: maxPrice + 10,
        ticks: {
          callback: (value) => value.toFixed(0) + " RON",
          color: "#D1D5DB"
        },
        title: {
          display: true,
          text: " Market  Price (Ron)",
          color: "#E2E8F0",
          font: { size: 14, family: "Poppins", weight: "bold" }
        }
      }
    },
    animation: {
  duration: 1200,
  easing: "easeOutCubic",
  delay: (context) => context.dataIndex * 100,
}
  };

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <h3>{title}</h3>
          {maxPrice !== minPrice && (
            <p style={{ textAlign: "center", marginBottom: "15px", color: "#A0AEC0", fontSize: "14px" }}>
              Highest price: <strong>{maxPrice} RON</strong><br />
              Lowest price: <strong>{minPrice} RON</strong>
            </p>
          )}

          <div style={{width: '100%', paddingBottom: '5px'}}>
            <div>
              <div style={{height: '300px'}}>
                <Line data={chartData} options={chartOptions}/>
              </div>
              <div style={{
                marginTop: "5px",
                marginLeft: "250px",
                color: "#E2E8F0",
                fontWeight: "bold",
                fontFamily: "Poppins",
                fontSize: "14px"
              }}>
                Tracking Date
              </div>
            </div>
          </div>

          <button className="close-modal-btn" onClick={onClose}>Close</button>
        </div>
      </div>
    </>
  );
}

export default PriceModal;
