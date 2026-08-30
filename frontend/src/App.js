import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "@/pages/Login";
import Rooms from "@/pages/Rooms";
import Briefing from "@/pages/Briefing";
import Mission from "@/pages/Mission";
import Escape from "@/pages/Escape";
import Teacher from "@/pages/Teacher";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/escape-rooms" element={<Rooms />} />
        <Route path="/briefing/:sessionId" element={<Briefing />} />
        <Route path="/missione/:sessionId/:num" element={<Mission />} />
        <Route path="/escape/:sessionId" element={<Escape />} />
        <Route path="/docente" element={<Teacher />} />
      </Routes>
    </BrowserRouter>
  );
}
