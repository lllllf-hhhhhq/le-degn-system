(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // ── Chart 1: Ablation Cost Comparison ──
  var configs = ['A (ERFM only)', 'B (ERFM+SA-DGWN)', 'C (ERFM+LHH)', 'D (Full)'];
  var costsMean = [258449.4, 257097.5, 257161.5, 256798.4];
  var costsStd = [3820.6, 7481.0, 6781.8, 5879.7];
  var aoccMean = [0.9528, 0.9530, 0.9530, 0.9528];

  var c1 = echarts.init(document.getElementById('chart-cost'), null, { renderer: 'svg' });
  c1.setOption({
    animation: false,
    color: [accent, accent2, accent2, accent],
    tooltip: { trigger: 'axis', appendToBody: true,
      formatter: function(p) { return p[0].name + '<br/>Cost: ' + p[0].value.toFixed(0); }
    },
    grid: { left: 15, right: 15, top: 20, bottom: 90, containLabel: true },
    xAxis: { type: 'category', data: configs, axisLabel: { color: ink, rotate: 25, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Final Cost', axisLabel: { color: muted }, nameTextStyle: { color: muted } },
    series: [{
      type: 'bar', data: costsMean,
      markLine: { silent: true, lineStyle: { color: rule, type: 'dashed' },
        data: [{ yAxis: costsMean[0], label: { formatter: 'ERFM only baseline', color: muted, fontSize: 10 } }]
      },
      itemStyle: { borderRadius: [4,4,0,0] }
    }]
  });
  window.addEventListener('resize', function() { c1.resize(); });

  // ── Chart 2: Component Contribution ──
  var c2 = echarts.init(document.getElementById('chart-contrib'), null, { renderer: 'svg' });
  c2.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['Cost Reduction', 'AOCC Improvement'], textStyle: { color: muted }, bottom: 0 },
    grid: { left: 15, right: 15, top: 20, bottom: 60, containLabel: true },
    xAxis: { type: 'category', data: ['SA-DGWN\n(A→B)', 'LHH\n(A→C)', 'Full\n(A→D)'],
      axisLabel: { color: ink, fontSize: 11 } },
    yAxis: [
      { type: 'value', name: 'Cost Reduction', axisLabel: { color: muted }, nameTextStyle: { color: muted } },
      { type: 'value', name: 'AOCC Δ', axisLabel: { color: muted }, nameTextStyle: { color: muted } }
    ],
    series: [
      { name: 'Cost Reduction', type: 'bar', data: [1351.9, 1288.0, 1651.1],
        itemStyle: { color: accent, borderRadius: [4,4,0,0] } },
      { name: 'AOCC Improvement', type: 'line', yAxisIndex: 1, data: [-0.0002, -0.0002, 0.0],
        itemStyle: { color: accent2 }, symbolSize: 8, lineStyle: { width: 2 } }
    ]
  });
  window.addEventListener('resize', function() { c2.resize(); });

  // ── Chart 3: Per-Seed Breakdown ──
  var seeds = ['42', '123', '456', '789', '1024'];
  var perSeedCosts = {
    'A': [257539.7, 263099.8, 259592.2, 251689.1, 260326.4],
    'B': [251644.4, 271287.5, 254271.0, 257554.2, 250730.5],
    'C': [254174.7, 264839.4, 264404.3, 255577.7, 246811.2],
    'D': [253705.5, 267730.6, 254271.0, 257554.2, 250730.5]
  };

  var c3 = echarts.init(document.getElementById('chart-seeds'), null, { renderer: 'svg' });
  c3.setOption({
    animation: false,
    color: [accent, accent2, muted, accent + '99'],
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: configs, textStyle: { color: muted }, bottom: 0 },
    grid: { left: 15, right: 15, top: 20, bottom: 60, containLabel: true },
    xAxis: { type: 'category', data: seeds, name: 'Seed', axisLabel: { color: ink },
      nameTextStyle: { color: muted } },
    yAxis: { type: 'value', name: 'Final Cost', axisLabel: { color: muted },
      nameTextStyle: { color: muted }, min: 240000 },
    series: [
      { name: 'A (ERFM only)', type: 'line', data: perSeedCosts['A'], lineStyle: { width: 2 }, symbolSize: 6 },
      { name: 'B (ERFM+SA-DGWN)', type: 'line', data: perSeedCosts['B'], lineStyle: { width: 2, type: 'dashed' }, symbolSize: 6 },
      { name: 'C (ERFM+LHH)', type: 'line', data: perSeedCosts['C'], lineStyle: { width: 2, type: 'dashed' }, symbolSize: 6 },
      { name: 'D (Full)', type: 'line', data: perSeedCosts['D'], lineStyle: { width: 2, type: 'dotted' }, symbolSize: 6 }
    ]
  });
  window.addEventListener('resize', function() { c3.resize(); });

  // ── Chart 4: Pipeline Metrics ──
  var c4 = echarts.init(document.getElementById('chart-pipeline'), null, { renderer: 'svg' });
  c4.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    grid: { left: 15, right: 15, top: 20, bottom: 30, containLabel: true },
    xAxis: { type: 'category', data: ['Before\n(Original)', 'After\n(Improved)'],
      axisLabel: { color: ink } },
    yAxis: [
      { type: 'value', name: '边匹配率 (%)', axisLabel: { color: muted }, max: 100,
        nameTextStyle: { color: muted } },
      { type: 'value', name: '时间方差', axisLabel: { color: muted },
        nameTextStyle: { color: muted } }
    ],
    series: [
      { name: '边匹配率 (%)', type: 'bar', data: [43.2, 73.5],
        itemStyle: { color: accent, borderRadius: [4,4,0,0] } },
      { name: '时间方差 (×1000)', type: 'line', yAxisIndex: 1,
        data: [4.8, 6.5], itemStyle: { color: accent2 }, symbolSize: 8 }
    ]
  });
  window.addEventListener('resize', function() { c4.resize(); });
})();
