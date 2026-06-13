import { Layout as AntLayout, Menu } from "antd";
import { HomeOutlined, SearchOutlined, BankOutlined, BookOutlined, FileTextOutlined } from "@ant-design/icons";
import { useNavigate, useLocation, Outlet } from "react-router-dom";

const { Header, Content } = AntLayout;

const menuItems = [
  { key: "/", icon: <HomeOutlined />, label: "首页" },
  { key: "/recommend", icon: <SearchOutlined />, label: "智能推荐" },
  { key: "/universities", icon: <BankOutlined />, label: "院校浏览" },
  { key: "/majors", icon: <BookOutlined />, label: "专业浏览" },
  { key: "/plans", icon: <FileTextOutlined />, label: "志愿表" },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <AntLayout style={{ minHeight: "100vh" }}>
      <Header style={{ display: "flex", alignItems: "center", padding: "0 24px" }}>
        <div style={{ color: "#fff", fontSize: 20, fontWeight: "bold", marginRight: 40, whiteSpace: "nowrap" }}>
          高考志愿填报系统
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content style={{ padding: "24px", maxWidth: 1400, margin: "0 auto", width: "100%" }}>
        <Outlet />
      </Content>
    </AntLayout>
  );
}
