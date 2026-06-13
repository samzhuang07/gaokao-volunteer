import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import RecommendPage from "./pages/RecommendPage";
import UniversityPage from "./pages/UniversityPage";
import MajorPage from "./pages/MajorPage";
import PlanPage from "./pages/PlanPage";

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/recommend" element={<RecommendPage />} />
            <Route path="/universities" element={<UniversityPage />} />
            <Route path="/majors" element={<MajorPage />} />
            <Route path="/plans" element={<PlanPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
