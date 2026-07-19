import pptxgen from "pptxgenjs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const IMG = (p) => path.join(__dirname, "report_images", p);

// ============== DESIGN TOKENS (NEW: Orange + Navy) ==============
const C = {
  ORANGE: "FF6B35",
  NAVY: "1A1A2E",
  WHITE: "FFFFFF",
  LIGHT_BG: "F8F9FA",
  GRAY: "B0B0B0",
  GREEN: "2ECC71",
  RED: "E74C3C",
  TEXT: "1A1A2E",
};

const FONT = "Microsoft YaHei";

// ============== UTILITIES ==============
function addBrand(slide) {
  slide.addText("美园外卖", {
    x: 8.5, y: 0.15, w: 1.2, h: 0.3,
    fontSize: 11, fontFace: FONT, color: C.GRAY, align: "right", margin: 0,
  });
}

function addBottomLine(slide) {
  slide.addShape("rect", {
    x: 0.56, y: 5.2, w: 8.88, h: 0.025,
    fill: { color: C.ORANGE },
  });
}

function addPageNum(slide, num) {
  slide.addText(String(num), {
    x: 8.5, y: 5.3, w: 1.2, h: 0.25,
    fontSize: 10, fontFace: FONT, color: C.GRAY, align: "right", margin: 0,
  });
}

function addFrame(slide, num) {
  addBrand(slide);
  addBottomLine(slide);
  addPageNum(slide, num);
}

function addTransitionSlide(pres, partNum, title, name, decorShapeType) {
  const slide = pres.addSlide();
  slide.background = { color: C.NAVY };

  slide.addText(partNum, {
    x: 0.8, y: 1.6, w: 8, h: 0.5,
    fontSize: 15, fontFace: FONT, color: C.ORANGE, margin: 0,
  });
  slide.addText(title, {
    x: 0.8, y: 2.1, w: 8, h: 0.9,
    fontSize: 36, fontFace: FONT, bold: true, color: C.WHITE, margin: 0,
  });
  slide.addText(name, {
    x: 0.8, y: 3.2, w: 8, h: 0.5,
    fontSize: 16, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // Decorative shape bottom-right
  const decorTx = 0.15;
  if (decorShapeType === "circle") {
    slide.addShape("ellipse", {
      x: 8.2, y: 3.8, w: 2.2, h: 2.2,
      fill: { color: C.ORANGE, transparency: 85 },
    });
  } else if (decorShapeType === "triangle") {
    slide.addShape("rect", {
      x: 7.5, y: 4.0, w: 2.0, h: 1.8,
      fill: { color: C.ORANGE, transparency: 85 },
      rotate: 45,
    });
  } else {
    slide.addShape("rect", {
      x: 7.5, y: 3.8, w: 1.8, h: 1.8,
      fill: { color: C.ORANGE, transparency: 85 },
      rotate: 45,
    });
  }
  return slide;
}

// ============== SLIDE 1: COVER ==============
function createCover(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };

  // Right orange block
  slide.addShape("rect", {
    x: 7.0, y: 0, w: 3.0, h: 5.625,
    fill: { color: C.ORANGE },
  });

  // Left content
  slide.addText("美园外卖", {
    x: 0.8, y: 1.2, w: 5.5, h: 1.0,
    fontSize: 48, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });
  slide.addText("基于Android的手机外卖管理系统", {
    x: 0.8, y: 2.2, w: 5.5, h: 0.5,
    fontSize: 22, fontFace: FONT, color: C.TEXT, margin: 0,
  });

  slide.addShape("rect", {
    x: 0.8, y: 2.9, w: 1.0, h: 0.025,
    fill: { color: C.ORANGE },
  });

  slide.addText("信息系统分析与设计 课程设计答辩", {
    x: 0.8, y: 3.15, w: 5.5, h: 0.4,
    fontSize: 15, fontFace: FONT, color: C.GRAY, margin: 0,
  });
  slide.addText("崔桐浩  ·  马鸣远  ·  王略帆", {
    x: 0.8, y: 3.65, w: 5.5, h: 0.4,
    fontSize: 16, fontFace: FONT, color: C.TEXT, margin: 0,
  });
  slide.addText("2026.07", {
    x: 0.8, y: 4.15, w: 5.5, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // Right block: white text on orange
  slide.addText("手机外卖\n管理App", {
    x: 7.2, y: 1.8, w: 2.6, h: 1.2,
    fontSize: 18, fontFace: FONT, bold: true, color: C.WHITE, align: "center", valign: "middle", margin: 0,
  });
  slide.addText("校园 · 便捷 · 智能", {
    x: 7.2, y: 3.0, w: 2.6, h: 0.4,
    fontSize: 12, fontFace: FONT, color: C.WHITE, align: "center", margin: 0,
  });
}

// ============== SLIDE 2: PROJECT OVERVIEW ==============
function createOverview(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 2);

  // Top positioning statement
  slide.addText("三角色 · 纯本地 · 全闭环", {
    x: 1, y: 0.6, w: 8, h: 0.7,
    fontSize: 28, fontFace: FONT, bold: true, color: C.TEXT, align: "center", margin: 0,
  });
  slide.addText("买家 / 商家 / 管理员    |    Android + SQLite    |    浏览 → 下单 → 履约 → 管控", {
    x: 1, y: 1.3, w: 8, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });

  // Three cards
  const cardW = 2.55;
  const cardGap = 0.25;
  const cardStartX = 1.0;
  const cardY = 2.2;
  const cardH = 2.5;

  const cards = [
    { name: "崔桐浩", items: ["数据库设计", "版本演进", "软删除机制"] },
    { name: "马鸣远", items: ["业务逻辑", "状态机设计", "购物车约束"] },
    { name: "王略帆", items: ["数据建模", "编码规范", "DFD设计"] },
  ];

  cards.forEach((c, i) => {
    const cx = cardStartX + i * (cardW + cardGap);
    // Card bg
    slide.addShape("rect", {
      x: cx, y: cardY, w: cardW, h: cardH,
      fill: { color: C.LIGHT_BG },
      rectRadius: 0.1,
    });
    // Name
    slide.addText(c.name, {
      x: cx + 0.2, y: cardY + 0.15, w: cardW - 0.4, h: 0.4,
      fontSize: 18, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
    });
    // Separator
    slide.addShape("rect", {
      x: cx + 0.2, y: cardY + 0.6, w: 0.6, h: 0.015,
      fill: { color: C.ORANGE },
    });
    // Items
    slide.addText(c.items.map((t, j) => ({
      text: t,
      options: { breakLine: j < c.items.length - 1, paraSpaceAfter: 8 },
    })), {
      x: cx + 0.2, y: cardY + 0.8, w: cardW - 0.4, h: 1.4,
      fontSize: 14, fontFace: FONT, color: C.TEXT, margin: 0,
    });
  });
}

// ============== SLIDE 3: TRANSITION - CUI ==============
// ============== SLIDE 4: DB VERSION EVOLUTION ==============
function createDBEvolution(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 4);

  // Title
  slide.addText("数据库三版本安全演进", {
    x: 0.8, y: 0.45, w: 6, h: 0.6,
    fontSize: 30, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });
  slide.addText("真实项目中的数据迁移问题", {
    x: 0.8, y: 1.0, w: 6, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // Left: Two code blocks
  const blockX = 0.8;
  const blockW = 5.5;

  // Code block 1: v1→v2
  slide.addShape("rect", {
    x: blockX, y: 1.55, w: blockW, h: 1.05,
    fill: { color: C.LIGHT_BG },
    rectRadius: 0.06,
  });
  slide.addShape("rect", {
    x: blockX, y: 1.55, w: 0.04, h: 1.05,
    fill: { color: C.ORANGE },
  });
  slide.addText("v1  →  v2", {
    x: blockX + 0.2, y: 1.55, w: 1.5, h: 0.3,
    fontSize: 14, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });
  slide.addText("新增两个字段：营业时间 opening_hours、店铺图片路径 store_image_uri", {
    x: blockX + 0.2, y: 1.85, w: blockW - 0.4, h: 0.65,
    fontSize: 12, fontFace: FONT, color: C.TEXT, margin: 0,
  });

  // Code block 2: v2→v3
  slide.addShape("rect", {
    x: blockX, y: 2.85, w: blockW, h: 1.45,
    fill: { color: C.LIGHT_BG },
    rectRadius: 0.06,
  });
  slide.addShape("rect", {
    x: blockX, y: 2.85, w: 0.04, h: 1.45,
    fill: { color: C.ORANGE },
  });
  slide.addText("v2  →  v3 （四步安全迁移）", {
    x: blockX + 0.2, y: 2.85, w: 3.5, h: 0.3,
    fontSize: 14, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });
  slide.addText([
    { text: "① 重命名旧表", options: { breakLine: true, fontFace: FONT } },
    { text: "② 创建新表（移除 UNIQUE 约束）", options: { breakLine: true, fontFace: FONT } },
    { text: "③ 迁移数据", options: { breakLine: true, fontFace: FONT } },
    { text: "④ 删除旧表", options: { fontFace: FONT } },
  ], {
    x: blockX + 0.2, y: 3.2, w: blockW - 0.4, h: 1.0,
    fontSize: 12, fontFace: FONT, color: C.TEXT, paraSpaceAfter: 4, margin: 0,
  });

  // Right: Version flow
  const vs = [{ label: "v1", subtitle: "基础四表", y: 1.2 }, { label: "v2", subtitle: "+店铺扩展", y: 2.4 }, { label: "v3", subtitle: "软删除支持", y: 3.6 }];
  vs.forEach((v, i) => {
    slide.addShape("rect", {
      x: 7.5, y: v.y, w: 1.3, h: 0.65,
      fill: { color: C.ORANGE },
      rectRadius: 0.06,
    });
    slide.addText(v.label, {
      x: 7.5, y: v.y + 0.02, w: 1.3, h: 0.38,
      fontSize: 18, fontFace: FONT, bold: true, color: C.WHITE, align: "center", valign: "middle", margin: 0,
    });
    slide.addText(v.subtitle, {
      x: 7.5, y: v.y + 0.38, w: 1.3, h: 0.25,
      fontSize: 9, fontFace: FONT, color: C.WHITE, align: "center", margin: 0,
    });
    if (i < vs.length - 1) {
      slide.addShape("rect", {
        x: 8.15, y: v.y + 0.65, w: 0.025, h: 0.55,
        fill: { color: C.GRAY },
      });
    }
  });

  // Bottom note
  slide.addText("★ 为什么移除UNIQUE？ → 支持软删除后用户名回收", {
    x: 0.8, y: 4.5, w: 6, h: 0.35,
    fontSize: 14, fontFace: FONT, italic: true, color: C.ORANGE, margin: 0,
  });
}

// ============== SLIDE 5: SOFT DELETE & USERNAME RECYCLE ==============
function createSoftDelete(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 5);

  slide.addText("软删除 + 用户名回收机制", {
    x: 0.8, y: 0.45, w: 8, h: 0.6,
    fontSize: 30, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });

  // Flow chart
  const boxes = [
    { label: "商家注销", y: 1.6 },
    { label: "status = 2\n(软删除)", y: 1.6 },
    { label: "数据保留\n可追溯", y: 1.6 },
    { label: "用户名释放\n可重新注册", y: 1.6 },
  ];
  const boxW = 1.8;
  const boxH = 1.1;
  const bxStart = 0.8;

  boxes.forEach((b, i) => {
    const bx = bxStart + i * (boxW + 0.15);
    slide.addShape("rect", {
      x: bx, y: b.y, w: boxW, h: boxH,
      fill: { color: C.WHITE },
      line: { color: C.ORANGE, width: 2 },
      rectRadius: 0.08,
    });
    slide.addText(b.label, {
      x: bx, y: b.y, w: boxW, h: boxH,
      fontSize: 13, fontFace: FONT, color: C.TEXT, align: "center", valign: "middle", margin: 0,
    });
    if (i < boxes.length - 1) {
      slide.addShape("rect", {
        x: bx + boxW, y: b.y + boxH / 2 - 0.01, w: 0.15, h: 0.025,
        fill: { color: C.TEXT },
      });
    }
  });

  // Three rules
  const rules = [
    { code: "登录查询时自动过滤已删除用户", desc: "已删除用户无法登录" },
    { code: "商品列表查询时跳过已删除商家", desc: "商品自动对买家隐藏" },
    { code: "注册校验时排除已删除用户", desc: "用户名可被新用户注册" },
  ];

  rules.forEach((r, i) => {
    const ry = 3.05 + i * 0.6;
    // Badge dot
    slide.addShape("ellipse", {
      x: 0.8, y: ry + 0.1, w: 0.15, h: 0.15,
      fill: { color: C.ORANGE },
    });
    // Code
    slide.addText(r.code, {
      x: 1.1, y: ry, w: 4.5, h: 0.35,
      fontSize: 12, fontFace: FONT, color: C.TEXT, margin: 0,
    });
    // Desc
    slide.addText(r.desc, {
      x: 5.5, y: ry, w: 3.5, h: 0.35,
      fontSize: 13, fontFace: FONT, color: C.GRAY, margin: 0,
    });
  });
}

// ============== SLIDE 6: FEASIBILITY ANALYSIS ==============
function createFeasibility(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 6);

  slide.addText("三维度可行性分析", {
    x: 0.8, y: 0.4, w: 6, h: 0.6,
    fontSize: 30, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });
  slide.addText("技术 · 经济 · 操作 — 三个维度均给出\"完全可行\"的核心判断", {
    x: 0.8, y: 0.95, w: 8, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  const cards = [
    {
      title: "技术可行性",
      check: "完全可行",
      items: [
        "Android + Java 全开源技术栈，生态成熟稳定",
        "SQLite 嵌入式数据库，无需独立服务器部署",
        "MVC 分层架构，三层职责清晰分离",
        "兼容 Android 5.0 ~ 13，覆盖绝大多数设备",
      ],
    },
    {
      title: "经济可行性",
      check: "完全可行",
      items: [
        "全技术栈零商业授权，无付费第三方依赖",
        "纯本地运行架构，无需配置后端服务器",
        "开发投入仅为三人10个工作日时间成本",
        "零运维成本，应用可直接安装使用",
      ],
    },
    {
      title: "操作可行性",
      check: "完全可行",
      items: [
        "遵循 Material Design 设计规范",
        "交互模式借鉴主流外卖应用通用范式",
        "三类用户独立界面，角色互不干扰",
        "同步提示 + 异步广播双通道反馈机制",
      ],
    },
  ];

  cards.forEach((c, i) => {
    const cx = 0.4 + i * 3.1;
    const cy = 1.5;
    // Card bg
    slide.addShape("rect", {
      x: cx, y: cy, w: 2.9, h: 3.1,
      fill: { color: C.LIGHT_BG },
      rectRadius: 0.08,
    });
    // Title
    slide.addText(c.title, {
      x: cx + 0.15, y: cy + 0.12, w: 2.6, h: 0.35,
      fontSize: 16, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
    });
    // Check badge
    slide.addShape("rect", {
      x: cx + 0.15, y: cy + 0.52, w: 1.2, h: 0.3,
      fill: { color: C.GREEN },
      rectRadius: 0.04,
    });
    slide.addText("✓ " + c.check, {
      x: cx + 0.15, y: cy + 0.54, w: 1.2, h: 0.26,
      fontSize: 10, fontFace: FONT, bold: true, color: C.WHITE, align: "center", valign: "middle", margin: 0,
    });
    // Items
    slide.addText(c.items.map((item, j) => ({
      text: "●  " + item,
      options: { breakLine: j < c.items.length - 1, paraSpaceAfter: 8 },
    })), {
      x: cx + 0.15, y: cy + 1.0, w: 2.6, h: 1.9,
      fontSize: 10, fontFace: FONT, color: C.TEXT, margin: 0,
    });
  });

  slide.addText("以上分析为项目启动阶段的核心决策依据，确立了\"全开源 · 零成本 · 纯本地\"的技术路线", {
    x: 0.8, y: 4.85, w: 8.5, h: 0.25,
    fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0,
  });
}

// ============== SLIDE 7: PROJECT PLAN & BUSINESS RULES ==============
function createProjectPlan(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 7);

  slide.addText("项目计划与核心业务规则", {
    x: 0.8, y: 0.4, w: 6, h: 0.5,
    fontSize: 28, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });

  // Left: Project plan timeline
  slide.addText("项目实施阶段（瀑布模型，两周六阶段）", {
    x: 0.8, y: 1.1, w: 5, h: 0.3,
    fontSize: 13, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });

  const stages = [
    { phase: "1", date: "6.22-23", task: "可行性分析 + 项目计划", person: "崔桐浩" },
    { phase: "2", date: "6.24-25", task: "需求分析 + 业务建模", person: "马鸣远" },
    { phase: "3", date: "6.26/29", task: "数据流图 + 数据字典", person: "王略帆" },
    { phase: "4", date: "6.30-7.1", task: "概要设计 + 详细设计", person: "马鸣远 / 王略帆" },
    { phase: "5", date: "7.2-3", task: "数据库设计 + 编码实现", person: "崔桐浩 / 马鸣远" },
    { phase: "6", date: "7.3", task: "报告撰写 + 答辩准备", person: "崔桐浩" },
  ];

  stages.forEach((st, i) => {
    const sy = 1.5 + i * 0.38;
    // Phase number circle
    slide.addShape("ellipse", { x: 0.8, y: sy + 0.04, w: 0.28, h: 0.28, fill: { color: C.ORANGE } });
    slide.addText(st.phase, { x: 0.8, y: sy + 0.04, w: 0.28, h: 0.28, fontSize: 10, fontFace: FONT, bold: true, color: C.WHITE, align: "center", valign: "middle", margin: 0 });
    // Date
    slide.addText(st.date, { x: 1.2, y: sy, w: 0.9, h: 0.35, fontSize: 9, fontFace: FONT, color: C.GRAY, valign: "middle", margin: 0 });
    // Task
    slide.addText(st.task, { x: 2.15, y: sy, w: 2.3, h: 0.35, fontSize: 11, fontFace: FONT, color: C.TEXT, valign: "middle", margin: 0 });
    // Person
    slide.addText(st.person, { x: 4.5, y: sy, w: 1.5, h: 0.35, fontSize: 10, fontFace: FONT, color: C.GRAY, valign: "middle", margin: 0 });
    // Connector line
    if (i < stages.length - 1) {
      slide.addShape("rect", { x: 0.93, y: sy + 0.33, w: 0.025, h: 0.25, fill: { color: C.GRAY } });
    }
  });

  // Right: Business rules
  slide.addShape("rect", { x: 6.1, y: 1.0, w: 0.015, h: 3.5, fill: { color: C.GRAY } });

  slide.addText("七条核心业务规则", {
    x: 6.4, y: 1.1, w: 3.2, h: 0.3,
    fontSize: 13, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });
  slide.addText("（从代码逆向还原）", {
    x: 6.4, y: 1.35, w: 3.2, h: 0.2,
    fontSize: 9, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  const rules = [
    "商品列表只显示正常商家在售商品",
    "购物车一次只能买同一商家商品",
    "订单状态按主线单向流转",
    "封禁商家拒绝登录",
    "已删除数据可追溯且用户名可回收",
    "用户名对未删除用户不可重复",
    "图片存本地文件，数据库仅存路径",
  ];

  rules.forEach((r, i) => {
    const ry = 1.75 + i * 0.38;
    slide.addText((i + 1) + ". " + r, {
      x: 6.4, y: ry, w: 3.2, h: 0.35,
      fontSize: 10, fontFace: FONT, color: C.TEXT, valign: "middle", margin: 0,
    });
  });

  slide.addText("每一条规则都源自源码中 SQL 条件、if 判断和字段赋值的逆向分析", {
    x: 0.8, y: 4.85, w: 8, h: 0.25,
    fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0,
  });
}

// ============== SLIDE 8: ER DIAGRAM (FULL PAGE) ==============
function createERDiagram(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 8);

  slide.addText("概念结构设计", {
    x: 0.8, y: 0.35, w: 5, h: 0.5,
    fontSize: 20, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });

  // Left labels
  const labels = [
    "4个核心实体",
    "4组 1:N 关系",
    "单表三角色（role字段区分）",
    "外键通过业务SQL逆向还原",
  ];
  slide.addText(labels.map((l, i) => ({
    text: "●  " + l,
    options: { breakLine: i < labels.length - 1, paraSpaceAfter: 6 },
  })), {
    x: 0.8, y: 1.0, w: 2.2, h: 2.0,
    fontSize: 12, fontFace: FONT, color: C.TEXT, margin: 0,
  });

  // ER diagram full page
  slide.addImage({
    path: IMG("cui2/media/image2.jpeg"),
    x: 3.3, y: 0.8, w: 6.3, h: 4.2,
    sizing: { type: "contain", w: 6.3, h: 4.2 },
  });
  slide.addText("图：系统数据库 E-R 图", {
    x: 3.3, y: 5.0, w: 6.3, h: 0.2,
    fontSize: 11, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });
}

// ============== SLIDE 7: TRANSITION - MA ==============
// ============== SLIDE 8: ORDER STATE MACHINE ==============
function createStateMachine(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 10);

  slide.addText("订单五状态机", {
    x: 0.8, y: 0.45, w: 5, h: 0.6,
    fontSize: 30, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });
  slide.addText("5个状态节点 · 4条转换路径", {
    x: 0.8, y: 1.0, w: 5, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // State nodes
  const nodeW = 1.35;
  const nodeH = 0.75;
  const nodes = [
    { label: "paid", sub: "已支付", x: 0.6, y: 1.7, fill: C.LIGHT_BG },
    { label: "accepted", sub: "已接单", x: 2.3, y: 1.7, fill: C.LIGHT_BG },
    { label: "delivering", sub: "配送中", x: 4.0, y: 1.7, fill: C.LIGHT_BG },
    { label: "completed", sub: "已完成 ✓", x: 5.7, y: 1.7, fill: C.GREEN },
    { label: "canceled", sub: "已取消 ✗", x: 0.6, y: 3.1, fill: C.RED },
  ];

  nodes.forEach((n) => {
    const isTerminal = n.label === "completed" || n.label === "canceled";
    slide.addShape("rect", {
      x: n.x, y: n.y, w: nodeW, h: nodeH,
      fill: { color: n.fill },
      line: { color: isTerminal ? n.fill : C.TEXT, width: isTerminal ? 0 : 1.5 },
      rectRadius: 0.06,
    });
    slide.addText(n.label, {
      x: n.x, y: n.y + 0.05, w: nodeW, h: 0.4,
      fontSize: 15, fontFace: FONT, bold: true, color: isTerminal ? C.WHITE : C.TEXT, align: "center", valign: "middle", margin: 0,
    });
    slide.addText(n.sub, {
      x: n.x, y: n.y + 0.42, w: nodeW, h: 0.28,
      fontSize: 9, fontFace: FONT, color: isTerminal ? C.WHITE : C.GRAY, align: "center", margin: 0,
    });
  });

  // Arrows
  const arrows = [
    { x: nodes[0].x + nodeW, y: nodes[0].y + nodeH / 2, w: 0.35, label: "商家接单", color: C.ORANGE },
    { x: nodes[1].x + nodeW, y: nodes[1].y + nodeH / 2, w: 0.35, label: "商家配送", color: C.ORANGE },
    { x: nodes[2].x + nodeW, y: nodes[2].y + nodeH / 2, w: 0.35, label: "买家确认", color: C.ORANGE },
  ];
  arrows.forEach((a) => {
    slide.addShape("rect", {
      x: a.x, y: a.y - 0.01, w: a.w, h: 0.025,
      fill: { color: C.TEXT },
    });
    slide.addText(a.label, {
      x: a.x - 0.05, y: a.y - 0.35, w: a.w + 0.1, h: 0.3,
      fontSize: 9, fontFace: FONT, color: a.color, align: "center", margin: 0,
    });
  });

  // Cancel arrow (down)
  slide.addShape("rect", {
    x: nodes[0].x + nodeW / 2, y: nodes[0].y + nodeH, w: 0.025, h: 0.55,
    fill: { color: C.TEXT },
  });
  slide.addText("买家取消", {
    x: nodes[0].x + nodeW / 2 + 0.08, y: nodes[0].y + nodeH + 0.05, w: 1.0, h: 0.25,
    fontSize: 9, fontFace: FONT, color: C.ORANGE, margin: 0,
  });

  // Bottom notes
  slide.addText("状态更新通过统一的状态更新方法实现，确保原子性操作", {
    x: 0.8, y: 4.2, w: 5, h: 0.25,
    fontSize: 12, fontFace: FONT, color: C.GRAY, margin: 0,
  });
  slide.addText("订单列表根据角色和状态动态显示对应的操作按钮（接单/配送/确认收货/取消）", {
    x: 0.8, y: 4.5, w: 8, h: 0.25,
    fontSize: 12, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // Right: use case image
  slide.addImage({
    path: IMG("cui2/media/image1.jpeg"),
    x: 6.2, y: 3.5, w: 3.5, h: 1.6,
    sizing: { type: "contain", w: 3.5, h: 1.6 },
  });
  slide.addText("用例图", {
    x: 6.2, y: 5.05, w: 3.5, h: 0.15,
    fontSize: 9, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });
}

// ============== SLIDE 9: CART CONSTRAINT ==============
function createCartConstraint(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 11);

  slide.addText("同商家购物车约束", {
    x: 0.8, y: 0.45, w: 6, h: 0.6,
    fontSize: 28, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });

  // Left: Flow
  const steps = [
    { num: "①", label: "加购新商品", code: "" },
    { num: "②", label: "获取当前购物车商家编号", code: "与购物车中已有商品的商家对比" },
    { num: "③", label: "与新商品所属商家比对", code: "" },
  ];

  steps.forEach((s, i) => {
    const sy = 1.5 + i * 0.75;
    // Circle
    slide.addShape("ellipse", {
      x: 0.8, y: sy, w: 0.35, h: 0.35,
      fill: { color: C.ORANGE },
    });
    slide.addText(s.num, {
      x: 0.8, y: sy, w: 0.35, h: 0.35,
      fontSize: 12, fontFace: FONT, bold: true, color: C.WHITE, align: "center", valign: "middle", margin: 0,
    });
    slide.addText(s.label, {
      x: 1.3, y: sy + 0.02, w: 4, h: 0.3,
      fontSize: 14, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
    });
    if (s.code) {
      slide.addText(s.code, {
        x: 1.3, y: sy + 0.32, w: 4, h: 0.25,
        fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0,
      });
    }
    if (i < steps.length - 1) {
      slide.addShape("rect", {
        x: 0.96, y: sy + 0.35, w: 0.025, h: 0.4,
        fill: { color: C.GRAY },
      });
    }
  });

  // Branch results
  slide.addText("一致 → 加入成功  ✓", {
    x: 0.8, y: 3.8, w: 3, h: 0.35,
    fontSize: 14, fontFace: FONT, color: C.GREEN, margin: 0,
  });
  slide.addText("不一致 → 弹窗提示阻断  ✗", {
    x: 0.8, y: 4.15, w: 3, h: 0.35,
    fontSize: 14, fontFace: FONT, color: C.RED, margin: 0,
  });

  // Right: Cart screenshot + Function structure image
  slide.addImage({
    path: SS("screenshot_cart.png"),
    x: 5.3, y: 1.2, w: 2.1, h: 1.65,
    sizing: { type: "contain", w: 2.1, h: 1.65 },
  });
  slide.addText("购物车实机截图", {
    x: 5.3, y: 2.82, w: 2.1, h: 0.2,
    fontSize: 9, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });
  slide.addImage({
    path: IMG("ma2/media/image5.jpeg"),
    x: 7.55, y: 1.2, w: 2.15, h: 3.2,
    sizing: { type: "contain", w: 2.15, h: 3.2 },
  });
  slide.addText("图：系统功能结构图（5大模块22个功能）", {
    x: 7.55, y: 4.45, w: 2.15, h: 0.2,
    fontSize: 9, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });

  // Summary below
  slide.addShape("rect", {
    x: 0.8, y: 4.75, w: 4.2, h: 0.025,
    fill: { color: C.ORANGE },
  });
  slide.addText("购物车采用全局唯一实例管理 — 结算前进行购物车非空和商家有效性双重校验", {
    x: 0.8, y: 4.85, w: 8.5, h: 0.25,
    fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0,
  });
}

const SS = (p) => path.join(__dirname, "app_screenshots", p);

// ============== FLOW SLIDE HELPER: image + text + screenshot ==============
function createFlowSlideWithScreenshot(pres, pageNum, title, subtitle, flowImgPath, ssPath, textLines) {
  const s = pres.addSlide();
  s.background = { color: C.WHITE };
  addFrame(s, pageNum);

  s.addText(title, { x: 0.8, y: 0.3, w: 6, h: 0.4, fontSize: 22, fontFace: FONT, bold: true, color: C.TEXT, margin: 0 });
  s.addText(subtitle, { x: 0.8, y: 0.65, w: 7, h: 0.25, fontSize: 12, fontFace: FONT, color: C.GRAY, margin: 0 });

  // Flow diagram image - left side, contained to keep aspect ratio
  s.addImage({
    path: flowImgPath,
    x: 0.5, y: 1.05, w: 6.2, h: 3.9,
    sizing: { type: "contain", w: 6.2, h: 3.9 },
  });

  // Vertical separator
  s.addShape("rect", { x: 6.9, y: 1.1, w: 0.015, h: 3.8, fill: { color: C.GRAY } });

  // Right side: text explanation
  s.addText("流程说明", {
    x: 7.1, y: 1.1, w: 2.3, h: 0.3,
    fontSize: 13, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });
  s.addText(textLines, {
    x: 7.1, y: 1.4, w: 2.3, h: 1.6,
    fontSize: 10, fontFace: FONT, color: C.TEXT, paraSpaceAfter: 6, margin: 0,
  });

  // App screenshot
  if (ssPath) {
    s.addText("实机展示", {
      x: 7.1, y: 3.15, w: 2.3, h: 0.25,
      fontSize: 13, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
    });
    s.addImage({
      path: SS(ssPath),
      x: 7.1, y: 3.42, w: 2.3, h: 1.55,
      sizing: { type: "contain", w: 2.3, h: 1.55 },
    });
  }
}

// ============== SLIDE: I/O DESIGN ==============
function createIODesign(pres, pageNum) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, pageNum);

  slide.addText("输入输出设计", {
    x: 0.8, y: 0.4, w: 6, h: 0.5,
    fontSize: 28, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });
  slide.addText("覆盖登录、注册、商品维护、店铺维护、地址管理、购物车下单、管理员操作七个场景", {
    x: 0.8, y: 0.85, w: 8.5, h: 0.25,
    fontSize: 12, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // Left: Input design
  slide.addText("输入设计", {
    x: 0.8, y: 1.25, w: 4, h: 0.3,
    fontSize: 16, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });

  const inputItems = [
    { scene: "登录", fields: "用户名、密码", rule: "非空校验 + 账号存在性与状态校验" },
    { scene: "注册", fields: "用户名、密码、角色；商家还需店铺名、地址、电话等", rule: "用户名对未删除用户不可重复" },
    { scene: "商品维护", fields: "名称、价格（必填）；描述、分类、图片可选", rule: "名称和价格为空时拒绝提交" },
    { scene: "店铺维护", fields: "店铺名（必填）；地址、电话、营业时间、图片", rule: "店铺名必填校验" },
    { scene: "地址管理", fields: "地址文本", rule: "地址非空校验" },
    { scene: "购物车/下单", fields: "商品条目、数量、收货地址", rule: "购物车非空 + 商家有效性校验" },
    { scene: "管理员操作", fields: "选择商家 + 操作类型（封禁/解封）", rule: "已注销商家不可操作" },
  ];

  inputItems.forEach((item, i) => {
    const iy = 1.65 + i * 0.4;
    slide.addText((i + 1) + ". " + item.scene, {
      x: 0.95, y: iy, w: 0.8, h: 0.35,
      fontSize: 11, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
    });
    slide.addText(item.fields, {
      x: 1.8, y: iy, w: 2.2, h: 0.35,
      fontSize: 10, fontFace: FONT, color: C.GRAY, margin: 0,
    });
    slide.addText(item.rule, {
      x: 4.05, y: iy, w: 2.5, h: 0.35,
      fontSize: 10, fontFace: FONT, color: C.TEXT, margin: 0,
    });
  });

  // Vertical separator
  slide.addShape("rect", { x: 6.7, y: 1.25, w: 0.015, h: 3.2, fill: { color: C.GRAY } });

  // Right: Output design
  slide.addText("输出设计", {
    x: 6.95, y: 1.25, w: 2.8, h: 0.3,
    fontSize: 16, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });

  const outputItems = [
    { scene: "登录/注册反馈", desc: "成功→按角色跳转对应主页；失败→提示原因" },
    { scene: "买家商品列表", desc: "图文列表展示商品，支持输入框实时搜索过滤" },
    { scene: "商品详情/购物车", desc: "大图详情展示；购物车支持数量调节和实时总价计算" },
    { scene: "订单中心", desc: "列表展示订单，根据角色和状态动态显示操作按钮" },
    { scene: "商家首页", desc: "商品列表含状态标签；点击编辑；快捷新增入口" },
    { scene: "管理员界面", desc: "商家列表展示；点击弹出封禁/解封菜单" },
    { scene: "本地通知/存储", desc: "下单成功→广播通知；图片存本地文件目录" },
  ];

  outputItems.forEach((item, i) => {
    const oy = 1.65 + i * 0.4;
    slide.addText((i + 1) + ". " + item.scene, {
      x: 6.95, y: oy, w: 1.3, h: 0.35,
      fontSize: 11, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
    });
    slide.addText(item.desc, {
      x: 8.3, y: oy, w: 1.5, h: 0.35,
      fontSize: 10, fontFace: FONT, color: C.GRAY, margin: 0,
    });
  });

  slide.addText("每种控件的选择都有交互频率和视觉层次的考量——例如购物车用悬浮按钮降低操作路径", {
    x: 0.8, y: 4.85, w: 8.5, h: 0.2,
    fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0,
  });
}

// ============== SLIDE: DATA DICTIONARY OVERVIEW ==============
function createDataDict(pres, pageNum) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, pageNum);

  slide.addText("数据字典概览", {
    x: 0.8, y: 0.35, w: 5, h: 0.5,
    fontSize: 28, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });
  slide.addText("四张核心数据表 · 28个字段 · 完整约束与业务含义标注", {
    x: 0.8, y: 0.75, w: 8, h: 0.25,
    fontSize: 12, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // Four tables in 2x2 grid, compact
  const tblW = 4.2;
  const tblH = 1.6;
  const tblGapY = 0.25;

  const dicts = [
    {
      title: "users 表（10字段）",
      x: 0.5, y: 1.15,
      rows: [
        [{ text: "字段", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "类型", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "含义", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } }],
        [{ text: "id", options: { fontSize: 8 } }, { text: "INTEGER PK", options: { fontSize: 8 } }, { text: "用户编号，自增主键", options: { fontSize: 8 } }],
        [{ text: "username", options: { fontSize: 8 } }, { text: "TEXT", options: { fontSize: 8 } }, { text: "登录名（业务唯一）", options: { fontSize: 8 } }],
        [{ text: "role", options: { fontSize: 8 } }, { text: "TEXT", options: { fontSize: 8 } }, { text: "admin/merchant/buyer", options: { fontSize: 8 } }],
        [{ text: "status", options: { fontSize: 8 } }, { text: "INTEGER", options: { fontSize: 8 } }, { text: "1正常 / 0封禁 / 2已删除", options: { fontSize: 8 } }],
        [{ text: "store_name", options: { fontSize: 8 } }, { text: "TEXT", options: { fontSize: 8 } }, { text: "商家店铺名称", options: { fontSize: 8 } }],
      ],
    },
    {
      title: "products 表（8字段）",
      x: 5.3, y: 1.15,
      rows: [
        [{ text: "字段", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "类型", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "含义", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } }],
        [{ text: "id", options: { fontSize: 8 } }, { text: "INTEGER PK", options: { fontSize: 8 } }, { text: "商品编号，自增主键", options: { fontSize: 8 } }],
        [{ text: "merchant_id", options: { fontSize: 8 } }, { text: "INTEGER", options: { fontSize: 8 } }, { text: "所属商家编号", options: { fontSize: 8 } }],
        [{ text: "name", options: { fontSize: 8 } }, { text: "TEXT", options: { fontSize: 8 } }, { text: "商品名称（必填）", options: { fontSize: 8 } }],
        [{ text: "price", options: { fontSize: 8 } }, { text: "REAL", options: { fontSize: 8 } }, { text: "商品价格（必填）", options: { fontSize: 8 } }],
        [{ text: "status", options: { fontSize: 8 } }, { text: "INTEGER", options: { fontSize: 8 } }, { text: "1上架 / 0下架", options: { fontSize: 8 } }],
      ],
    },
    {
      title: "orders 表（7字段）",
      x: 0.5, y: 1.15 + tblH + tblGapY,
      rows: [
        [{ text: "字段", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "类型", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "含义", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } }],
        [{ text: "id", options: { fontSize: 8 } }, { text: "INTEGER PK", options: { fontSize: 8 } }, { text: "订单编号，自增主键", options: { fontSize: 8 } }],
        [{ text: "buyer_id", options: { fontSize: 8 } }, { text: "INTEGER", options: { fontSize: 8 } }, { text: "下单买家编号", options: { fontSize: 8 } }],
        [{ text: "merchant_id", options: { fontSize: 8 } }, { text: "INTEGER", options: { fontSize: 8 } }, { text: "接单商家编号", options: { fontSize: 8 } }],
        [{ text: "total_price", options: { fontSize: 8 } }, { text: "REAL", options: { fontSize: 8 } }, { text: "订单总金额", options: { fontSize: 8 } }],
        [{ text: "status", options: { fontSize: 8 } }, { text: "TEXT", options: { fontSize: 8 } }, { text: "paid/accepted/delivering/completed/canceled", options: { fontSize: 8 } }],
      ],
    },
    {
      title: "addresses 表（3字段）",
      x: 5.3, y: 1.15 + tblH + tblGapY,
      rows: [
        [{ text: "字段", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "类型", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } },
         { text: "含义", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 9 } }],
        [{ text: "_id", options: { fontSize: 8 } }, { text: "INTEGER PK", options: { fontSize: 8 } }, { text: "地址编号，自增主键", options: { fontSize: 8 } }],
        [{ text: "user_id", options: { fontSize: 8 } }, { text: "INTEGER", options: { fontSize: 8 } }, { text: "所属用户编号（NOT NULL）", options: { fontSize: 8 } }],
        [{ text: "detail", options: { fontSize: 8 } }, { text: "TEXT", options: { fontSize: 8 } }, { text: "收货地址详细描述（NOT NULL）", options: { fontSize: 8 } }],
      ],
    },
  ];

  dicts.forEach((dt) => {
    slide.addText(dt.title, {
      x: dt.x, y: dt.y - 0.22, w: tblW, h: 0.2,
      fontSize: 12, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
    });
    const colCount = dt.rows[0].length;
    const colW = [1.1, 1.1, 2.0];
    slide.addTable(dt.rows, {
      x: dt.x, y: dt.y, w: tblW,
      colW: colW,
      border: { pt: 0.5, color: C.GRAY },
      rowH: dt.rows.map(() => 0.2),
      margin: [1, 3, 1, 3],
    });
  });

  slide.addText(
    "除数据库持久化外，还补充编写了运行期临时数据字典——登录会话中的5个键值、购物车内存映射结构、以及图片文件存储路径规则",
    { x: 0.8, y: 4.65, w: 8.5, h: 0.25, fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0 }
  );
}

// ============== SLIDE 11: TRANSITION - WANG (now slide 14) ==============
// ============== SLIDE 12: DFD + D5 (now slide 15) ==============
function createDFDAndD5(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 17);

  slide.addText("数据流图与复合型 D5 设计", {
    x: 0.8, y: 0.35, w: 7, h: 0.5,
    fontSize: 28, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });
  // Badge
  slide.addShape("rect", {
    x: 7.0, y: 0.4, w: 2.5, h: 0.3,
    fill: { color: C.LIGHT_BG },
    rectRadius: 0.04,
  });
  slide.addText("3外部实体 · 6处理 · 5存储", {
    x: 7.0, y: 0.42, w: 2.5, h: 0.26,
    fontSize: 10, fontFace: FONT, color: C.GRAY, align: "center", valign: "middle", margin: 0,
  });

  // DFD Image
  slide.addImage({
    path: IMG("wang2/media/image1.jpeg"),
    x: 0.5, y: 0.85, w: 9.0, h: 2.5,
    sizing: { type: "contain", w: 9.0, h: 2.5 },
  });
  slide.addText("图：系统数据流图（DFD）", {
    x: 3, y: 3.35, w: 4, h: 0.2,
    fontSize: 10, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });

  // D5 Table
  const d5Table = [
    [
      { text: "存储类型", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 12 } },
      { text: "生命周期", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 12 } },
      { text: "数据内容", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 12 } },
    ],
    [
      { text: "SharedPreferences", options: { fontSize: 12, fontFace: FONT } },
      { text: "退出登录时清空", options: { fontSize: 12 } },
      { text: "user_id, role, username 等5键值", options: { fontSize: 12 } },
    ],
    [
      { text: "CartManager", options: { fontSize: 12, fontFace: FONT } },
      { text: "进程退出时清空", options: { fontSize: 12 } },
      { text: "Product → Quantity 映射", options: { fontSize: 12 } },
    ],
    [
      { text: "Internal Files", options: { fontSize: 12, fontFace: FONT } },
      { text: "永久保存", options: { fontSize: 12 } },
      { text: "商品/店铺图片文件", options: { fontSize: 12 } },
    ],
  ];
  slide.addTable(d5Table, {
    x: 1.5, y: 3.65, w: 7.0,
    colW: [2.3, 2.0, 2.7],
    border: { pt: 1.5, color: C.TEXT },
    rowH: [0.32, 0.32, 0.32, 0.32],
    margin: [3, 8, 3, 8],
  });

  slide.addText("★ 不标注 D5，DFD 无法完整反映系统全部数据形态", {
    x: 0.8, y: 5.0, w: 8, h: 0.2,
    fontSize: 12, fontFace: FONT, italic: true, color: C.ORANGE, margin: 0,
  });
}

// ============== SLIDE 13: CODING SYSTEM (now slide 16) ==============
function createCodingSystem(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 18);

  slide.addText("信息分类编码设计", {
    x: 0.8, y: 0.35, w: 5, h: 0.5,
    fontSize: 28, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
  });
  slide.addText("四套编码 · 13个值 · 三条原则", {
    x: 0.8, y: 0.8, w: 5, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.GRAY, margin: 0,
  });

  // Left: Three principles
  const principles = [
    { title: "原则一", main: "英文枚举语义化", code: '用 "已支付" 一目了然，比用数字1 更直观' },
    { title: "原则二", main: "整数单向唯一", code: "0 = 否定  1 = 肯定  2 = 软删除" },
    { title: "原则三", main: "编码即业务节点", code: "编码值 = 外卖流程关键阶段" },
  ];

  principles.forEach((p, i) => {
    const py = 1.4 + i * 1.15;
    slide.addShape("rect", {
      x: 0.8, y: py, w: 3.5, h: 0.95,
      fill: { color: C.LIGHT_BG },
      rectRadius: 0.06,
    });
    slide.addShape("rect", {
      x: 0.8, y: py, w: 0.04, h: 0.95,
      fill: { color: C.ORANGE },
    });
    slide.addText(p.title, {
      x: 1.0, y: py + 0.05, w: 3, h: 0.22,
      fontSize: 11, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
    });
    slide.addText(p.main, {
      x: 1.0, y: py + 0.28, w: 3, h: 0.3,
      fontSize: 14, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
    });
    slide.addText(p.code, {
      x: 1.0, y: py + 0.6, w: 3, h: 0.25,
      fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0,
    });
  });

  // Right: Order status table
  slide.addText('订单状态编码表（"一表双用"）', {
    x: 4.7, y: 1.4, w: 4.5, h: 0.35,
    fontSize: 14, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
  });

  const orderTable = [
    [
      { text: "编码值", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 10 } },
      { text: "含义", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 10 } },
      { text: "下一状态", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 10 } },
      { text: "操作角色", options: { bold: true, color: C.WHITE, fill: { color: C.ORANGE }, fontSize: 10 } },
    ],
    [
      { text: "paid", options: { fontFace: FONT, fontSize: 10 } },
      { text: "待接单", options: { fontSize: 10 } },
      { text: "accepted / canceled", options: { fontFace: FONT, fontSize: 9 } },
      { text: "商家 / 买家", options: { fontSize: 10 } },
    ],
    [
      { text: "accepted", options: { fontFace: FONT, fontSize: 10 } },
      { text: "已接单", options: { fontSize: 10 } },
      { text: "delivering", options: { fontFace: FONT, fontSize: 9 } },
      { text: "商家", options: { fontSize: 10 } },
    ],
    [
      { text: "delivering", options: { fontFace: FONT, fontSize: 10 } },
      { text: "配送中", options: { fontSize: 10 } },
      { text: "completed", options: { fontFace: FONT, fontSize: 9 } },
      { text: "买家", options: { fontSize: 10 } },
    ],
    [
      { text: "completed", options: { fontFace: FONT, fontSize: 10, color: C.GRAY } },
      { text: "已完成", options: { fontSize: 10, color: C.GRAY } },
      { text: "—", options: { fontSize: 9, color: C.GRAY } },
      { text: "—", options: { fontSize: 10, color: C.GRAY } },
    ],
    [
      { text: "canceled", options: { fontFace: FONT, fontSize: 10, color: C.GRAY } },
      { text: "已取消", options: { fontSize: 10, color: C.GRAY } },
      { text: "—", options: { fontSize: 9, color: C.GRAY } },
      { text: "—", options: { fontSize: 10, color: C.GRAY } },
    ],
  ];
  slide.addTable(orderTable, {
    x: 4.7, y: 1.8, w: 4.6,
    colW: [1.1, 0.9, 1.5, 1.1],
    border: { pt: 1, color: C.TEXT },
    rowH: [0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
    margin: [2, 5, 2, 5],
  });

  slide.addText("一表双用：编码含义 + 状态机转换路径", {
    x: 4.7, y: 3.55, w: 4.6, h: 0.2,
    fontSize: 11, fontFace: FONT, color: C.ORANGE, align: "right", margin: 0,
  });

  // Other coding tables (compact)
  const smallTables = [
    { title: "用户角色编码", rows: [
      [{ text: "admin", options: { fontFace: FONT, fontSize: 9 } }, { text: "管理员", options: { fontSize: 9 } }],
      [{ text: "merchant", options: { fontFace: FONT, fontSize: 9 } }, { text: "商家", options: { fontSize: 9 } }],
      [{ text: "buyer", options: { fontFace: FONT, fontSize: 9 } }, { text: "买家", options: { fontSize: 9 } }],
    ]},
    { title: "账号状态编码", rows: [
      [{ text: "1", options: { fontFace: FONT, fontSize: 9 } }, { text: "正常", options: { fontSize: 9 } }],
      [{ text: "0", options: { fontFace: FONT, fontSize: 9 } }, { text: "封禁", options: { fontSize: 9 } }],
      [{ text: "2", options: { fontFace: FONT, fontSize: 9 } }, { text: "已删除", options: { fontSize: 9 } }],
    ]},
    { title: "商品状态编码", rows: [
      [{ text: "1", options: { fontFace: FONT, fontSize: 9 } }, { text: "上架", options: { fontSize: 9 } }],
      [{ text: "0", options: { fontFace: FONT, fontSize: 9 } }, { text: "下架", options: { fontSize: 9 } }],
    ]},
  ];

  smallTables.forEach((st, i) => {
    const tx = 0.8 + i * 1.4;
    slide.addText(st.title, {
      x: tx, y: 4.05, w: 1.3, h: 0.22,
      fontSize: 10, fontFace: FONT, bold: true, color: C.TEXT, margin: 0,
    });
    slide.addTable(st.rows, {
      x: tx, y: 4.25, w: 1.3,
      colW: [0.7, 0.6],
      border: { pt: 0.5, color: C.GRAY },
      rowH: [0.2, 0.2, 0.2],
      margin: [1, 3, 1, 3],
    });
  });

  slide.addText("共计4套编码体系 · 13个编码值 · 覆盖系统全部状态标识", {
    x: 0.8, y: 5.0, w: 8, h: 0.2,
    fontSize: 11, fontFace: FONT, color: C.GRAY, margin: 0,
  });
}

// ============== SLIDE 14: SUMMARY (now slide 17) ==============
function createSummary(pres) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  addFrame(slide, 19);

  slide.addText("项目核心创新", {
    x: 1, y: 0.45, w: 8, h: 0.6,
    fontSize: 30, fontFace: FONT, bold: true, color: C.TEXT, align: "center", margin: 0,
  });

  // 2x3 grid of innovation cards
  const cards = [
    { num: "01", text: "数据库\n三版本演进" },
    { num: "02", text: "软删除 +\n用户名回收" },
    { num: "03", text: "五状态\n订单状态机" },
    { num: "04", text: "同商家\n购物车约束" },
    { num: "05", text: "复合型D5\n存储建模" },
    { num: "06", text: "英文枚举\n编码体系" },
  ];

  const cardW = 2.6;
  const cardH = 1.25;
  const gapX = 0.25;
  const gapY = 0.2;
  const gridX = 1.0;
  const gridY = 1.3;

  cards.forEach((c, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const cx = gridX + col * (cardW + gapX);
    const cy = gridY + row * (cardH + gapY);

    slide.addShape("rect", {
      x: cx, y: cy, w: cardW, h: cardH,
      fill: { color: C.LIGHT_BG },
      rectRadius: 0.08,
    });
    slide.addText(c.num, {
      x: cx + 0.15, y: cy + 0.1, w: cardW - 0.3, h: 0.5,
      fontSize: 24, fontFace: FONT, bold: true, color: C.ORANGE, margin: 0,
    });
    slide.addText(c.text, {
      x: cx + 0.15, y: cy + 0.6, w: cardW - 0.3, h: 0.55,
      fontSize: 13, fontFace: FONT, color: C.TEXT, margin: 0,
    });
  });

  // Closing
  // Two app detail screenshots
  slide.addImage({
    path: SS("screenshot_detail1.png"),
    x: 1.5, y: 4.3, w: 2.5, h: 1.3,
    sizing: { type: "contain", w: 2.5, h: 1.3 },
  });
  slide.addImage({
    path: SS("screenshot_detail2.png"),
    x: 6.0, y: 4.3, w: 2.5, h: 1.3,
    sizing: { type: "contain", w: 2.5, h: 1.3 },
  });
  slide.addText("App 实机运行展示", {
    x: 3.5, y: 4.15, w: 3, h: 0.2,
    fontSize: 10, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });
  slide.addText("感谢老师指导 · 欢迎提问", {
    x: 1, y: 4.85, w: 8, h: 0.35,
    fontSize: 15, fontFace: FONT, color: C.GRAY, align: "center", margin: 0,
  });
}

// ============== MAIN ==============
function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "崔桐浩, 马鸣远, 王略帆";
  pres.title = "美园外卖 - 答辩展示";

  // Slide 1: Cover
  createCover(pres);

  // Slide 2: Project Overview
  createOverview(pres);

  // Slide 3: Transition - Part 1 (Cui)
  addTransitionSlide(pres, "PART 01", "数据库设计与工程决策", "崔桐浩", "circle");

  // Slide 4: DB Version Evolution
  createDBEvolution(pres);

  // Slide 5: Soft Delete & Username Recycle
  createSoftDelete(pres);

  // Slide 6: Feasibility Analysis (NEW)
  createFeasibility(pres);

  // Slide 7: Project Plan & Business Rules (NEW)
  createProjectPlan(pres);

  // Slide 8: ER Diagram (full page)
  createERDiagram(pres);

  // Slide 9: Transition - Part 2 (Ma)
  addTransitionSlide(pres, "PART 02", "核心业务逻辑设计与实现", "马鸣远", "triangle");

  // Slide 10: Order State Machine
  createStateMachine(pres);

  // Slide 11: Cart Constraint
  createCartConstraint(pres);

  // Slides 12-15: Business Flow Diagrams (image contain + text + screenshot)
  createFlowSlideWithScreenshot(pres, 12,
    "登录与角色分流",
    "启动 → 校验 → 会话保存 → 三向跳转",
    IMG("ma2/media/image1.jpeg"),
    "screenshot_login.png",
    [
      { text: "App启动 → 初始化", options: { breakLine: true, bold: true } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "检测是否已登录", options: { breakLine: true, bold: true } },
      { text: "已登录→按角色自动跳转", options: { breakLine: true } },
      { text: "管理员 → 管控页面", options: { breakLine: true, fontFace: FONT } },
      { text: "商家 → 商品管理页", options: { breakLine: true, fontFace: FONT } },
      { text: "买家 → 商品浏览页", options: { breakLine: true, fontFace: FONT } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "未登录→填写表单", options: { breakLine: true, bold: true } },
      { text: "数据库查询校验账号", options: { breakLine: true, fontFace: FONT } },
      { text: "封禁账号→拒绝并提示", options: { breakLine: true } },
      { text: "正常账号→保存会话→跳转", options: { breakLine: true } },
    ]
  );

  createFlowSlideWithScreenshot(pres, 13,
    "买家下单全链路",
    "浏览 → 搜索 → 加购 → 结算 → 广播通知",
    IMG("ma2/media/image2.jpeg"),
    "screenshot_buyer.png",
    [
      { text: "双重过滤展示商品", options: { breakLine: true, bold: true } },
      { text: "排除已删除商家和已下架商品", options: { breakLine: true, fontFace: FONT } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "输入即搜实时过滤", options: { breakLine: true, bold: true } },
      { text: "按商品名称和描述匹配", options: { breakLine: true, fontFace: FONT } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "加购时同商家校验", options: { breakLine: true, bold: true } },
      { text: "不同商家→提示先清空购物车", options: { breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "结算生成订单", options: { breakLine: true, bold: true } },
      { text: "下单成功→清空购物车+广播通知", options: { breakLine: true, fontFace: FONT } },
    ]
  );

  createFlowSlideWithScreenshot(pres, 14,
    "商家商品与订单管理",
    "商品增删改查 + 图片本地存储 + 接单配送两阶段",
    IMG("ma2/media/image3.jpeg"),
    "screenshot_merchant.png",
    [
      { text: "商品新增与编辑双模式", options: { breakLine: true, bold: true } },
      { text: "通过传递商品信息自动识别模式", options: { breakLine: true, fontFace: FONT } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "图片保存到手机本地", options: { breakLine: true, bold: true } },
      { text: "图片存为文件，数据库只记录路径", options: { breakLine: true, fontFace: FONT } },
      { text: "减小数据库体积", options: { breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "订单处理两个关键操作", options: { breakLine: true, bold: true } },
      { text: "待接单→接单→开始配送", options: { breakLine: true } },
      { text: "已接单→开始配送→配送中", options: { breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "账号注销→软删除机制", options: { breakLine: true, bold: true } },
      { text: "标记为已删除，用户名可回收", options: { breakLine: true, fontFace: FONT } },
    ]
  );

  createFlowSlideWithScreenshot(pres, 15,
    "管理员商家状态管控",
    "商家列表 → 封禁/解封 → 提示反馈 → 刷新",
    IMG("ma2/media/image4.jpeg"),
    "screenshot_admin.png",
    [
      { text: "系统预置管理员账号", options: { breakLine: true, bold: true } },
      { text: "仅拥有商家状态管理权限", options: { breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "加载全部商家列表", options: { breakLine: true, bold: true } },
      { text: "列表形式展示所有商家", options: { breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "点击弹出管理菜单", options: { breakLine: true, bold: true } },
      { text: "选择封禁或解封操作", options: { breakLine: true } },
      { text: "已注销的商家跳过操作", options: { breakLine: true } },
      { text: "", options: { breakLine: true, fontSize: 3 } },
      { text: "执行状态更新并刷新列表", options: { breakLine: true, bold: true, fontFace: FONT } },
      { text: "操作后弹出提示并自动刷新", options: { breakLine: true } },
    ]
  );

  // Slide 16: Transition - Part 3 (Wang)
  addTransitionSlide(pres, "PART 03", "数据建模与编码规范设计", "王略帆", "diamond");

  // Slide 17: DFD + D5
  createDFDAndD5(pres);

  // Slide 18: I/O Design (NEW)
  createIODesign(pres, 18);

  // Slide 19: Coding System
  createCodingSystem(pres);

  // Slide 20: Data Dictionary (NEW)
  createDataDict(pres, 20);

  // Slide 21: Summary
  createSummary(pres);

  const outputPath = path.join(__dirname, "美园外卖答辩展示_v4.pptx");
  return pres.writeFile({ fileName: outputPath });
}

main()
  .then((fileName) => console.log("PPT generated: " + fileName))
  .catch((err) => console.error("Failed:", err));
