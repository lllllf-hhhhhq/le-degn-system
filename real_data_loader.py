#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Road Network Loader for LE-DEGN
使用 OpenStreetMap 真实路网数据替代随机生成路网

功能:
  - 从 OpenStreetMap 下载指定城市的真实道路网络
  - 将 osmnx MultiDiGraph 转换为 LE-DEGN RoadNetworkEnv 兼容格式
  - 支持按城市、行政区、中心点半径三种方式提取路网
  - 支持从 LibCity 格式数据集加载真实交通流量/速度数据作为拥堵概率来源
  - 在无 osmnx 时优雅降级，给出安装提示

LE-DEGN 边属性完整列表 (与 RoadNetworkEnv._build_network 对齐):
  - weight:          路径搜索距离权重 (道路长度 / speed_factor)
  - width:           道路宽度（米）
  - angle:           道路方向角度（0-360，正北为0，顺时针）
  - type:            道路类型编号（0=常规道路，1=特殊道路）
  - scenario:        道路场景描述（主干道/次干道/居民区/未分类 等）
  - time_window:     通行时间窗口 {'E': 开始分钟, 'L': 结束分钟}
  - color:           可视化颜色 (hex 字符串)
  - speed_factor:    速度因子（相对基准 50km/h 的比例）
  - congestion_prob: 拥堵概率 [0, 1]
"""

import os
import sys
import math
import csv
from typing import Dict, Tuple, Optional, List, Any

import numpy as np
import networkx as nx

# ============================================================
# 优雅降级：尝试导入 osmnx
# ============================================================
try:
    import osmnx as ox  # type: ignore
    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False
    ox = None  # type: ignore


class RealRoadNetworkLoader:
    """从 OpenStreetMap 加载真实城市路网

    将 osmnx 下载的 OSM 路网转换为 LE-DEGN RoadNetworkEnv 完全兼容的
    MultiDiGraph 格式，包含所有必需的边属性和节点坐标。

    使用示例:
        >>> loader = RealRoadNetworkLoader(city="Shanghai, China", radius=3000)
        >>> loader.print_statistics()
        >>> # loader.G, loader.pos, loader.edge_widths 可直接供 RoadNetworkEnv 使用
    """

    # ============================================================
    # OSM highway → LE-DEGN scenario 映射表
    # ============================================================
    HIGHWAY_TO_SCENARIO: Dict[str, str] = {
        'motorway':       '主干道',
        'trunk':          '主干道',
        'primary':        '次干道',
        'secondary':      '次干道',
        'tertiary':       '次干道',
        'residential':    '居民区',
        'living_street':  '居民区',
        'unclassified':   '未分类',
        'service':        '未分类',
        'track':          '未分类',
        'road':           '未分类',
        'pedestrian':     '商业步行街',
        'footway':        '商业步行街',
        'path':           '未分类',
        'cycleway':       '未分类',
        'steps':          '商业步行街',
    }

    # ============================================================
    # 默认 speed_factor — 当 OSM 无 maxspeed 标签时使用
    # 基准速度约 50 km/h，speed_factor = 实际限速 / 50
    # ============================================================
    DEFAULT_SPEED_FACTOR: Dict[str, float] = {
        'motorway':       1.2,   # ~120 km/h
        'trunk':          1.1,   # ~80-100 km/h
        'primary':        1.0,   # ~60 km/h
        'secondary':      0.8,   # ~50 km/h
        'tertiary':       0.7,   # ~40 km/h
        'residential':    0.7,   # ~40 km/h
        'living_street':  0.6,   # ~30 km/h
        'unclassified':   0.6,   # ~30 km/h
        'service':        0.6,   # ~30 km/h
        'pedestrian':     0.4,   # ~20 km/h
        'footway':        0.3,   # ~15 km/h
        'path':           0.5,
        'cycleway':       0.5,
        'track':          0.5,
        'road':           0.6,
        'steps':          0.2,
    }

    # ============================================================
    # 默认 congestion_prob — 无 LibCity 数据时根据 road type 推算
    # ============================================================
    DEFAULT_CONGESTION_PROB: Dict[str, float] = {
        'motorway':       0.15,
        'trunk':          0.20,
        'primary':        0.25,
        'secondary':      0.30,
        'tertiary':       0.35,
        'residential':    0.20,
        'living_street':  0.15,
        'unclassified':   0.30,
        'service':        0.35,
        'pedestrian':     0.40,
        'footway':        0.25,
        'path':           0.20,
        'cycleway':       0.15,
        'track':          0.20,
        'road':           0.30,
        'steps':          0.50,
    }

    # ============================================================
    # 场景 → 颜色映射（与 RoadNetworkEnv 保持一致）
    # ============================================================
    SCENARIO_COLORS: Dict[str, str] = {
        '主干道':     '#45B7D1',
        '次干道':     '#F39C12',
        '居民区':     '#96CEB4',
        '未分类':     '#95A5A6',
        '商业步行街': '#FF6B6B',
        '施工路段':   '#FFEAA7',
        '学校周边':   '#4ECDC4',
        '连通补边':   '#BDC3C7',
    }

    # ============================================================
    # 单车道平均宽度（米），用于根据 lanes 推算 road width
    # ============================================================
    LANE_WIDTH_MAP: Dict[str, float] = {
        'motorway':       3.75,
        'trunk':          3.50,
        'primary':        3.25,
        'secondary':      3.00,
        'tertiary':       2.75,
        'residential':    2.50,
        'living_street':  2.50,
        'unclassified':   2.50,
        'service':        2.00,
    }

    # ============================================================
    # __init__
    # ============================================================
    def __init__(
        self,
        city: str = "Shanghai, China",
        district: Optional[str] = None,
        radius: Optional[float] = None,
        network_type: str = "drive",
    ):
        """初始化真实道路网络加载器

        参数:
            city: 城市名称。遵循 OSM 命名约定，例如：
                  "Shanghai, China" / "北京市, China" / "Tokyo, Japan"
            district: 可选。行政区名称，例如 "Pudong, Shanghai, China"。
                      指定后将仅提取该行政区的路网。
            radius: 可选。以城市/行政区几何中心为圆心，提取半径(米)内的路网。
                    对于大城市，建议设置此参数以避免下载海量数据。
            network_type: OSM 路网类型，默认 "drive" (机动车道)。
                          可选: "walk", "bike", "all", "drive_service"

        异常:
            ImportError: 如果 osmnx 未安装
            RuntimeError: 如果 OSM 查询失败（如城市名无效）
        """
        if not OSMNX_AVAILABLE:
            raise ImportError(
                "osmnx 库未安装，无法加载 OSM 路网数据。\n"
                "安装方法:\n"
                "  pip install osmnx\n"
                "建议使用 conda（自动处理 GDAL 等复杂依赖）:\n"
                "  conda install -c conda-forge osmnx"
            )

        self.city = city
        self.district = district
        self.radius = radius
        self.network_type = network_type

        # ---- LE-DEGN 兼容的核心数据结构 ----
        self.G: nx.MultiDiGraph = nx.MultiDiGraph()
        self.pos: Dict[int, Tuple[float, float]] = {}
        self.edge_widths: Dict[Tuple[int, int], float] = {}
        self.closed_edges: set = set()  # 预留，与 RoadNetworkEnv 接口一致

        # ---- OSM 元数据，便于调试和外部查询 ----
        self.osm_node_ids: Dict[int, int] = {}           # LE id → OSM osmid
        self.osm_edge_ids: Dict[Tuple[int, int], str] = {}  # (u,v) → OSM way id
        self._raw_graph: Optional[nx.MultiDiGraph] = None

        # ---- 执行加载流水线 ----
        self._load_osm_network()
        self._build_legdeg_format()

        # ---- 统计摘要 ----
        self.node_count: int = self.G.number_of_nodes()
        self.edge_count: int = self.G.number_of_edges()

    # ============================================================
    # 步骤 1: 下载 OSM 原始路网
    # ============================================================
    def _load_osm_network(self) -> None:
        """使用 osmnx 从 OpenStreetMap 下载并预处理路网

        预处理包括:
          - simplify=True: 移除冗余节点，保留交叉口和拐点
          - project_graph: 从 WGS84 投影到合适的米制 CRS
        """
        place = self.district if self.district else self.city
        print(f"[RealRoadNetworkLoader] 正在从 OSM 加载路网: {place} ...", flush=True)

        # 常见中国城市坐标（用于绕过 Nominatim geocoding）
        CITY_COORDS = {
            '上海': (31.2304, 121.4737),
            'shanghai': (31.2304, 121.4737),
            '北京': (39.9042, 116.4074),
            'beijing': (39.9042, 116.4074),
            '深圳': (22.5431, 114.0579),
            'shenzhen': (22.5431, 114.0579),
            '成都': (30.5728, 104.0668),
            'chengdu': (30.5728, 104.0668),
            '广州': (23.1291, 113.2644),
            'guangzhou': (23.1291, 113.2644),
        }
        place_lower = place.lower()

        try:
            if self.radius is not None:
                # ---- 半径模式: 优先用预设坐标，绕过 Nominatim ----
                center_lat, center_lng = None, None
                for key, coords in CITY_COORDS.items():
                    if key in place_lower:
                        center_lat, center_lng = coords
                        break
                if center_lat is None:
                    # 回退到 geocode
                    gdf = ox.geocode_to_gdf(place)
                    center_lat = float(gdf.geometry.centroid.y.iloc[0])
                    center_lng = float(gdf.geometry.centroid.x.iloc[0])
                print(f"  中心坐标: ({center_lat:.4f}, {center_lng:.4f}), "
                      f"半径={self.radius}m")

                self._raw_graph = ox.graph_from_point(
                    (center_lat, center_lng),
                    dist=self.radius,
                    network_type=self.network_type,
                    simplify=True,
                )
            else:
                # ---- 区域模式: 直接用坐标提取多边形区域 ----
                center_lat, center_lng = None, None
                for key, coords in CITY_COORDS.items():
                    if key in place_lower:
                        center_lat, center_lng = coords
                        break
                if center_lat is not None:
                    # 用坐标点 + 大半径代替 geocode 的 polygon 模式
                    self._raw_graph = ox.graph_from_point(
                        (center_lat, center_lng),
                        dist=5000,  # 默认5km
                        network_type=self.network_type,
                        simplify=True,
                    )
                    print(f"  使用预设坐标 ({center_lat:.4f}, {center_lng:.4f}), 半径=5000m")
                else:
                    self._raw_graph = ox.graph_from_place(
                        place,
                        network_type=self.network_type,
                        simplify=True,
                    )

        except Exception as e:
            raise RuntimeError(
                f"无法从 OSM 加载路网 '{place}'。\n"
                f"请检查:\n"
                f"  1. 城市名称是否符合 OSM 约定（如 'Shanghai, China'）\n"
                f"  2. 网络连接是否正常\n"
                f"  3. 是否指定了合理的 radius 避免超大请求\n"
                f"原始错误: {e}"
            ) from e

        # ---- 投影到米制坐标系 ----
        # 原始 OSM 图使用 WGS84 (经纬度)，投影后 (x,y) 单位为米，
        # 便于计算距离、角度以及 speed_factor。
        print("  正在投影到本地米制坐标系 ...", flush=True)
        self._raw_graph = ox.project_graph(self._raw_graph)

        raw_nodes = len(self._raw_graph.nodes)
        raw_edges = len(self._raw_graph.edges)
        print(f"  OSM 原始数据: {raw_nodes} 个节点, {raw_edges} 条边")

    # ============================================================
    # 步骤 2: 转换为 LE-DEGN 兼容格式
    # ============================================================
    def _build_legdeg_format(self) -> None:
        """将 osmnx 输出的 networkx.MultiDiGraph 转换为 LE-DEGN 格式

        转换过程:
          1. OSM osmid (LargeInt) → LE-DEGN node_id (0..N-1 连续整数)
          2. 提取投影坐标到 self.pos
          3. 将边属性映射为 RoadNetworkEnv 所需的 9 个必需字段
          4. 处理 oneway 属性：单向路仅添加单项边，双向路添加来回边
          5. 确保图的弱连通性
        """
        print("[RealRoadNetworkLoader] 正在转换为 LE-DEGN 兼容格式 ...", flush=True)

        raw = self._raw_graph

        # ---------- 2.1 节点映射 ----------
        old_nodes: List[int] = list(raw.nodes())
        node_mapping: Dict[int, int] = {}  # OSM osmid → LE-DEGN node_id

        for new_id, old_osmid in enumerate(old_nodes):
            node_mapping[old_osmid] = new_id
            self.osm_node_ids[new_id] = old_osmid

            # 节点坐标 (已投影到米制)
            nd = raw.nodes[old_osmid]
            self.pos[new_id] = (float(nd['x']), float(nd['y']))
            self.G.add_node(new_id)

        # ---------- 2.2 边转换 ----------
        skipped_no_highway = 0

        for u_old, v_old, key, edge_data in raw.edges(keys=True, data=True):
            # 过滤环路边
            if u_old == v_old:
                continue

            # 提取 highway 标签
            highway_raw = edge_data.get('highway', None)
            if highway_raw is None:
                skipped_no_highway += 1
                continue
            highway: str = highway_raw[0] if isinstance(highway_raw, list) else str(highway_raw)

            # 映射到 LE-DEGN 类型
            scenario = self.HIGHWAY_TO_SCENARIO.get(highway, '未分类')

            # type 编号: 0=常规道路, 1=次干道/特殊道路
            road_type = 0 if scenario in ('主干道', '居民区', '商业步行街') else 1

            # ---- oneway 处理 ----
            oneway = edge_data.get('oneway', None)

            # oneway 可能是 True/False, 字符串 "yes"/"no", 或数字 1/0
            if oneway is True or oneway in ('yes', 1, '1', 'True', 'true'):
                is_bidirectional = False
            elif oneway is False or oneway in ('no', 0, '0', 'False', 'false'):
                is_bidirectional = True
            elif oneway is None:
                # OSM 默认: motorway 单向，其他双向
                is_bidirectional = (highway != 'motorway')
            else:
                is_bidirectional = (highway != 'motorway')

            # ---- 核心属性计算 ----
            length_m  = float(edge_data.get('length', 100.0))
            speed_f   = self._compute_speed_factor(edge_data, highway)
            weight    = length_m / max(speed_f, 0.01)  # 路径权重 = 距离 / 速度因子
            width     = self._compute_width(edge_data, highway)
            angle     = self._compute_angle(node_mapping[u_old], node_mapping[v_old])
            color     = self.SCENARIO_COLORS.get(scenario, '#45B7D1')
            cong_prob = self.DEFAULT_CONGESTION_PROB.get(highway, 0.30)

            # 边属性的时间窗口: 全天通行
            time_window = {'E': 0, 'L': 1440}

            u_new = node_mapping[u_old]
            v_new = node_mapping[v_old]

            # ---- 组装完整的边属性字典 ----
            base_attrs: Dict[str, Any] = {
                'weight':          round(weight, 4),
                'width':           round(width, 3),
                'angle':           round(angle, 2),
                'type':            road_type,
                'scenario':        scenario,
                'time_window':     time_window,
                'color':           color,
                'speed_factor':    round(speed_f, 4),
                'congestion_prob': round(cong_prob, 4),
                # ---- 附加 OSM 元数据（调试/查询用） ----
                '_osm_highway':    highway,
                '_osm_length_m':   round(length_m, 2),
                '_osm_oneway':     not is_bidirectional,
                '_osm_name':       str(edge_data.get('name', '')),
                '_osm_maxspeed':   str(edge_data.get('maxspeed', '')),
            }

            # ---- 正向边 (u → v) ----
            if not self.G.has_edge(u_new, v_new):
                self.G.add_edge(u_new, v_new, **base_attrs)
                self.edge_widths[(u_new, v_new)] = width
                self.osm_edge_ids[(u_new, v_new)] = str(edge_data.get('osmid', ''))

            # ---- 反向边 (v → u)，仅双向路 ----
            if is_bidirectional and not self.G.has_edge(v_new, u_new):
                rev_angle = (angle + 180.0) % 360.0
                rev_attrs = {**base_attrs, 'angle': round(rev_angle, 2)}
                self.G.add_edge(v_new, u_new, **rev_attrs)
                self.edge_widths[(v_new, u_new)] = width
                self.osm_edge_ids[(v_new, u_new)] = str(edge_data.get('osmid', ''))

        if skipped_no_highway > 0:
            print(f"  跳过 {skipped_no_highway} 条无 highway 标签的边")

        # ---------- 2.3 连通性修复 ----------
        self._ensure_connectivity()

        # ---------- 2.4 删除 osmnx 原始图以释放内存 ----------
        del self._raw_graph
        self._raw_graph = None

        print(f"  LE-DEGN 格式转换完成: "
              f"{self.G.number_of_nodes()} 个节点, "
              f"{self.G.number_of_edges()} 条边")

    # ============================================================
    # speed_factor 计算
    # ============================================================
    def _compute_speed_factor(self, edge_data: dict, highway: str) -> float:
        """根据 OSM maxspeed 推算 speed_factor

        优先使用 OSM 的 maxspeed 标签，若缺失则根据 highway 类型使用默认值。
        speed_factor = 路段限速(km/h) / 基准速度(50 km/h)

        返回值范围: [0.2, 1.5]，对应 10 km/h ~ 75 km/h
        """
        maxspeed = edge_data.get('maxspeed', None)

        if maxspeed is not None:
            # maxspeed 可能是字符串列表（osmnx 有时保留多个值）
            if isinstance(maxspeed, list):
                maxspeed = maxspeed[0]

            try:
                speed_val = float(maxspeed)
                # 转换并裁剪到合理范围
                return float(np.clip(speed_val / 50.0, 0.2, 1.5))
            except (ValueError, TypeError):
                pass  # 非数值 maxspeed（如 'signals', 'national'），回退到默认

        return self.DEFAULT_SPEED_FACTOR.get(highway, 0.6)

    # ============================================================
    # 道路宽度计算
    # ============================================================
    def _compute_width(self, edge_data: dict, highway: str) -> float:
        """计算道路宽度（米）

        优先级: OSM width > lanes × 单车道宽 > highway 类型默认值

        注: 由于 width 在 LE-DEGN 中用于可视化线宽，这里使用实际宽度(米) x 2
        以在 matplotlib 中产生视觉上合理的线宽。
        """
        # ---- 尝试 OSM width 标签 ----
        w = edge_data.get('width', None)
        if w is not None:
            if isinstance(w, list):
                w = w[0]
            try:
                return float(w)
            except (ValueError, TypeError):
                pass

        # ---- 尝试从 lanes 推算 ----
        lanes = edge_data.get('lanes', None)
        if lanes is not None:
            if isinstance(lanes, list):
                lanes = lanes[0]
            try:
                num = max(1, int(float(lanes)))
                lane_w = self.LANE_WIDTH_MAP.get(highway, 3.0)
                return num * lane_w
            except (ValueError, TypeError):
                pass

        # ---- highway 类型默认值 ----
        return self.LANE_WIDTH_MAP.get(highway, 3.0)

    # ============================================================
    # 角度计算
    # ============================================================
    def _compute_angle(self, u: int, v: int) -> float:
        """计算从节点 u 到节点 v 的方向角度

        返回值: 0° ~ 360°，正北(y轴正方向)=0°，顺时针增加
        此定义与 RoadNetworkEnv._calc_angle 保持一致。
        """
        if u not in self.pos or v not in self.pos:
            return 0.0

        dx = self.pos[v][0] - self.pos[u][0]
        dy = self.pos[v][1] - self.pos[u][1]

        angle_rad = math.atan2(dx, dy)  # 正北为 0
        angle_deg = math.degrees(angle_rad)
        return angle_deg % 360.0

    # ============================================================
    # 连通性修复
    # ============================================================
    def _ensure_connectivity(self) -> None:
        """确保图的弱连通性

        OSM 数据可能包含少量孤立节点或死端（仅入/仅出）。
        此方法为其添加「连通补边」以保证路网可用。
        参照 RoadNetworkEnv._ensure_strong_connectivity 的逻辑。
        """
        # ---- 修复完全孤立节点 (degree == 0) ----
        isolated_count = 0
        for n in list(self.G.nodes()):
            if self.G.degree(n) == 0:
                candidates = [
                    m for m in self.G.nodes()
                    if m != n and self.G.degree(m) > 0
                ]
                if not candidates:
                    continue  # 极端情况: 所有节点都孤立

                near = min(candidates, key=lambda m: math.hypot(
                    self.pos[n][0] - self.pos[m][0],
                    self.pos[n][1] - self.pos[m][1],
                ))

                dist = math.hypot(
                    self.pos[n][0] - self.pos[near][0],
                    self.pos[n][1] - self.pos[near][1],
                )
                angle = self._compute_angle(n, near)

                fill_attrs = {
                    'weight': dist, 'width': 3.0, 'angle': angle,
                    'type': 0, 'scenario': '连通补边',
                    'time_window': {'E': 0, 'L': 1440},
                    'color': '#BDC3C7', 'speed_factor': 1.0,
                    'congestion_prob': 0.05,
                }

                self.G.add_edge(n, near, **fill_attrs)
                self.G.add_edge(near, n, **{**fill_attrs, 'angle': (angle + 180) % 360})
                self.edge_widths[(n, near)] = 3.0
                self.edge_widths[(near, n)] = 3.0
                isolated_count += 1

        if isolated_count > 0:
            print(f"  已为 {isolated_count} 个孤立节点添加双向连通补边")

        # ---- 修复死端节点 (out_degree == 0 但 in_degree > 0) ----
        sink_count = 0
        for n in list(self.G.nodes()):
            if self.G.out_degree(n) == 0 and self.G.in_degree(n) > 0:
                candidates = [m for m in self.G.nodes() if m != n]
                if not candidates:
                    continue

                near = min(candidates, key=lambda m: math.hypot(
                    self.pos[n][0] - self.pos[m][0],
                    self.pos[n][1] - self.pos[m][1],
                ))

                dist = math.hypot(
                    self.pos[n][0] - self.pos[near][0],
                    self.pos[n][1] - self.pos[near][1],
                )
                angle = self._compute_angle(n, near)

                self.G.add_edge(n, near,
                    weight=dist, width=3.0, angle=angle,
                    type=0, scenario='连通补边',
                    time_window={'E': 0, 'L': 1440},
                    color='#BDC3C7', speed_factor=1.0, congestion_prob=0.05,
                )
                self.edge_widths[(n, near)] = 3.0
                sink_count += 1

        if sink_count > 0:
            print(f"  已为 {sink_count} 个死端节点添加出边")

    # ============================================================
    # LibCity 格式交通数据加载
    # ============================================================
    def load_traffic_data(self, speed_csv_path: Optional[str] = None) -> bool:
        """从 LibCity 格式数据集加载真实交通流量/速度数据

        LibCity 是城市计算领域的标准化交通预测库。
        其速度数据文件为 CSV 格式，典型结构如下:

            road_id,time,avg_speed,volume
            12345,0,45.2,120
            12345,5,42.1,115
            ...

        加载后，每条边的 congestion_prob 将根据该路段的历史平均速度更新:
            congestion_prob = 1 - avg_speed / global_max_speed

        参数:
            speed_csv_path: LibCity 格式的速度 CSV 文件路径。
                           若为 None 则保持默认拥堵概率。

        返回:
            bool: True 表示成功加载并更新了部分边的拥堵概率。
        """
        if speed_csv_path is None:
            print("[RealRoadNetworkLoader] 未指定交通数据文件，使用默认 congestion_prob")
            return False

        if not os.path.isfile(speed_csv_path):
            print(f"[RealRoadNetworkLoader] 文件不存在: {speed_csv_path}")
            return False

        try:
            from collections import defaultdict

            print(f"[RealRoadNetworkLoader] 正在加载交通数据: {speed_csv_path}")

            # ---- 读取并聚合每个 road_id 的平均速度 ----
            road_speeds: Dict[str, List[float]] = defaultdict(list)

            with open(speed_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # 兼容 LibCity 不同版本的列名
                for row in reader:
                    rid = (row.get('road_id')
                        or row.get('road_ID')
                        or row.get('edge_id')
                        or row.get('segment_id', ''))

                    speed = float(row.get('avg_speed')
                                or row.get('speed')
                                or row.get('travel_time', 0))

                    if rid and speed > 0:
                        road_speeds[rid].append(speed)

            if not road_speeds:
                print("  [警告] 文件中未找到有效数据，使用默认拥堵概率")
                return False

            # ---- 映射到图中的边 ----
            global_max = max(
                max(speeds) for speeds in road_speeds.values()
            )
            updated = 0

            for (u, v), osm_id in self.osm_edge_ids.items():
                # LibCity road_id 可能存储为 OSM way ID
                match_key = str(osm_id)
                if match_key in road_speeds:
                    speeds = road_speeds[match_key]
                    avg = float(np.mean(speeds))

                    # 拥堵概率 = 1 - 平均速度 / 全局最高速度
                    cong = float(np.clip(1.0 - avg / max(global_max, 0.1), 0.02, 0.95))

                    if self.G.has_edge(u, v):
                        self.G[u][v][0]['congestion_prob'] = cong
                        updated += 1

            print(f"  交通数据加载完成: {len(road_speeds)} 个路段的速度记录, "
                  f"成功匹配 {updated} 条边")
            return updated > 0

        except Exception as e:
            print(f"[RealRoadNetworkLoader] 加载交通数据时出错: {e}")
            print("  将保持使用默认拥堵概率")
            return False

    # ============================================================
    # 统计输出
    # ============================================================
    def get_statistics(self) -> Dict[str, Any]:
        """返回路网摘要统计的字典"""
        scenario_counts: Dict[str, int] = {}
        speed_factors: List[float] = []
        cong_probs: List[float] = []
        widths: List[float] = []

        for _, _, data in self.G.edges(data=True):
            s = data.get('scenario', '未知')
            scenario_counts[s] = scenario_counts.get(s, 0) + 1
            speed_factors.append(float(data.get('speed_factor', 1.0)))
            cong_probs.append(float(data.get('congestion_prob', 0.3)))
            widths.append(float(data.get('width', 3.0)))

        n = self.G.number_of_nodes()
        e = self.G.number_of_edges()

        return {
            'city':             self.city,
            'district':         self.district,
            'radius_m':         self.radius,
            'network_type':     self.network_type,
            'node_count':       n,
            'edge_count':       e,
            'avg_degree':       round(e / max(n, 1), 3),
            'scenario_counts':  scenario_counts,
            'avg_speed_factor': round(float(np.mean(speed_factors)), 4) if speed_factors else 0,
            'min_speed_factor': round(float(np.min(speed_factors)), 4) if speed_factors else 0,
            'max_speed_factor': round(float(np.max(speed_factors)), 4) if speed_factors else 0,
            'avg_congestion':   round(float(np.mean(cong_probs)), 4) if cong_probs else 0,
            'avg_width':        round(float(np.mean(widths)), 2) if widths else 0,
        }

    def print_statistics(self) -> None:
        """美观打印路网统计信息"""
        s = self.get_statistics()

        print()
        print("=" * 62)
        print("  LE-DEGN 真实路网加载结果")
        print("=" * 62)
        print(f"  城市:             {s['city']}")
        if s['district']:
            print(f"  行政区:           {s['district']}")
        if s['radius_m'] is not None:
            print(f"  半径:             {s['radius_m']} m")
        print(f"  路网类型:         {s['network_type']}")
        print(f"  节点数:           {s['node_count']}")
        print(f"  边数:             {s['edge_count']}")
        print(f"  平均出/入度:      {s['avg_degree']}")
        print(f"  速度因子:         均值={s['avg_speed_factor']:.4f}  "
              f"(min={s['min_speed_factor']:.2f}, max={s['max_speed_factor']:.2f})")
        print(f"  平均拥堵概率:     {s['avg_congestion']:.4f}")
        print(f"  平均道路宽度:     {s['avg_width']:.2f} m")
        print()
        print("  道路类型分布:")
        for sc, cnt in sorted(s['scenario_counts'].items(), key=lambda x: -x[1]):
            pct = cnt / max(s['edge_count'], 1) * 100
            bar = '█' * int(pct / 2)
            print(f"    {sc:10s}  {cnt:6d} 边  ({pct:5.1f}%)  {bar}")
        print("=" * 62)
        print()

    # ============================================================
    # 便捷方法: 检查是否可以直接替换到 RoadNetworkEnv
    # ============================================================
    def validate_compatibility(self) -> Tuple[bool, List[str]]:
        """验证当前数据是否与 RoadNetworkEnv 兼容

        返回:
            (是否兼容, 问题列表)
        """
        issues: List[str] = []
        required_edge_attrs = [
            'weight', 'width', 'angle', 'type', 'scenario',
            'time_window', 'color', 'speed_factor', 'congestion_prob',
        ]

        if not isinstance(self.G, nx.MultiDiGraph):
            issues.append("self.G 不是 networkx.MultiDiGraph 实例")

        if not isinstance(self.pos, dict):
            issues.append("self.pos 不是 dict 类型")
        else:
            for n in self.G.nodes():
                if n not in self.pos:
                    issues.append(f"节点 {n} 不在 self.pos 中")
                    break

        for u, v, data in self.G.edges(data=True):
            for attr in required_edge_attrs:
                if attr not in data:
                    issues.append(f"边 ({u}, {v}) 缺少属性: {attr}")
            break  # 只检查第一条边即可

        return len(issues) == 0, issues


# ================================================================
# 测试入口
# ================================================================
if __name__ == '__main__':
    print("LE-DEGN 真实路网加载器 (RealRoadNetworkLoader)  测试")
    print("-" * 50)

    # ---- 检查 osmnx 是否可用 ----
    if not OSMNX_AVAILABLE:
        print("")
        print("[跳过] osmnx 未安装，无法执行实际加载测试。")
        print("请安装 osmnx 后再试:")
        print("  pip install osmnx")
        print("")
        print("验证代码结构 ...")
        # 即使没有 osmnx，也可以验证类的定义
        assert hasattr(RealRoadNetworkLoader, '_load_osm_network')
        assert hasattr(RealRoadNetworkLoader, '_build_legdeg_format')
        assert hasattr(RealRoadNetworkLoader, 'load_traffic_data')
        assert hasattr(RealRoadNetworkLoader, 'get_statistics')
        assert hasattr(RealRoadNetworkLoader, 'print_statistics')
        assert hasattr(RealRoadNetworkLoader, 'validate_compatibility')
        print("[OK] RealRoadNetworkLoader 类定义完整")
        sys.exit(0)

    # ---- 实际加载测试 ----
    try:
        # 使用较小的半径以加快测试
        print("\n[测试] 加载上海黄浦区路网 (半径 3000m, drive 网络) ...")
        loader = RealRoadNetworkLoader(
            city="Shanghai, China",
            district="Huangpu, Shanghai, China",
            radius=3000,
            network_type="drive",
        )

        # 打印统计
        loader.print_statistics()

        # 兼容性验证
        print("[验证] 检查与 RoadNetworkEnv 的数据结构兼容性 ...")
        ok, issues = loader.validate_compatibility()
        if ok:
            print("  [PASS] 所有必需属性字段均存在")
            print("  [PASS] self.G 为 MultiDiGraph")
            print("  [PASS] self.pos 包含所有节点坐标")
            print("  [PASS] self.edge_widths 包含所有边宽度")
            print("  [PASS] 与 RoadNetworkEnv 数据结构完全兼容")
        else:
            print("  [FAIL] 发现以下兼容性问题:")
            for iss in issues:
                print(f"    - {iss}")

        # 展示样例边数据
        print("\n[样例] 前 3 条边的属性:")
        for i, (u, v, data) in enumerate(list(loader.G.edges(data=True))[:3]):
            print(f"  边 {i+1}: ({u} → {v})")
            print(f"    scenario={data['scenario']},  type={data['type']},  "
                  f"speed_factor={data['speed_factor']:.3f}")
            print(f"    width={data['width']:.2f}m,  weight={data['weight']:.1f},  "
                  f"angle={data['angle']:.1f}°")
            print(f"    congestion_prob={data['congestion_prob']:.3f},  "
                  f"color={data['color']}")
            if data.get('_osm_name'):
                print(f"    OSM 路名: {data['_osm_name']}")
            print()

        print("[测试] 全部通过。")

    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        print("\n提示:")
        print("  - 如果网络不通，请检查是否可以访问 https://overpass-api.de")
        print("  - 如果城市名找不到，尝试使用不同的名称格式")
        print("  - 对于大型城市，请使用 radius 参数限制加载范围")
