import React from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./Pages/Login/Login";
import Signup from "./Pages/SignUp/SignUp";
import Home from "./Pages/Home/Home";
import Products from "./Pages/Products/Products";
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <Router>
      <Routes>
          <Route path="*" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
          <Route path="/products" element={<Products />} />
      </Routes>
    </Router>
  );
}

export default App;

