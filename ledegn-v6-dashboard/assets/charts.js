(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var succ = '#059669'; var warn = '#D97706'; var fail = '#DC2626';

  // ═══ Chart 1: Sigma Evolution Across Versions ═══
  var c1 = echarts.init(document.getElementById('chart-sigma'), null, { renderer: 'svg' });
  c1.setOption({
    animation: false, color: [accent, accent2],
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['σ > 0.5 Edges', 'σ Mean'], bottom: 0, textStyle: { color: muted } },
    grid: { left: 15, right: 60, top: 20, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: ['v3\n(free flow)', 'v4\n(aligned events)', 'v5\n(high density)', 'v6★\n(dynamic closure)'],
      axisLabel: { color: ink, fontSize: 11 } },
    yAxis: [
      { type: 'value', name: 'σ > 0.5 Count', axisLabel: { color: muted }, nameTextStyle: { color: muted } },
      { type: 'value', name: 'σ Mean', axisLabel: { color: muted }, nameTextStyle: { color: muted },
        min: 0, max: 0.5 }
    ],
    series: [
      { name: 'σ > 0.5 Edges', type: 'bar', data: [3, 3, 3, 78],
        itemStyle: { borderRadius: [4,4,0,0],
          color: function(p) { return p.dataIndex == 3 ? succ : accent; } },
        label: { show: true, position: 'top', color: ink, fontSize: 12, fontWeight: 700 } },
      { name: 'σ Mean', type: 'line', yAxisIndex: 1, data: [0.009, 0.010, 0.267, 0.326],
        itemStyle: { color: accent2 }, symbolSize: 10, symbol: 'diamond',
        label: { show: true, position: 'top', color: accent2, fontSize: 11,
          formatter: function(p) { return p.value.toFixed(3); } } }
    ]
  });
  window.addEventListener('resize', function() { c1.resize(); });

  // ═══ Chart 2: Cost Delta Over Versions ═══
  var c2 = echarts.init(document.getElementById('chart-cost'), null, { renderer: 'svg' });
  c2.setOption({
    animation: false, color: [accent],
    tooltip: { trigger: 'axis', appendToBody: true,
      formatter: function(p) { return p[0].name + '<br/>ΔCost: ' + (p[0].value>0?'+':'') + p[0].value.toFixed(0) + ' (' + (p[0].value/258000*100).toFixed(2) + '%)'; }
    },
    grid: { left: 15, right: 15, top: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category',
      data: ['v3\n(uncontrolled events)', 'v4\n(aligned events)', 'v5\n(high density)', 'v6★\n(dynamic closure)'],
      axisLabel: { color: ink, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Cost Improvement (A→B)', axisLabel: { color: muted },
      nameTextStyle: { color: muted },
      axisLine: { lineStyle: { color: rule } },
      splitLine: { lineStyle: { color: rule } } },
    series: [{
      type: 'bar', data: [-1351.9, -2988.7, 0.0, +75.6],
      itemStyle: {
        borderRadius: [4,4,0,0],
        color: function(p) { return p.value < 0 ? succ : (p.value > 0 ? warn : muted); }
      },
      label: { show: true, position: 'outside',
        formatter: function(p) { return (p.value>0?'+':'') + p.value.toFixed(0); },
        color: ink, fontSize: 12 }
    }]
  });
  window.addEventListener('resize', function() { c2.resize(); });

  // ═══ Chart 3: Per-Seed v6 Results ═══
  var seeds = ['42', '123', '456', '789', '1024'];
  var aData = [274205.8, 265433.7, 268121.5, 262300.7, 266270.9];
  var bData = [271604.7, 277315.4, 260662.5, 263838.6, 262533.2];

  var c3 = echarts.init(document.getElementById('chart-seeds'), null, { renderer: 'svg' });
  c3.setOption({
    animation: false, color: [accent, accent2],
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['A (ERFM only)', 'B (ERFM+SA-DGWN)'], bottom: 0, textStyle: { color: muted } },
    grid: { left: 15, right: 15, top: 20, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: seeds, name: 'Seed', axisLabel: { color: ink },
      nameTextStyle: { color: muted } },
    yAxis: { type: 'value', name: 'Final Cost', axisLabel: { color: muted },
      nameTextStyle: { color: muted } },
    series: [
      { name: 'A (ERFM only)', type: 'bar', data: aData, barGap: '10%',
        itemStyle: { color: accent + '99', borderRadius: [4,4,0,0] },
        label: { show: true, position: 'inside', formatter: function(p) { return (aData[p.dataIndex] - bData[p.dataIndex] > 0 ? '>' : '<'); }, color: ink, fontSize: 10 } },
      { name: 'B (ERFM+SA-DGWN)', type: 'bar', data: bData,
        itemStyle: { color: accent2, borderRadius: [4,4,0,0] } }
    ]
  });
  window.addEventListener('resize', function() { c3.resize(); });

  // ═══ Chart 4: Speed Profile (dynamic closure effect) ═══
  var hours = [];
  for (var h = 0; h < 24; h++) hours.push(h + ':00');
  // Simulated speed profile showing closures
  var speedProfile = [
    0.85,0.83,0.81,0.78,0.75,0.72,0.68,  // 0-6h
    0.55,0.42,0.38,0.58,0.72,0.78,        // 7-12h (7-9 has closure)
    0.80,0.82,0.83,0.81,0.79,             // 13-17h
    0.52,0.38,0.35,0.55,0.70,0.78,0.80    // 18-24h (17-19 has closure)
  ];
  // Mark closure periods
  var marks = [
    { xAxis: '7:00', label: { formatter: 'AM Peak\nClosure', color: fail, fontSize: 11 } },
    { xAxis: '17:00', label: { formatter: 'PM Peak\nClosure', color: fail, fontSize: 11 } }
  ];

  var c4 = echarts.init(document.getElementById('chart-speed'), null, { renderer: 'svg' });
  c4.setOption({
    animation: false, color: [accent],
    tooltip: { trigger: 'axis', appendToBody: true },
    grid: { left: 15, right: 15, top: 20, bottom: 30, containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { color: muted, fontSize: 10, rotate: 45 } },
    yAxis: { type: 'value', name: 'Relative Speed', min: 0, max: 1,
      axisLabel: { color: muted }, nameTextStyle: { color: muted } },
    series: [{
      type: 'line', data: speedProfile, areaStyle: { color: accent + '22' },
      lineStyle: { width: 2 }, symbol: 'none',
      markArea: {
        silent: true,
        data: [
          [{ xAxis: '7:00' }, { xAxis: '9:00' }],
          [{ xAxis: '17:00' }, { xAxis: '19:00' }]
        ],
        itemStyle: { color: fail + '18' },
        label: { show: true, position: 'insideTop', color: fail, fontSize: 11,
          formatter: function(p) { return p.name === 'G1_0' ? 'CLOSED' : 'CLOSED'; } }
      },
      markLine: {
        silent: true, symbol: 'none',
        lineStyle: { color: fail, type: 'dashed', width: 1.5 },
        data: marks
      }
    }]
  });
  window.addEventListener('resize', function() { c4.resize(); });

  // ═══ Chart 5: SA-DGWN Prediction Pipeline ═══
  var c5 = echarts.init(document.getElementById('chart-pipeline'), null, { renderer: 'svg' });
  c5.setOption({
    animation: false,
    color: [accent, accent2, '#059669', '#D97706'],
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['Edge Mapping %', 'σ > 0.5 Edges', 'MSE ×10³', 'SA-DGWN Effect %'], bottom: 0,
      textStyle: { color: muted, fontSize: 10 } },
    grid: { left: 15, right: 60, top: 20, bottom: 60, containLabel: true },
    xAxis: { type: 'category', data: ['v3 (baseline)', 'v4 (aligned)', 'v5 (dense)', 'v6★ (closure)'],
      axisLabel: { color: ink, fontSize: 10, rotate: 20 } },
    yAxis: [
      { type: 'value', name: '% / Count', axisLabel: { color: muted }, nameTextStyle: { color: muted } },
      { type: 'value', name: 'Cost %', axisLabel: { color: muted }, nameTextStyle: { color: muted } }
    ],
    series: [
      { name: 'Edge Mapping %', type: 'line', data: [43.2, 73.5, 73.5, 73.5],
        itemStyle: { color: accent2 }, symbolSize: 8, lineStyle: { width: 2.5 } },
      { name: 'σ > 0.5 Edges', type: 'line', data: [3, 3, 3, 78],
        itemStyle: { color: succ }, symbolSize: 8, lineStyle: { width: 2.5 } },
      { name: 'MSE ×10³', type: 'line', data: [0.276, 0.276, 0.398, 0.399],
        itemStyle: { color: warn }, symbolSize: 8, lineStyle: { width: 2 } },
      { name: 'SA-DGWN Effect %', type: 'line', yAxisIndex: 1,
        data: [-0.5, -1.2, 0.0, 0.03],
        itemStyle: { color: accent }, symbolSize: 10, symbol: 'diamond',
        lineStyle: { width: 3, type: 'dashed' },
        markLine: { silent: true, symbol: 'none',
          lineStyle: { color: 'transparent' },
          label: { formatter: '→ Goal: >0.5%', position: 'start', color: succ, fontSize: 10 },
          data: [{ yAxis: 0.5 }] }
      }
    ]
  });
  window.addEventListener('resize', function() { c5.resize(); });
})();
