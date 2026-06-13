import { useState, useEffect, useCallback } from "react";
import { Table, Select, Input, Tag, Space, Card, Typography, Spin, message } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { api } from "../api";

const { Title } = Typography;

const LEVEL_COLORS: Record<string, string> = {
  "985": "red", "211": "orange", "双一流": "blue", "普通": "default",
};

export default function UniversityPage() {
  const [provinces, setProvinces] = useState<any[]>([]);
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Record<string, string>>({});

  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [scores, setScores] = useState<Record<number, any[]>>({});
  const [scoresLoading, setScoresLoading] = useState(false);

  useEffect(() => {
    api.getProvinces().then(setProvinces).catch(() => {});
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getUniversities({
        page: String(page),
        page_size: "20",
        ...filters,
      });
      setData(res.items);
      setTotal(res.total);
    } catch {
      message.error("获取院校列表失败");
    }
    setLoading(false);
  }, [page, filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onExpand = async (expanded: boolean, record: any) => {
    if (!expanded) {
      setExpandedRow(null);
      return;
    }
    setExpandedRow(record.id);
    if (!scores[record.id]) {
      setScoresLoading(true);
      try {
        const res = await api.getScores({ university_id: String(record.id), page_size: "50" });
        setScores((prev) => ({ ...prev, [record.id]: res.items }));
      } catch {
        message.error("获取分数线失败");
      }
      setScoresLoading(false);
    }
  };

  const columns = [
    {
      title: "院校名称",
      dataIndex: "name",
      key: "name",
      render: (text: string, record: any) => (
        <Space>
          {text}
          {record.level !== "普通" && (
            <Tag color={LEVEL_COLORS[record.level]}>{record.level}</Tag>
          )}
        </Space>
      ),
    },
    { title: "所在地", dataIndex: "province_name", key: "province" },
    { title: "类型", dataIndex: "type", key: "type" },
  ];

  return (
    <div>
      <Title level={3}>院校浏览</Title>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            style={{ width: 160 }}
            placeholder="省份"
            allowClear
            onChange={(val) => { setFilters((f) => ({ ...f, province_id: val || "" })); setPage(1); }}
            options={provinces.map((p) => ({ value: String(p.id), label: p.name }))}
          />
          <Select
            style={{ width: 120 }}
            placeholder="层级"
            allowClear
            onChange={(val) => { setFilters((f) => ({ ...f, level: val || "" })); setPage(1); }}
            options={[
              { value: "985", label: "985" },
              { value: "211", label: "211" },
              { value: "双一流", label: "双一流" },
              { value: "普通", label: "普通" },
            ]}
          />
          <Select
            style={{ width: 120 }}
            placeholder="类型"
            allowClear
            onChange={(val) => { setFilters((f) => ({ ...f, utype: val || "" })); setPage(1); }}
            options={["综合", "理工", "师范", "医药", "农林", "财经", "政法", "语言"].map((t) => ({
              value: t,
              label: t,
            }))}
          />
          <Input
            style={{ width: 200 }}
            placeholder="搜索院校名称"
            prefix={<SearchOutlined />}
            allowClear
            onPressEnter={(e) => { setFilters((f) => ({ ...f, keyword: (e.target as HTMLInputElement).value })); setPage(1); }}
          />
        </Space>
      </Card>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          total,
          pageSize: 20,
          onChange: setPage,
          showTotal: (t) => `共 ${t} 所院校`,
        }}
        expandable={{
          expandedRowRender: (record) => {
            if (scoresLoading && expandedRow === record.id) return <Spin />;
            const sc = scores[record.id] || [];
            if (sc.length === 0) return <Typography.Text type="secondary">暂无分数线数据</Typography.Text>;
            return (
              <Table
                size="small"
                dataSource={sc}
                rowKey="id"
                pagination={false}
                columns={[
                  { title: "专业", dataIndex: "major_name", key: "major" },
                  { title: "类别", dataIndex: "major_category", key: "cat" },
                  { title: "年份", dataIndex: "year", key: "year" },
                  { title: "批次", dataIndex: "batch", key: "batch" },
                  { title: "最低分", dataIndex: "min_score", key: "min" },
                  { title: "平均分", dataIndex: "avg_score", key: "avg" },
                  { title: "最低位次", dataIndex: "min_rank", key: "rank", render: (v: number) => v?.toLocaleString() },
                ]}
              />
            );
          },
          onExpand,
          expandedRowKeys: expandedRow ? [expandedRow] : [],
        }}
      />
    </div>
  );
}
