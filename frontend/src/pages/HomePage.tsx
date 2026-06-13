import { useState, useEffect } from "react";
import { Card, Form, Select, InputNumber, Button, Typography, Steps } from "antd";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const { Title, Paragraph } = Typography;

export default function HomePage() {
  const [provinces, setProvinces] = useState<{ id: number; name: string; gaokao_mode: string }[]>([]);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    api.getProvinces().then(setProvinces).catch(() => {});
  }, []);

  const onFinish = (values: any) => {
    const params = new URLSearchParams({
      province_id: values.province_id,
      score: values.score,
      rank: values.rank,
      subject_group: values.subject_group || "物理",
    });
    navigate(`/recommend?${params.toString()}`);
  };

  return (
    <div>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <Title level={2}>高考志愿智能填报系统</Title>
        <Paragraph type="secondary">
          输入你的高考分数和位次，智能匹配最适合你的院校和专业
        </Paragraph>
      </div>

      <Steps
        current={0}
        items={[
          { title: "输入分数", description: "填写高考信息" },
          { title: "查看推荐", description: "智能匹配院校" },
          { title: "管理志愿表", description: "创建和调整志愿方案" },
        ]}
        style={{ maxWidth: 600, margin: "0 auto 40px" }}
      />

      <Card style={{ maxWidth: 500, margin: "0 auto" }}>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item
            name="province_id"
            label="高考省份"
            rules={[{ required: true, message: "请选择省份" }]}
          >
            <Select
              showSearch
              placeholder="选择你的高考省份"
              optionFilterProp="label"
              options={provinces.map((p) => ({
                value: p.id,
                label: `${p.name} (${p.gaokao_mode})`,
              }))}
            />
          </Form.Item>

          <Form.Item
            name="subject_group"
            label="选科组 / 文理科"
            initialValue="物理"
          >
            <Select
              options={[
                { value: "物理", label: "物理 (理科)" },
                { value: "历史", label: "历史 (文科)" },
                { value: "不限", label: "不限" },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="score"
            label="高考分数"
            rules={[{ required: true, message: "请输入高考分数" }]}
          >
            <InputNumber
              min={100}
              max={750}
              style={{ width: "100%" }}
              placeholder="输入你的高考总分"
            />
          </Form.Item>

          <Form.Item
            name="rank"
            label="全省位次"
            rules={[{ required: true, message: "请输入位次" }]}
          >
            <InputNumber
              min={1}
              style={{ width: "100%" }}
              placeholder="输入在全省的排名"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" size="large" block>
              查看推荐院校
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
