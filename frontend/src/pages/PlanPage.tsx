import { useState, useEffect, useCallback } from "react";
import {
  Card, Typography, Button, List, Tag, Modal, Form, InputNumber, Select,
  Popconfirm, Empty, message, Spin,
} from "antd";
import { PlusOutlined, DeleteOutlined, HolderOutlined } from "@ant-design/icons";
import {
  DndContext, closestCenter, PointerSensor, useSensor, useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext, verticalListSortingStrategy, useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { api } from "../api";
import { usePlanStore, type VolunteerItem } from "../stores/planStore";

const { Title, Text } = Typography;

function SortableItem({ item, onDelete }: { item: VolunteerItem; onDelete: () => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: item.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style}>
      <List.Item
        actions={[
          <Popconfirm
            key="del"
            title="确定删除此志愿？"
            onConfirm={onDelete}
          >
            <Button type="link" danger icon={<DeleteOutlined />} />
          </Popconfirm>,
        ]}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, width: "100%" }}>
          <div {...attributes} {...listeners} style={{ cursor: "grab", padding: 4 }}>
            <HolderOutlined style={{ fontSize: 18, color: "#999" }} />
          </div>
          <Tag color="blue" style={{ minWidth: 32, textAlign: "center" }}>
            {item.priority}
          </Tag>
          <div style={{ flex: 1 }}>
            <Text strong>
              {item.university_name}
            </Text>
            <Tag
              color={item.university_level === "985" ? "red" : item.university_level === "211" ? "orange" : item.university_level === "双一流" ? "blue" : "default"}
              style={{ marginLeft: 8 }}
            >
              {item.university_level}
            </Tag>
            <br />
            <Text type="secondary">
              {item.major_name} · {item.major_category}
            </Text>
          </div>
        </div>
      </List.Item>
    </div>
  );
}

export default function PlanPage() {
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [createForm] = Form.useForm();
  const [provinces, setProvinces] = useState<any[]>([]);

  const { currentPlan, setCurrentPlan, reorderItems, removeItem } = usePlanStore();

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
  );

  const loadPlans = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getPlans();
      setPlans(data);
    } catch { message.error("获取志愿方案失败"); }
    setLoading(false);
  }, []);

  useEffect(() => { loadPlans(); }, [loadPlans]);
  useEffect(() => { api.getProvinces().then(setProvinces).catch(() => {}); }, []);

  const selectPlan = async (id: number) => {
    try {
      const plan = await api.getPlan(id);
      setCurrentPlan(plan);
    } catch { message.error("获取志愿方案详情失败"); }
  };

  const createPlan = async () => {
    try {
      const values = await createForm.validateFields();
      await api.createPlan({
        name: values.name || "我的志愿方案",
        province_id: String(values.province_id),
        score: String(values.score),
        rank: String(values.rank),
        subject_group: values.subject_group || "物理",
      });
      message.success("创建成功");
      setCreateModalOpen(false);
      createForm.resetFields();
      loadPlans();
    } catch { /* validation error */ }
  };

  const deletePlan = async (id: number) => {
    try {
      await api.deletePlan(id);
      message.success("已删除");
      if (currentPlan?.id === id) setCurrentPlan(null);
      loadPlans();
    } catch { message.error("删除失败"); }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id || !currentPlan) return;

    const oldIndex = currentPlan.items.findIndex((i) => i.id === active.id);
    const newIndex = currentPlan.items.findIndex((i) => i.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;

    const newItems = [...currentPlan.items];
    const [removed] = newItems.splice(oldIndex, 1);
    newItems.splice(newIndex, 0, removed);
    const orderedIds = newItems.map((i) => i.id);

    reorderItems(orderedIds);
    try {
      await api.reorderItems(currentPlan.id, orderedIds);
    } catch { message.error("排序保存失败"); }
  };

  const deleteItem = async (itemId: number) => {
    if (!currentPlan) return;
    try {
      await api.deletePlanItem(currentPlan.id, itemId);
      removeItem(itemId);
      message.success("已删除");
    } catch { message.error("删除失败"); }
  };

  return (
    <div>
      <Title level={3}>志愿表管理</Title>

      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 24, minHeight: "60vh" }}>
        <Card
          title="我的志愿方案"
          extra={
            <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => setCreateModalOpen(true)}>
              新建
            </Button>
          }
        >
          {loading ? (
            <Spin />
          ) : plans.length === 0 ? (
            <Empty description="暂无方案，点击上方按钮创建" />
          ) : (
            <List
              size="small"
              dataSource={plans}
              renderItem={(plan: any) => (
                <List.Item
                  style={{
                    cursor: "pointer",
                    background: currentPlan?.id === plan.id ? "#e6f4ff" : undefined,
                    padding: "8px 12px",
                    borderRadius: 6,
                    marginBottom: 4,
                  }}
                  onClick={() => selectPlan(plan.id)}
                  actions={[
                    <Popconfirm key="del" title="确定删除此方案？" onConfirm={() => deletePlan(plan.id)}>
                      <Button type="link" danger size="small" icon={<DeleteOutlined />} />
                    </Popconfirm>,
                  ]}
                >
                  <div>
                    <Text strong>{plan.name}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {plan.score}分 | 位次{plan.rank?.toLocaleString()} | {plan.item_count}个志愿
                    </Text>
                  </div>
                </List.Item>
              )}
            />
          )}
        </Card>

        <Card title={currentPlan ? currentPlan.name : "志愿详情"}>
          {!currentPlan ? (
            <Empty description="请选择或创建一个志愿方案" />
          ) : currentPlan.items.length === 0 ? (
            <Empty description="该方案暂无志愿条目，请在推荐页面添加" />
          ) : (
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={currentPlan.items.map((i) => i.id)} strategy={verticalListSortingStrategy}>
                <List
                  dataSource={currentPlan.items}
                  renderItem={(item) => (
                    <SortableItem key={item.id} item={item} onDelete={() => deleteItem(item.id)} />
                  )}
                />
              </SortableContext>
            </DndContext>
          )}
        </Card>
      </div>

      <Modal
        title="新建志愿方案"
        open={createModalOpen}
        onOk={createPlan}
        onCancel={() => setCreateModalOpen(false)}
        okText="创建"
        cancelText="取消"
      >
        <Form form={createForm} layout="vertical">
          <Form.Item name="name" label="方案名称" initialValue="我的志愿方案">
            <Select
              options={[{ value: "我的志愿方案", label: "我的志愿方案" }]}
            />
          </Form.Item>
          <Form.Item name="province_id" label="目标省份" rules={[{ required: true, message: "请选择省份" }]}>
            <Select
              options={provinces.map((p: any) => ({ value: p.id, label: p.name }))}
            />
          </Form.Item>
          <Form.Item name="score" label="高考分数" rules={[{ required: true }]}>
            <InputNumber min={100} max={750} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="rank" label="全省位次" rules={[{ required: true }]}>
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="subject_group" label="选科组" initialValue="物理">
            <Select options={[{ value: "物理", label: "物理" }, { value: "历史", label: "历史" }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
