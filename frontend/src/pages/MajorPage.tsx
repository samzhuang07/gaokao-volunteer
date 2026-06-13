import { useState, useEffect } from "react";
import { Card, Tag, Row, Col, Typography, Input } from "antd";
import { api } from "../api";

const { Title, Text } = Typography;

const CATEGORY_COLORS: Record<string, string> = {
  "工学": "blue", "理学": "geekblue", "医学": "red", "经济学": "gold",
  "管理学": "purple", "法学": "volcano", "文学": "cyan", "教育学": "green",
  "农学": "lime", "历史学": "orange", "哲学": "magenta", "艺术学": "pink",
};

export default function MajorPage() {
  const [categories, setCategories] = useState<string[]>([]);
  const [majors, setMajors] = useState<any[]>([]);
  const [selectedCat, setSelectedCat] = useState<string>("");
  const [keyword, setKeyword] = useState("");

  useEffect(() => {
    api.getCategories().then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    const params: Record<string, string> = {};
    if (selectedCat) params.category = selectedCat;
    if (keyword) params.keyword = keyword;
    api.getMajors(params).then((res) => setMajors(res.items)).catch(() => {});
  }, [selectedCat, keyword]);

  return (
    <div>
      <Title level={3}>专业浏览</Title>

      <Card size="small" style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 12 }}>
          <Text strong>学科门类：</Text>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
          <Tag
            color={selectedCat === "" ? "blue" : "default"}
            style={{ cursor: "pointer" }}
            onClick={() => setSelectedCat("")}
          >
            全部
          </Tag>
          {categories.map((cat) => (
            <Tag
              key={cat}
              color={selectedCat === cat ? CATEGORY_COLORS[cat] || "blue" : "default"}
              style={{ cursor: "pointer" }}
              onClick={() => setSelectedCat(cat)}
            >
              {cat}
            </Tag>
          ))}
        </div>
        <Input.Search
          style={{ maxWidth: 300 }}
          placeholder="搜索专业名称"
          allowClear
          onSearch={setKeyword}
        />
      </Card>

      <Row gutter={[16, 16]}>
        {majors.map((m) => (
          <Col xs={24} sm={12} md={8} lg={6} key={m.id}>
            <Card size="small" hoverable>
              <Text strong>{m.name}</Text>
              <br />
              <Tag color={CATEGORY_COLORS[m.category] || "default"}>{m.category}</Tag>
              <Text type="secondary" style={{ fontSize: 12 }}>
                代码: {m.code}
              </Text>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}
