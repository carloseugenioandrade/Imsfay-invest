import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Carteira from "./pages/Carteira";
import Valuation from "./pages/Valuation";
import Dividendos from "./pages/Dividendos";
import Fiscal from "./pages/Fiscal";
import JurosCompostos from "./pages/JurosCompostos";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="carteira" element={<Carteira />} />
        <Route path="valuation" element={<Valuation />} />
        <Route path="dividendos" element={<Dividendos />} />
        <Route path="fiscal" element={<Fiscal />} />
        <Route path="juros-compostos" element={<JurosCompostos />} />
      </Route>
    </Routes>
  );
}
