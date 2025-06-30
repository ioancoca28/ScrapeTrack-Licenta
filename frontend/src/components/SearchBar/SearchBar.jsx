import React from "react";
import { FaSearch } from "react-icons/fa";

function SearchBar({ searchTerm, setSearchTerm, handleSearch }) {
  return (
    <div className="search-container">
      <div className="search-wrapper">
        <FaSearch className="search-icon" />
        <input
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleSearch}
        />
      </div>
    </div>
  );
}

export default SearchBar;
