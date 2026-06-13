import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Card, Tag, Row, Col, Typography, Progress, Button, message, Tabs, Select, Spin } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { api } from "../api";

const { Title, Text } = Typography;

const CATEGORY_COLORS: Record<string, string> = {
  safety: "#52c41a",
  match: "#1677ff",
  reach: "#ff4d4f",
};

const CATEGORY_LABELS: Record<string, string> = {
  safety: "保底",
  match: "稳妥",
  reach: "冲刺",
};

const RATING_COLORS: Record<string, string> = {
  "A+": "#c41d7f", "A": "#cf1322", "A-": "#d4380d",
  "B+": "#d46b08", "B": "#d48806", "B-": "#7cb305",
  "C+": "#08979c", "C": "#1677ff", "C-": "#597ef7",
};

function ResultCard({ item, onAddToPlan }: { item: any; onAddToPlan: () => void }) {
  const prob = item.probability || 0;
  const color = CATEGORY_COLORS[item.category] || "#999";

  return (
    <Card
      size="small"
      style={{ marginBottom: 12 }}
      actions={[
        <Button
          key="add"
          type="link"
          icon={<PlusOutlined />}
          onClick={onAddToPlan}
        >
          加入志愿表
        </Button>,
      ]}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <Text strong style={{ fontSize: 16 }}>
              {item.university_name}
            </Text>
            <Tag color={item.university_level === "985" ? "red" : item.university_level === "211" ? "orange" : item.university_level === "双一流" ? "blue" : "default"}>
              {item.university_level}
            </Tag>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <Text type="secondary">
              {item.major_name} · {item.major_category}
            </Text>
            {item.discipline_rating && (
              <Tag color={RATING_COLORS[item.discipline_rating] || "default"} style={{ fontSize: 11, lineHeight: "18px" }}>
                {item.discipline_rating}
              </Tag>
            )}
          </div>
          <div style={{ display: "flex", gap: 16 }}>
            <Text type="secondary">
              最低分: {item.min_score?.toFixed(0)} | 均分: {item.avg_score?.toFixed(0)}
            </Text>
            <Text type="secondary">
              最低位次: {item.min_rank?.toLocaleString()}
            </Text>
          </div>
        </div>
        <div style={{ textAlign: "center", minWidth: 80 }}>
          <Progress
            type="circle"
            percent={prob}
            size={60}
            strokeColor={color}
            format={() => `${prob}%`}
          />
          <div style={{ marginTop: 4 }}>
            <Tag color={color}>{CATEGORY_LABELS[item.category]}</Tag>
          </div>
        </div>
      </div>
    </Card>
  );
}

export default function RecommendPage() {
  const [searchParams] = useSearchParams();
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("all");
  const [plans, setPlans] = useState<any[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null);

  const params = {
    province_id: searchParams.get("province_id") || "",
    score: searchParams.get("score") || "",
    rank: searchParams.get("rank") || "",
    subject_group: searchParams.get("subject_group") || "物理",
  };

  useEffect(() => {
    if (!params.province_id || !params.score) return;
    setLoading(true);
    api.getRecommend(params)
      .then(setResults)
      .catch(() => message.error("获取推荐失败"))
      .finally(() => setLoading(false));
    api.getPlans().then(setPlans).catch(() => {});
  }, [searchParams]);

  const addToPlan = async (item: any) => {
    if (!selectedPlan) {
      message.warning("请先在下拉框中选择一个志愿方案");
      return;
    }
    try {
      await api.addPlanItem(selectedPlan, {
        university_id: String(item.university_id),
        major_id: String(item.major_id),
        note: "",
      });
      message.success(`已添加 ${item.university_name} - ${item.major_name}`);
    } catch {
      message.error("添加失败");
    }
  };

  if (loading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;

  const items = results?.items || [];
  const total = results?.total || 0;
  const safetyItems = items.filter((i: any) => i.category === "safety");
  const matchItems = items.filter((i: any) => i.category === "match");
  const reachItems = items.filter((i: any) => i.category === "reach");

  return (
    <div>
      <div style={{ marginBottom: 24, display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
        <Title level={3} style={{ margin: 0 }}>
          推荐结果
        </Title>
        <Text type="secondary">
          分数: {params.score} | 位次: {Number(params.rank).toLocaleString()} | 选科: {params.subject_group}
        </Text>
        <div style={{ flex: 1 }} />
        <Select
          style={{ width: 240 }}
          placeholder="选择志愿方案"
          value={selectedPlan}
          onChange={setSelectedPlan}
          options={[
            { value: null, label: "选择志愿方案..." },
            ...plans.map((p: any) => ({ value: p.id, label: p.name })),
          ]}
        />
      </div>

      {items.length === 0 ? (
        <Card>
          <Text type="secondary">请输入分数和省份信息查看推荐结果</Text>
        </Card>
      ) : (
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: "all",
              label: `全部 (${total})`,
              children: (
                <Row gutter={[16, 0]}>
                  {items.map((item: any, idx: number) => (
                    <Col xs={24} lg={12} key={idx}>
                      <ResultCard item={item} onAddToPlan={() => addToPlan(item)} />
                    </Col>
                  ))}
                </Row>
              ),
            },
            {
              key: "reach",
              label: `冲刺 (${reachItems.length})`,
              children: (
                <Row gutter={[16, 0]}>
                  {reachItems.map((item: any, idx: number) => (
                    <Col xs={24} lg={12} key={idx}>
                      <ResultCard item={item} onAddToPlan={() => addToPlan(item)} />
                    </Col>
                  ))}
                </Row>
              ),
            },
            {
              key: "match",
              label: `稳妥 (${matchItems.length})`,
              children: (
                <Row gutter={[16, 0]}>
                  {matchItems.map((item: any, idx: number) => (
                    <Col xs={24} lg={12} key={idx}>
                      <ResultCard item={item} onAddToPlan={() => addToPlan(item)} />
                    </Col>
                  ))}
                </Row>
              ),
            },
            {
              key: "safety",
              label: `保底 (${safetyItems.length})`,
              children: (
                <Row gutter={[16, 0]}>
                  {safetyItems.map((item: any, idx: number) => (
                    <Col xs={24} lg={12} key={idx}>
                      <ResultCard item={item} onAddToPlan={() => addToPlan(item)} />
                    </Col>
                  ))}
                </Row>
              ),
            },
          ]}
        />
      )}
    </div>
  );
}
